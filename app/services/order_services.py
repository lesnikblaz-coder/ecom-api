from sqlalchemy.orm import Session
from collections.abc import Sequence
from decimal import Decimal

from app.models import Order, OrderItem, CartItem
from app.repositories import order_repository, payment_repository
from app.services.cart_services import cart_get
from app.exceptions import EmptyCartError, InsufficientStockError, OrderNotFoundError
from app.enums import OrderStatus, PaymentStatus
from app.database import transaction
from app.logging_config import logger
from app.integrations.payment_result import PaymentResult
from app.services import payment_services

# internal helpers
def _validate_stock_and_calculate_total(items: list[CartItem]) -> Decimal:
    total_price = Decimal("0")
    for item in items:
        if item.quantity > item.product.quantity:
            raise InsufficientStockError(f"Insufficient stock for {item.product.name} (ID: {item.product_id}).")
        total_price += (item.quantity * item.product.price)

    return total_price

def _create_order_items(item: CartItem, order: Order) -> OrderItem:
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
    order = order_repository.order_get_by_id_plus_user(db, order_id, user_id)
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
        total_price = _validate_stock_and_calculate_total(items)

        # create order
        order = Order(user_id=user_id, total_price=total_price, status=OrderStatus.PENDING_PAYMENT, delivery_address=delivery_address)

        # add to session and flush to generate order_id
        order_repository.add(db, order)
        order_repository.flush(db)

        for item in items:
            # create order_item for each item in cart
            order_item = _create_order_items(item, order)

            # add to order_item database
            order_repository.add(db, order_item)

        # with the generated order_id we can create a payment (in my case, we update the stock and clear cart AFTER a payment was successful -
         # in a real app I'd set those products as reserved to prevent selling more items than in stock if 2 or more orders happen to happen simultaneously)
        payment = payment_services.create_payment(db, order)

    payment_result: PaymentResult = payment_services.process_payment(payment)

    with transaction(db):
        payment.status = payment_result.status
        payment.provider_payment_id = payment_result.provider_payment_id

        payment = payment_repository.payment_update(db, payment)
        logger.info("Payment charge id=%s, status=%s, amount=%s, currency=%s, provider=%s, updated_at=%s",
                    payment.payment_id,
                    payment.status,
                    payment.amount,
                    payment.currency,
                    payment.provider,
                    payment.updated_at
                    )

        if payment_result.status == PaymentStatus.SUCCESS:
            for item in items:
                # remove from stock
                item.product.quantity -= item.quantity

                # clear cart
                order_repository.delete_return_only(db, item)

            order.status = OrderStatus.CONFIRMED

    logger.info("Order created id=%s user=%s total=%s, status=%s",
                order.order_id,
                user_id,
                order.total_price,
                order.status
                )
    return order

def cancel(db: Session, order_id: int, user_id: int) -> Order:
    with transaction(db):
        order = order_get_by_user(db, order_id, user_id)
        order.cancel()

        for item in order.order_items:
            item.product.quantity += item.quantity

    logger.info("Cancelled order %s by user %s", order_id, user_id)
    return order

def confirm(db: Session, order_id: int, user_id: int) -> Order:
    with transaction(db):
        order = order_get_by_user(db, order_id, user_id)
        order.confirm()

    logger.info("Confirmed order %s by user %s", order_id, user_id)
    return order

def ship(db: Session, order_id: int, user_id: int) -> Order:
    with transaction(db):
        order = order_get_by_user(db, order_id, user_id)
        order.ship()

    logger.info("Shipped order %s by user %s", order_id, user_id)
    return order

def delivered(db: Session, order_id: int, user_id: int) -> Order:
    with transaction(db):
        order = order_get_by_user(db, order_id, user_id)
        order.delivered()

    logger.info("Delivered order %s by user %s", order_id, user_id)
    return order

def order_delete(db: Session, order_id: int) -> None:
    with transaction(db):
        order = order_repository.order_get_by_id(db, order_id)

        if not order:
            raise OrderNotFoundError("Order not found.")

        logger.info("Order deleted id=%s", order.order_id)
        order_repository.delete_return_only(db, order)