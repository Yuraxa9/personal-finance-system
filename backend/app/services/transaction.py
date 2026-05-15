import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.models.category import Category
from app.models.transaction import Transaction, TransactionType
from app.schemas.analytics import AnalyticsResponse, CategorySummary, PeriodSummary
from app.schemas.transaction import TransactionCreate, TransactionFilter, TransactionUpdate


def _apply_balance(account: Account, transaction_type: TransactionType, amount: Decimal) -> None:
    if transaction_type == TransactionType.income:
        account.balance += amount
    else:
        account.balance -= amount


def _revert_balance(account: Account, transaction_type: TransactionType, amount: Decimal) -> None:
    if transaction_type == TransactionType.income:
        account.balance -= amount
    else:
        account.balance += amount


async def get_transactions(
    db: AsyncSession, user_id: uuid.UUID, filters: TransactionFilter
) -> list[Transaction]:
    conditions = [Transaction.user_id == user_id]
    if filters.account_id:
        conditions.append(Transaction.account_id == filters.account_id)
    if filters.category_id:
        conditions.append(Transaction.category_id == filters.category_id)
    if filters.transaction_type:
        conditions.append(Transaction.transaction_type == filters.transaction_type)
    if filters.date_from:
        conditions.append(Transaction.date >= filters.date_from)
    if filters.date_to:
        conditions.append(Transaction.date <= filters.date_to)

    result = await db.execute(
        select(Transaction).where(and_(*conditions)).order_by(Transaction.date.desc())
    )
    return list(result.scalars().all())


async def get_transaction(
    db: AsyncSession, transaction_id: uuid.UUID, user_id: uuid.UUID
) -> Transaction | None:
    result = await db.execute(
        select(Transaction).where(
            Transaction.id == transaction_id, Transaction.user_id == user_id
        )
    )
    return result.scalar_one_or_none()


async def create_transaction(
    db: AsyncSession, user_id: uuid.UUID, data: TransactionCreate
) -> Transaction:
    account_result = await db.execute(
        select(Account).where(Account.id == data.account_id, Account.user_id == user_id)
    )
    account = account_result.scalar_one_or_none()
    if account is None:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    transaction = Transaction(
        user_id=user_id,
        account_id=data.account_id,
        category_id=data.category_id,
        amount=data.amount,
        transaction_type=data.transaction_type,
        description=data.description,
        date=data.date,
    )
    _apply_balance(account, data.transaction_type, data.amount)

    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)
    return transaction


async def update_transaction(
    db: AsyncSession, transaction_id: uuid.UUID, user_id: uuid.UUID, data: TransactionUpdate
) -> Transaction | None:
    transaction = await get_transaction(db, transaction_id, user_id)
    if transaction is None:
        return None

    if data.amount is not None:
        account_result = await db.execute(
            select(Account).where(Account.id == transaction.account_id)
        )
        account = account_result.scalar_one_or_none()
        if account:
            _revert_balance(account, transaction.transaction_type, transaction.amount)
            _apply_balance(account, transaction.transaction_type, data.amount)

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(transaction, field, value)

    await db.commit()
    await db.refresh(transaction)
    return transaction


async def delete_transaction(
    db: AsyncSession, transaction_id: uuid.UUID, user_id: uuid.UUID
) -> bool:
    transaction = await get_transaction(db, transaction_id, user_id)
    if transaction is None:
        return False

    account_result = await db.execute(
        select(Account).where(Account.id == transaction.account_id)
    )
    account = account_result.scalar_one_or_none()
    if account:
        _revert_balance(account, transaction.transaction_type, transaction.amount)

    await db.delete(transaction)
    await db.commit()
    return True


async def get_analytics(
    db: AsyncSession,
    user_id: uuid.UUID,
    date_from: datetime | None,
    date_to: datetime | None,
) -> AnalyticsResponse:
    conditions = [Transaction.user_id == user_id]
    if date_from:
        conditions.append(Transaction.date >= date_from)
    if date_to:
        conditions.append(Transaction.date <= date_to)

    # totals
    totals_result = await db.execute(
        select(
            Transaction.transaction_type,
            func.sum(Transaction.amount).label("total"),
        )
        .where(and_(*conditions))
        .group_by(Transaction.transaction_type)
    )
    totals = {row.transaction_type: row.total for row in totals_result}
    total_income = totals.get(TransactionType.income, Decimal("0.00")) or Decimal("0.00")
    total_expense = totals.get(TransactionType.expense, Decimal("0.00")) or Decimal("0.00")
    total_transfer = totals.get(TransactionType.transfer, Decimal("0.00")) or Decimal("0.00")

    # by category
    by_category_result = await db.execute(
        select(
            Transaction.category_id,
            Category.name.label("category_name"),
            func.sum(Transaction.amount).label("total_amount"),
            func.count(Transaction.id).label("count"),
        )
        .outerjoin(Category, Transaction.category_id == Category.id)
        .where(and_(*conditions))
        .group_by(Transaction.category_id, Category.name)
    )

    by_category = [
        CategorySummary(
            category_id=row.category_id,
            category_name=row.category_name or "Без категории",
            total_amount=row.total_amount or Decimal("0.00"),
            count=row.count,
        )
        for row in by_category_result
    ]

    return AnalyticsResponse(
        period={"date_from": date_from, "date_to": date_to},
        summary=PeriodSummary(
            total_income=total_income,
            total_expense=total_expense,
            balance=total_income - total_expense - total_transfer,
        ),
        by_category=by_category,
    )
