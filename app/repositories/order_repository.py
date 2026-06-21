from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from collections.abc import Sequence
from typing import Any

from app.models import Order, OrderItem

def orders_get(db: Session, user_id: int) -> Sequence[Order]:
    return db.scalars(select(Order)
                      .where(Order.user_id == user_id)
                      .options(selectinload(Order.order_items).selectinload(OrderItem.product))
                      ).all()

def order_get_by_id(db: Session, order_id: int, user_id: int) -> Order | None:
    return db.scalar(select(Order)
                     .where(Order.order_id == order_id, Order.user_id == user_id)
                     .options(selectinload(Order.order_items).selectinload(OrderItem.product))
                     )

def flush(db: Session) -> None:
    db.flush()

def add(db: Session, obj: Any) -> Any:
    db.add(obj)
    return obj

def delete_return_only(db: Session, obj: Any) -> Any:
    db.delete(obj)
    return obj