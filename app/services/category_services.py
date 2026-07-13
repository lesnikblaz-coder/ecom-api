from sqlalchemy.ext.asyncio import AsyncSession
from collections.abc import Sequence

from app.models import Category
from app.repositories import category_repository
from app.exceptions import CategoryNotFoundError, CategoryAlreadyExistsError
from app.schemas import CategoryUpdate
from app.logging_config import logger

async def categories_get(db: AsyncSession) -> Sequence[Category]:
    return await category_repository.categories_get(db)

async def category_get(db: AsyncSession, category_id: int) -> Category:
    category = await category_repository.category_get(db, category_id)
    if not category:
        raise CategoryNotFoundError("Category not found.")
    return category

async def category_create(db: AsyncSession, name: str) -> Category:
    if await category_repository.category_get_by_name(db, name):
        raise CategoryAlreadyExistsError("Category already exists.")

    category = Category(name=name)
    category = await category_repository.category_create(db, category)

    logger.info("Category %s created", category.category_id)
    return category

async def category_update(db: AsyncSession, category_id: int, data: CategoryUpdate) -> Category:
    category = await category_get(db, category_id)
    logger.info("Category %s updated", category.category_id)
    return await category_repository.category_update(db, category, data)

async def category_delete(db: AsyncSession, category_id: int) -> None:
    category = await category_get(db, category_id)
    await category_repository.category_delete(db, category)
    logger.info("Category %s deleted", category.category_id)