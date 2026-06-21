from typing import Any

from sqlalchemy import select
from sqlalchemy import delete as sql_delete
from sqlalchemy.orm import Session, selectinload

from app.models import Cart, CartItem

def cart_get_by_user(db: Session, user_id: int) -> Cart | None:
    return db.scalar(
        select(Cart)
        .where(Cart.user_id == user_id)
        .options(selectinload(Cart.cart_items).selectinload(CartItem.product))
    )

def create_or_save(db: Session, obj: Any) -> Any:
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def delete(db: Session, obj: Any) -> Any:
    db.delete(obj)
    db.commit()

def cart_create(db: Session, cart: Cart) -> Cart:
    return create_or_save(db, cart)

def cart_item_save(db: Session, cart_item: CartItem) -> CartItem:
    return create_or_save(db, cart_item)

def cart_item_get_by_product(db: Session, cart_id: int, product_id: int) -> CartItem | None:
    return db.scalar(select(CartItem).where(
        CartItem.cart_id == cart_id,
        CartItem.product_id == product_id
    ))

def cart_item_get_by_id(db: Session, cart_id: int, cart_item_id: int) -> CartItem | None:
    return db.scalar(select(CartItem).where(
        CartItem.cart_id == cart_id,
        CartItem.cart_item_id == cart_item_id
    ))

def cart_item_delete(db: Session, cart_item: CartItem) -> None:
    delete(db, cart_item)

def cart_clear(db: Session, cart_id: int) -> None:
    db.execute(sql_delete(CartItem).where(CartItem.cart_id == cart_id))
    db.commit()