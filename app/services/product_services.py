from sqlalchemy.ext.asyncio import AsyncSession
from math import ceil
from decimal import Decimal

from app.repositories import product_repository, category_repository
from app.schemas import ProductUpdate, ProductFilters, PaginatedProductResponse, ProductResponse
from app.models import Product
from app.exceptions import ProductNotFoundError, CategoryNotFoundError
from app.logging_config import logger
from app.database import transaction

async def products_get(db: AsyncSession, filters: ProductFilters) -> PaginatedProductResponse:
    limit = filters.limit
    offset = (filters.page - 1) * limit

    products, total = await product_repository.products_get(db, filters, offset, limit)

    pages = ceil(total/limit) or 1

    has_next = (filters.page < pages)
    has_previous = (filters.page > 1)

    return PaginatedProductResponse(
        products=[ProductResponse.model_validate(product) for product in products],
        page=filters.page,
        limit=limit,
        total=total,
        pages=pages,
        has_next=has_next,
        has_previous=has_previous
    )

async def product_get(db: AsyncSession, product_id: int) -> Product:
    product = await product_repository.product_get(db, product_id)
    if not product:
        raise ProductNotFoundError("Product not found.")
    return product

async def product_create(db: AsyncSession, category_id: int, name: str, description: str, price: Decimal, quantity: int) -> Product:
    async with transaction(db):
        if not await category_repository.category_get(db, category_id):
            raise CategoryNotFoundError("Category not found.")

        product = Product(category_id=category_id, name=name, description=description, price=price, quantity=quantity)
        product = await product_repository.product_create(db, product)

        logger.info("Product created id=%s name=%s", product.product_id, product.name)
        return product

async def product_update(db: AsyncSession, product_id: int, data: ProductUpdate) -> Product:
    async with transaction(db):
        product = await product_get(db, product_id)
        logger.info("Product updated id=%s", product_id)
        return await product_repository.product_update(db, product, data)

async def product_delete(db: AsyncSession, product_id: int) -> None:
    async with transaction(db):
        product = await product_get(db, product_id)
        await product_repository.product_delete(db, product)
        logger.info("Product %s deleted", product_id)