from collections.abc import Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.repositories import user_repository
from app.exceptions import UserNotFoundError
from app.schemas import UserUpdate
from app.logging_config import logger
from app.database import transaction

async def users_get(db: AsyncSession) -> Sequence[User]:
    return await user_repository.users_get(db)

async def user_get(db: AsyncSession, user_id: int) -> User:
    user = await user_repository.user_get_by_id(db, user_id)
    if not user:
        raise UserNotFoundError("User not found.")
    return user

async def user_update(db: AsyncSession, user_id: int, data: UserUpdate) -> User:
    async with transaction(db):
        user = await user_get(db, user_id)
        logger.info("User %s updated", user_id)
        return await user_repository.user_update(db, user, data)

async def user_delete(db: AsyncSession, user_id: int) -> User:
    async with transaction(db):
        user = await user_get(db, user_id)
        logger.info("User %s deleted", user_id)
        return await user_repository.user_delete(db, user)