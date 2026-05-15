import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
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
