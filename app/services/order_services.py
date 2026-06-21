from sqlalchemy.orm import Session
from collections.abc import Sequence
from decimal import Decimal

from app.models import Order, OrderItem, CartItem
from app.repositories import order_repository
from app.services.cart_services import cart_get
from app.exceptions import EmptyCartError, InsufficientStockError, OrderNotFoundError
from app.enums import OrderStatus
from app.database import transaction

# helpers
def validate_stock_return_total(items: list[CartItem]) -> Decimal:
    total_price = Decimal("0")
    for item in items:
        if item.quantity > item.product.quantity:
            raise InsufficientStockError(f"Insufficient stock for {item.product.name} (ID: {item.product_id}).")
        total_price += (item.quantity * item.product.price)
    return total_price

def create_order_items(item: CartItem, order: Order) -> OrderItem:
    return OrderItem(
        order_id=order.order_id,
        product_id=item.product_id,
        quantity=item.quantity,
        unit_price=item.product.price
    )


# business
def orders_get_by_user(db: Session, user_id: int) -> Sequence[Order]:
    return order_repository.orders_get(db, user_id)

def order_get_by_user(db: Session, order_id: int, user_id: int) -> Order:
    order = order_repository.order_get_by_id(db, order_id, user_id)
    if not order:
        raise OrderNotFoundError("Order not found.")
    return order

def checkout(db: Session, user_id: int, delivery_address: str) -> Order:
    with transaction(db):
        cart = cart_get(db, user_id)
        items = cart.cart_items
        if not items:
            raise EmptyCartError("Cart is empty.")

        # validate stock + append to total_price
        total_price = validate_stock_return_total(items)

        # create order
        order = Order(user_id=user_id, total_price=total_price, status=OrderStatus.PENDING, delivery_address=delivery_address)

        # add to session and flush to generate order_id
        order_repository.add(db, order)
        order_repository.flush(db)

        for item in items:
            # create order_item for each item in cart
            order_item = create_order_items(item, order)

            # add to order_item database
            order_repository.add(db, order_item)

            # remove from stock
            item.product.quantity -= item.quantity

            # clear cart
            order_repository.delete_return_only(db, item)

    return order

def cancel(db: Session, order_id: int, user_id: int) -> Order:
    with transaction(db):
        order = order_get_by_user(db, order_id, user_id)
        order.cancel()

        for item in order.order_items:
            item.product.quantity += item.quantity

    return order

def confirm(db: Session, order_id: int, user_id: int) -> Order:
    with transaction(db):
        order = order_get_by_user(db, order_id, user_id)
        order.confirm()
    return order

def ship(db: Session, order_id: int, user_id: int) -> Order:
    with transaction(db):
        order = order_get_by_user(db, order_id, user_id)
        order.ship()
    return order

def delivered(db: Session, order_id: int, user_id: int) -> Order:
    with transaction(db):
        order = order_get_by_user(db, order_id, user_id)
        order.delivered()
    return order