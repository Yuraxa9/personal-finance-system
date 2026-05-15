import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.schemas.account import AccountCreate, AccountUpdate


async def get_accounts(db: AsyncSession, user_id: uuid.UUID) -> list[Account]:
    result = await db.execute(select(Account).where(Account.user_id == user_id))
    return list(result.scalars().all())


async def get_account(
    db: AsyncSession, account_id: uuid.UUID, user_id: uuid.UUID
) -> Account | None:
    result = await db.execute(
        select(Account).where(Account.id == account_id, Account.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def create_account(
    db: AsyncSession, user_id: uuid.UUID, data: AccountCreate
) -> Account:
    account = Account(
        user_id=user_id,
        name=data.name,
        account_type=data.account_type,
        balance=data.balance,
        currency=data.currency,
    )
    db.add(account)
    await db.commit()
    await db.refresh(account)
    return account


async def update_account(
    db: AsyncSession, account_id: uuid.UUID, user_id: uuid.UUID, data: AccountUpdate
) -> Account | None:
    account = await get_account(db, account_id, user_id)
    if account is None:
        return None
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(account, field, value)
    await db.commit()
    await db.refresh(account)
    return account


async def delete_account(
    db: AsyncSession, account_id: uuid.UUID, user_id: uuid.UUID
) -> bool:
    account = await get_account(db, account_id, user_id)
    if account is None:
        return False
    await db.delete(account)
    await db.commit()
    return True
