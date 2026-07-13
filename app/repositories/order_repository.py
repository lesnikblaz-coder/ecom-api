from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from collections.abc import Sequence
from typing import Any

from app.models import Order, OrderItem

async def orders_get(db: AsyncSession, user_id: int) -> Sequence[Order]:
    stmt = (
        select(Order)
        .where(Order.user_id == user_id)
        .options(
            selectinload(Order.order_items)
            .selectinload(OrderItem.product)
        )
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def order_get_by_id_plus_user(db: AsyncSession, order_id: int, user_id: int) -> Order | None:
    stmt = (
        select(Order)
        .where(
            Order.order_id == order_id,
            Order.user_id == user_id
        )
        .options(
            selectinload(Order.order_items)
            .selectinload(OrderItem.product)
        )
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def order_get_by_id(db: AsyncSession, order_id: int) -> Order | None:
    stmt = (
        select(Order)
        .where(Order.order_id == order_id)
        .options(
            selectinload(Order.order_items)
            .selectinload(OrderItem.product)
        )
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def flush(db: AsyncSession) -> None:
    await db.flush()

def add(db: AsyncSession, obj: Any) -> Any:
    db.add(obj)
    return obj

async def delete_return_only(db: AsyncSession, obj: Any) -> Any:
    await db.delete(obj)
    return obj