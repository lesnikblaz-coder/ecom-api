from sqlalchemy.orm import Session
from collections.abc import Sequence
from decimal import Decimal

from app.models import Order, OrderItem
from app.repositories import order_repository
from app.services.cart_services import cart_get
from app.exceptions import EmptyCartError, InsufficientStockError, OrderNotFoundError, InvalidOrderStateError
from app.enums import OrderStatus

def orders_get_by_user(db: Session, user_id: int) -> Sequence[Order]:
    return order_repository.orders_get(db, user_id)

def order_get_by_user(db: Session, order_id: int, user_id: int) -> Order:
    order = order_repository.order_get_by_id(db, order_id, user_id)
    if not order:
        raise OrderNotFoundError("Order not found.")
    return order

def checkout(db: Session, user_id: int, delivery_address: str):
    try:
        cart = cart_get(db, user_id)
        items = cart.cart_items
        if not items:
            raise EmptyCartError("Cart is empty.")

        # validate stock + append to total_price
        total_price = Decimal("0")
        for item in items:
            if item.quantity > item.product.quantity:
                raise InsufficientStockError(f"Insufficient stock for {item.product.name} (ID: {item.product_id}.")
            else:
                total_price += (item.quantity * item.product.price)

        order = Order(user_id=user_id, total_price=total_price, status=OrderStatus.PENDING, delivery_address=delivery_address)
        # add to database and flush to get id
        order = order_repository.save(db=db, obj=order, commit=False, flush=True)

        for item in items:
            order_item = OrderItem(
                order_id=order.order_id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.product.price
            )
            # add to order_item database
            order_repository.save(db=db, obj=order_item, commit=False, flush=False)

            # remove from stock and save
            item.product.quantity -= item.quantity
            order_repository.save(db=db, obj=item)

            # clear cart
            order_repository.delete_return_only(db=db, obj=item)


        # commit all changes, return
        order = order_repository.save(db=db, obj=order, commit=True)
        return order

    except Exception:
        order_repository.rollback(db)
        raise


def cancel(db: Session, order_id: int, user_id: int) -> Order:
    # statuses: PENDING -> CONFIRMED → SHIPPED → DELIVERED
    # PENDING -> CANCELLABLE (stock restored)
    # CONFIRMED -> CANCELLABLE (stock restored)
    # SHIPPED, DELIVERED -> UNCANCELLABLE

    try:
        order = order_get_by_user(db, order_id, user_id)

        if order.status in (OrderStatus.SHIPPED, OrderStatus.DELIVERED, OrderStatus.CANCELLED):
            raise InvalidOrderStateError("Order in uncancellable state.")

        order.status = OrderStatus.CANCELLED

        for item in order.order_items:
            item.product.quantity += item.quantity
            # save each product quantity
            order_repository.save(db=db, obj=item)

        # commit all saves to the database, rollback if any fail
        order = order_repository.save(db=db, obj=order, commit=True)
        return order

    except Exception:
        order_repository.rollback(db)
        raise