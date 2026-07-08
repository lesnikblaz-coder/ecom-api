from sqlalchemy.orm import Session

from app.models import Order, Payment
from app.integrations.mock_payment_gateway import MockPaymentGateway
from app.repositories import payment_repository
from app.enums import Currency
from app.logging_config import logger
from app.integrations.payment_result import PaymentResult

class PaymentService:
    def __init__(self, gateway):
        self.gateway = gateway

def process_payment(db: Session, order: Order) -> PaymentResult:

    gateway = MockPaymentGateway()
    payment_service = PaymentService(gateway)

    # create payment
    payment = Payment(
        order_id=order.order_id,
        amount=order.total_price,
        currency=Currency.USD,
        provider=gateway.provider
    )
    payment = payment_repository.payment_create(db, payment)
    logger.info("Payment created id=%s, amount=%s, currency=%s, created_at=%s",
                payment.payment_id,
                payment.amount,
                payment.currency,
                payment.created_at
                )

    # charge payment
    result: PaymentResult = gateway.charge(payment)

    # update payment
    payment.status = result.status
    payment.provider_payment_id = result.provider_payment_id
    payment = payment_repository.save_and_return(db, payment)
    logger.info("Payment charge id=%s, status=%s, amount=%s, currency=%s, provider=%s, updated_at=%s",
                payment.payment_id,
                payment.status,
                payment.amount,
                payment.currency,
                payment.provider,
                payment.updated_at
                )

    return result