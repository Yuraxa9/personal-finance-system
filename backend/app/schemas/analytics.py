import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class PeriodSummary(BaseModel):
    total_income: Decimal
    total_expense: Decimal
    balance: Decimal


class CategorySummary(BaseModel):
    category_id: uuid.UUID | None
    category_name: str
    total_amount: Decimal
    count: int


class AnalyticsResponse(BaseModel):
    period: dict[str, datetime | None]
    summary: PeriodSummary
    by_category: list[CategorySummary]
