from random import random

from app.integrations.payment_gateway import PaymentGateway
from app.models import Payment
from app.enums import PaymentStatus
from app.integrations.payment_result import PaymentResult

class MockPaymentGateway(PaymentGateway):
    @property
    def provider(self) -> str:
        return "mock"

    def charge(self, payment: Payment) -> PaymentResult:
        if random() < 0.7:
            return PaymentResult(
                status=PaymentStatus.SUCCESS,
                provider_payment_id="mock_123456"
            )
        return PaymentResult(
            status=PaymentStatus.FAILED,
            provider_payment_id="mock_654321"
        )

    # just for testing
    @staticmethod
    def charge_success(payment: Payment) -> PaymentResult:
        return PaymentResult(
            status=PaymentStatus.SUCCESS,
            provider_payment_id="mock_123456"
        )

    # just for testing
    @staticmethod
    def charge_failure(payment: Payment) -> PaymentResult:
        return PaymentResult(
            status=PaymentStatus.FAILED,
            provider_payment_id="mock_654321"
        )