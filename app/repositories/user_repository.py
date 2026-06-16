from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User
from app.schemas import UserUpdate

def user_get_by_id(db: Session, user_id: int) -> User | None:
    return db.scalar(select(User).where(User.user_id == user_id))

def user_get_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))

def user_create(db: Session, user: User) -> User:
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def user_update(db: Session, user: User, data: UserUpdate) -> User:
    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user

def user_delete(db: Session, user: User) -> User:
    db.delete(user)
    db.commit()
    return user