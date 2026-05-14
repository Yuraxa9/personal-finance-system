import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, Enum, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CategoryType(str, enum.Enum):
    income = "income"
    expense = "expense"


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category_type: Mapped[CategoryType] = mapped_column(
        Enum(CategoryType), nullable=False
    )
    color: Mapped[str] = mapped_column(String(7), nullable=False)
    icon: Mapped[str] = mapped_column(String(50), nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    user: Mapped["User | None"] = relationship(back_populates="categories")
    transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="category"
    )
