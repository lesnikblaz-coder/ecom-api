from sqlalchemy import select
from sqlalchemy.orm import Session
from collections.abc import Sequence

from app import schemas

from app.models import Category

def categories_get(db: Session) -> Sequence[Category]:
    return db.scalars(select(Category)).all()

def category_get(db: Session, category_id: int) -> Category | None:
    return db.scalar(select(Category).where(Category.category_id == category_id))

def category_get_by_name(db: Session, name: str) -> Category | None:
    return db.scalar(select(Category).where(Category.name == name))

def category_create(db: Session, category: Category) -> Category:
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

def category_update(db: Session, category: Category, data: schemas.CategoryUpdate) -> Category:
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)

    db.commit()
    db.refresh(category)
    return category

def category_delete(db: Session, category: Category) -> None:
    db.delete(category)
    db.commit()