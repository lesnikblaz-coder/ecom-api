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

class SuccessPaymentGateway(PaymentGateway):
    @property
    def provider(self) -> str:
        return "mock"

    def charge(self, payment: Payment) -> PaymentResult:
        return PaymentResult(
            status=PaymentStatus.SUCCESS,
            provider_payment_id="mock_success_12345"
        )

class FailPaymentGateway(PaymentGateway):
    @property
    def provider(self) -> str:
        return "mock"

    def charge(self, payment: Payment) -> PaymentResult:
        return PaymentResult(
            status=PaymentStatus.FAILED,
            provider_payment_id="mock_fail_54321"
        )