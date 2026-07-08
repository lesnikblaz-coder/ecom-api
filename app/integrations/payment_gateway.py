from abc import ABC, abstractmethod

from app.models import Payment
from app.integrations.payment_result import PaymentResult

class PaymentGateway(ABC):

    @abstractmethod
    def charge(self, payment: Payment) -> PaymentResult:
        pass