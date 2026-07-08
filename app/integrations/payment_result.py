from dataclasses import dataclass

from app.enums import PaymentStatus

@dataclass
class PaymentResult:
    status: PaymentStatus
    provider_payment_id: str