import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.models.transaction import TransactionType


class TransactionCreate(BaseModel):
    account_id: uuid.UUID
    category_id: uuid.UUID | None = None
    amount: Decimal
    transaction_type: TransactionType
    description: str | None = None
    date: datetime


class TransactionUpdate(BaseModel):
    category_id: uuid.UUID | None = None
    amount: Decimal | None = None
    description: str | None = None
    date: datetime | None = None


class TransactionResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    account_id: uuid.UUID
    category_id: uuid.UUID | None
    amount: Decimal
    transaction_type: TransactionType
    description: str | None
    date: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class TransactionFilter(BaseModel):
    account_id: uuid.UUID | None = None
    category_id: uuid.UUID | None = None
    transaction_type: TransactionType | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
