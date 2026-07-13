from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from collections.abc import Sequence

from app import schemas

from app.models import Category

async def categories_get(db: AsyncSession) -> Sequence[Category]:
    stmt = select(Category)
    result = await db.execute(stmt)
    return result.scalars().all()

async def category_get(db: AsyncSession, category_id: int) -> Category | None:
    stmt = (
        select(Category)
        .where(Category.category_id == category_id)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def category_get_by_name(db: AsyncSession, name: str) -> Category | None:
    stmt = (
        select(Category)
        .where(Category.name == name)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def category_create(db: AsyncSession, category: Category) -> Category:
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category

async def category_update(db: AsyncSession, category: Category, data: schemas.CategoryUpdate) -> Category:
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)

    await db.commit()
    await db.refresh(category)
    return category

async def category_delete(db: AsyncSession, category: Category) -> None:
    await db.delete(category)
    await db.commit()