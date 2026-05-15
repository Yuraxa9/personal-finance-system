import uuid

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


async def get_categories(db: AsyncSession, user_id: uuid.UUID) -> list[Category]:
    result = await db.execute(
        select(Category).where(
            or_(Category.user_id == user_id, Category.is_default.is_(True))
        )
    )
    return list(result.scalars().all())


async def get_category(
    db: AsyncSession, category_id: uuid.UUID, user_id: uuid.UUID
) -> Category | None:
    result = await db.execute(
        select(Category).where(
            Category.id == category_id,
            or_(Category.user_id == user_id, Category.is_default.is_(True)),
        )
    )
    return result.scalar_one_or_none()


async def create_category(
    db: AsyncSession, user_id: uuid.UUID, data: CategoryCreate
) -> Category:
    category = Category(
        user_id=user_id,
        name=data.name,
        category_type=data.category_type,
        color=data.color,
        icon=data.icon,
    )
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


async def update_category(
    db: AsyncSession, category_id: uuid.UUID, user_id: uuid.UUID, data: CategoryUpdate
) -> Category | None:
    result = await db.execute(
        select(Category).where(
            Category.id == category_id, Category.user_id == user_id
        )
    )
    category = result.scalar_one_or_none()
    if category is None:
        return None
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(category, field, value)
    await db.commit()
    await db.refresh(category)
    return category


async def delete_category(
    db: AsyncSession, category_id: uuid.UUID, user_id: uuid.UUID
) -> bool:
    result = await db.execute(
        select(Category).where(
            Category.id == category_id, Category.user_id == user_id
        )
    )
    category = result.scalar_one_or_none()
    if category is None:
        return False
    await db.delete(category)
    await db.commit()
    return True
