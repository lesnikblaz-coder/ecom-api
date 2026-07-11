from sqlalchemy import Sequence
from sqlalchemy.orm import Session

from app.models import Order, Payment, Cart
from app.repositories import payment_repository, order_repository
from app.enums import Currency, OrderStatus, PaymentStatus
from app.logging_config import logger
from app.integrations.payment_result import PaymentResult
from app.exceptions import InvalidOrderStateError, OrderNotFoundError
from app.database import transaction
from app.integrations.payment_gateway import PaymentGateway
from app.services.cart_services import cart_get

def create_payment(db: Session, order: Order, gateway_provider: str) -> Payment:
    # create payment
    payment = Payment(
        order_id=order.order_id,
        amount=order.total_price,
        currency=Currency.USD,
        provider=gateway_provider
    )
    payment = payment_repository.payment_create(db, payment)
    logger.info("Payment created id=%s, amount=%s, currency=%s, created_at=%s",
                payment.payment_id,
                payment.amount,
                payment.currency,
                payment.created_at
                )

    return payment

def process_payment(payment: Payment, gateway: PaymentGateway) -> PaymentResult:
    return gateway.charge(payment)

def payments_for_order(db: Session, order_id: int) -> Sequence[Payment]:
    return payment_repository.payments_for_order(db, order_id)

def payment_retry(db: Session, order_id: int, user_id: int, gateway: PaymentGateway) -> Payment:
    with transaction(db):
        order = order_repository.order_get_by_id_plus_user(db, order_id, user_id)
        if not order:
            raise OrderNotFoundError("Order not found.")

        if order.status != OrderStatus.PENDING_PAYMENT:
            raise InvalidOrderStateError("Invalid order state.")

        payment = create_payment(db, order, gateway.provider)

    payment_result = process_payment(payment, gateway)

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

        cart = cart_get(db, user_id)
        items = cart.cart_items

        if payment_result.status == PaymentStatus.SUCCESS:
            for item in items:
                # remove from stock
                item.product.quantity -= item.quantity

                # clear cart
                order_repository.delete_return_only(db, item)
            order.status = OrderStatus.CONFIRMED

    return payment