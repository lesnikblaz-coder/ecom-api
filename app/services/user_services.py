from sqlalchemy.orm import Session

from app.models import User
from app.repositories import user_repository
from app.exceptions import UserNotFoundError
from app.schemas import UserUpdate

def get_user(db: Session, user_id: int) -> User:
    user = user_repository.user_get_by_id(db, user_id)
    if not user:
        raise UserNotFoundError("User not found.")
    return user

def user_update(db: Session, user_id: int, data: UserUpdate) -> User:
    user = get_user(db, user_id)
    return user_repository.user_update(db, user, data)

def user_delete(db: Session, user_id: int) -> User:
    user =  get_user(db, user_id)
    return user_repository.user_delete(db, user)