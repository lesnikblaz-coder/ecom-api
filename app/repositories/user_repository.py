from collections.abc import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.schemas import UserUpdate

async def user_get_by_id(db: AsyncSession, user_id: int) -> User | None:
    result = await db.execute(
        select(User)
        .where(User.user_id == user_id)
    )
    return result.scalar_one_or_none()

async def user_get_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(
        select(User)
        .where(User.email == email)
    )
    return result.scalar_one_or_none()

async def user_create(db: AsyncSession, user: User) -> User:
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user

async def users_get(db: AsyncSession) -> Sequence[User]:
    result = await db.execute(select(User))
    return result.scalars().all()

async def user_update(db: AsyncSession, user: User, data: UserUpdate) -> User:
    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(user, field, value)

    await db.flush()
    await db.refresh(user)
    return user

async def user_delete(db: AsyncSession, user: User) -> User:
    await db.delete(user)
    await db.flush()
    return user