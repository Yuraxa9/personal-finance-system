import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.category import Category
from app.models.transaction import TransactionType
from app.models.user import User
from app.schemas.analytics import AnalyticsResponse
from app.schemas.transaction import (
    TransactionCreate,
    TransactionFilter,
    TransactionResponse,
    TransactionUpdate,
)
from app.services import transaction as transaction_service

router = APIRouter(prefix="/transactions", tags=["transactions"])


async def _validate_transaction_data(data: TransactionCreate | TransactionUpdate, user_id: uuid.UUID, db: AsyncSession) -> None:
    if hasattr(data, 'amount') and data.amount is not None and data.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Сумма должна быть больше нуля",
        )

    if hasattr(data, 'date') and data.date is not None:
        max_future = datetime.now(timezone.utc) + timedelta(days=1)
        tx_date = data.date if data.date.tzinfo else data.date.replace(tzinfo=timezone.utc)
        if tx_date > max_future:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Дата не может быть в будущем более чем на 1 день",
            )

    if hasattr(data, 'category_id') and data.category_id is not None:
        result = await db.execute(
            select(Category).where(
                Category.id == data.category_id,
                or_(Category.user_id == user_id, Category.is_default.is_(True)),
            )
        )
        if result.scalar_one_or_none() is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Категория не найдена или не принадлежит пользователю",
            )


@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics(
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await transaction_service.get_analytics(db, current_user.id, date_from, date_to)


@router.get("/", response_model=list[TransactionResponse])
async def list_transactions(
    account_id: uuid.UUID | None = Query(None),
    category_id: uuid.UUID | None = Query(None),
    transaction_type: TransactionType | None = Query(None),
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    filters = TransactionFilter(
        account_id=account_id,
        category_id=category_id,
        transaction_type=transaction_type,
        date_from=date_from,
        date_to=date_to,
    )
    return await transaction_service.get_transactions(db, current_user.id, filters)


@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    data: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _validate_transaction_data(data, current_user.id, db)
    return await transaction_service.create_transaction(db, current_user.id, data)


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    transaction = await transaction_service.get_transaction(db, transaction_id, current_user.id)
    if transaction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return transaction


@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: uuid.UUID,
    data: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _validate_transaction_data(data, current_user.id, db)
    transaction = await transaction_service.update_transaction(
        db, transaction_id, current_user.id, data
    )
    if transaction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return transaction


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    deleted = await transaction_service.delete_transaction(db, transaction_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
