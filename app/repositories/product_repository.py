from sqlalchemy import select
from sqlalchemy.orm import Session
from collections.abc import Sequence

from app.models import Product
from app.schemas import ProductUpdate

def products_get(db: Session) -> Sequence[Product]:
    return db.scalars(select(Product)).all()

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

def product_delete(db: Session, product: Product) -> Product:
    db.delete(product)
    db.commit()
    return product