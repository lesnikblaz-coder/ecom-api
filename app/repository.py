from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User

def user_get_by_id(db: Session, user_id: int) -> User | None:
    return db.scalar(select(User).where(User.user_id == user_id))

def user_get_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))

def user_create(db: Session, user: User) -> User:
    db.add(user)
    db.commit()
    db.refresh(user)
    return user