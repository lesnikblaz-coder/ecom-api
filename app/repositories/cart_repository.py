from typing import Any

from sqlalchemy import select
from sqlalchemy import delete as sql_delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Cart, CartItem

async def cart_get_by_user(db: AsyncSession, user_id: int) -> Cart | None:
    stmt = (
        select(Cart).
        where(Cart.user_id == user_id)
        .options(
            selectinload(Cart.cart_items)
            .selectinload(CartItem.product)
        )
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def create_or_save(db: AsyncSession, obj: Any) -> Any:
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj

async def delete(db: AsyncSession, obj: Any) -> Any:
    await db.delete(obj)
    await db.commit()

async def cart_create(db: AsyncSession, cart: Cart) -> Cart:
    return await create_or_save(db, cart)

async def cart_item_save(db: AsyncSession, cart_item: CartItem) -> CartItem:
    return await create_or_save(db, cart_item)

async def cart_item_get_by_product(db: AsyncSession, cart_id: int, product_id: int) -> CartItem | None:
    stmt = (
        select(CartItem)
        .where(
            CartItem.cart_id == cart_id,
            CartItem.product_id == product_id
        )
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def cart_item_get_by_id(db: AsyncSession, cart_id: int, cart_item_id: int) -> CartItem | None:
    stmt = (
        select(CartItem)
        .where(
            CartItem.cart_id == cart_id,
            CartItem.cart_item_id == cart_item_id
        )
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def cart_item_delete(db: AsyncSession, cart_item: CartItem) -> None:
    await delete(db, cart_item)

async def cart_clear(db: AsyncSession, cart_id: int) -> None:
    await db.execute(
        sql_delete(CartItem)
        .where(CartItem.cart_id == cart_id)
    )
    await db.commit()