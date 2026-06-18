from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Cart, CartItem

def cart_get_by_user(db: Session, user_id: int) -> Cart | None:
    return db.scalar(select(Cart).where(Cart.user_id == user_id))

def cart_create(db: Session, cart: Cart) -> Cart:
    db.add(cart)
    db.commit()
    db.refresh(cart)
    return cart

def cart_item_save(db: Session, cart_item: CartItem) -> CartItem:
    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)
    return cart_item

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
    db.delete(cart_item)
    db.commit()

def cart_clear():
    pass