from sqlalchemy.orm import Session
from collections.abc import Sequence
from decimal import Decimal

from app.repositories import product_repository, category_repository
from app.schemas import ProductUpdate
from app.models import Product
from app.exceptions import ProductNotFoundError, CategoryNotFoundError

def products_get(db: Session) -> Sequence[Product]:
    return product_repository.products_get(db)

def product_get(db: Session, product_id: int) -> Product:
    product = product_repository.product_get(db, product_id)
    if not product:
        raise ProductNotFoundError("Product not found.")
    return product

def product_create(db: Session, category_id: int, name: str, description: str, price: Decimal, quantity: int) -> Product:
    if not category_repository.category_get(db, category_id):
        raise CategoryNotFoundError("Category not found.")

    product = Product(category_id=category_id, name=name, description=description, price=price, quantity=quantity)
    return product_repository.product_create(db, product)

def product_update(db: Session, product_id: int, data: ProductUpdate) -> Product:
    product = product_get(db, product_id)
    return product_repository.product_update(db, product, data)

def product_delete(db: Session, product_id: int) -> None:
    product = product_get(db, product_id)
    product_repository.product_delete(db, product)