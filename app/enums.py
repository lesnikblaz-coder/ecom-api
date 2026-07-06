from enum import StrEnum

class UserRole(StrEnum):
    CUSTOMER = "customer"
    STAFF = "staff"
    ADMIN = "admin"

class OrderStatus(StrEnum):
    PENDING_PAYMENT = "pending_payment"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class PaymentStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class Currency(StrEnum):
    USD = "usd"
    EUR = "eur"
    GBP = "gbp"
    CAD = "cad"
    JPY = "jpy"
    NZD = "nzd"