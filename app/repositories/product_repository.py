from typing import cast
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from collections.abc import Sequence

from app.models import Product
from app.schemas import ProductUpdate, ProductFilters

def products_get(db: Session, filters: ProductFilters, offset: int, limit: int) -> tuple[Sequence[Product], int]:
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

    if filters.in_stock == False:
        query = query.where(Product.quantity == 0)

    count_query = select(func.count()).select_from(query.subquery())
    total = cast(int, db.scalar(count_query))

    query = query.offset(offset)
    query = query.limit(limit)

    products = db.scalars(query).all()

    return products, total

def product_get(db: Session, product_id: int) -> Product | None:
    return db.scalar(select(Product).where(Product.product_id == product_id))

def product_create(db: Session, product: Product) -> Product:
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

def product_update(db: Session, product: Product, data: ProductUpdate) -> Product:
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product

def product_delete(db: Session, product: Product) -> None:
    db.delete(product)
    db.commit()