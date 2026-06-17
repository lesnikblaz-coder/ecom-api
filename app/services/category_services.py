from sqlalchemy.orm import Session
from collections.abc import Sequence

from app.models import Category
from app.repositories import category_repository
from app.exceptions import CategoryNotFoundError, CategoryAlreadyExistsError
from app.schemas import CategoryUpdate

def categories_get(db: Session) -> Sequence[Category]:
    return category_repository.categories_get(db)

def category_get(db: Session, category_id: int) -> Category:
    category = category_repository.category_get(db, category_id)
    if not category:
        raise CategoryNotFoundError("Category not found.")
    return category

def category_create(db: Session, name: str) -> Category:
    if category_repository.category_get_by_name(db, name):
        raise CategoryAlreadyExistsError("Category already exists.")
    category = Category(name=name)
    return category_repository.category_create(db, category)

def category_update(db: Session, category_id: int, data: CategoryUpdate) -> Category:
    category = category_get(db, category_id)
    return category_repository.category_update(db, category, data)

def category_delete(db: Session, category_id: int) -> None:
    category = category_get(db, category_id)
    category_repository.category_delete(db, category)