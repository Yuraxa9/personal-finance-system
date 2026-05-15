import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.category import CategoryType


class CategoryCreate(BaseModel):
    name: str
    category_type: CategoryType
    color: str
    icon: str


class CategoryUpdate(BaseModel):
    name: str | None = None
    color: str | None = None
    icon: str | None = None


class CategoryResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID | None
    name: str
    category_type: CategoryType
    color: str
    icon: str
    is_default: bool
    created_at: datetime

    model_config = {"from_attributes": True}
