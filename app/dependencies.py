from app.services.payment_services import PaymentService
from app.integrations.mock_payment_gateway import MockPaymentGateway

def get_payment_service():

    gateway = MockPaymentGateway()

    return PaymentService(gateway)