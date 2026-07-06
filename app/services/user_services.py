from collections.abc import Sequence
from sqlalchemy.orm import Session

from app.models import User
from app.repositories import user_repository
from app.exceptions import UserNotFoundError
from app.schemas import UserUpdate
from app.logging_config import logger

def users_get(db: Session) -> Sequence[User]:
    return user_repository.users_get(db)

def user_get(db: Session, user_id: int) -> User:
    user = user_repository.user_get_by_id(db, user_id)
    if not user:
        raise UserNotFoundError("User not found.")
    return user

def user_update(db: Session, user_id: int, data: UserUpdate) -> User:
    user = user_get(db, user_id)
    logger.info("User %s updated", user_id)
    return user_repository.user_update(db, user, data)

def user_delete(db: Session, user_id: int) -> User:
    user =  user_get(db, user_id)
    logger.info("User %s deleted", user_id)
    return user_repository.user_delete(db, user)