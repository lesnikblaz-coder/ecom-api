from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from collections.abc import Sequence

from app.models import Product
from app.schemas import ProductUpdate, ProductFilters

async def products_get(db: AsyncSession, filters: ProductFilters, offset: int, limit: int) -> tuple[Sequence[Product], int]:
    query = select(Product)

    if filters.category:
        query = query.where(Product.category.ilike(f"%{filters.category}%"))

    if filters.min_price is not None:
        query = query.where(Product.price >= filters.min_price)

    if filters.max_price is not None:
        query = query.where(Product.price <= filters.max_price)

    if filters.search:
        query = query.where(Product.name.ilike(f"%{filters.search}%"))

    if filters.in_stock:
        query = query.where(Product.quantity >= 1)

    if filters.in_stock is False:
        query = query.where(Product.quantity == 0)

    count_query = select(func.count()).select_from(query.subquery())
    result_total = await db.execute(count_query)
    total = result_total.scalar_one()

    query = query.offset(offset)
    query = query.limit(limit)

    result = await db.execute(query)
    products = result.scalars().all()

    return products, total

async def product_get(db: AsyncSession, product_id: int) -> Product | None:
    result = await db.execute(
        select(Product)
        .where(Product.product_id == product_id)
    )
    return result.scalar_one_or_none()

async def product_create(db: AsyncSession, product: Product) -> Product:
    db.add(product)
    await db.flush()
    await db.refresh(product)
    return product

async def product_update(db: AsyncSession, product: Product, data: ProductUpdate) -> Product:
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    await db.flush()
    await db.refresh(product)
    return product

async def product_delete(db: AsyncSession, product: Product) -> None:
    await db.delete(product)
    await db.flush()