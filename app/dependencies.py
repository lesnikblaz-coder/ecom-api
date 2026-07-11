from app.integrations.payment_gateway import PaymentGateway
from app.integrations.mock_payment_gateway import (
    MockPaymentGateway,
    SuccessPaymentGateway,
    FailPaymentGateway
)

def get_payment_gateway() -> PaymentGateway:
    return SuccessPaymentGateway()