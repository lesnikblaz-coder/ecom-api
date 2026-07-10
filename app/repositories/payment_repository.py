from sqlalchemy import select, Sequence
from sqlalchemy.orm import Session

from app.models import Payment

def payment_create(db: Session, payment: Payment) -> Payment:
    db.add(payment)
    db.flush()
    db.refresh(payment)
    return payment

def payment_update(db: Session, payment: Payment) -> Payment:
    db.flush()
    db.refresh(payment)
    return payment

def payment_get(db: Session, payment_id: int) -> Payment | None:
    return db.scalar(select(Payment).where(Payment.payment_id == payment_id))

def payment_get_by_provider_id(db: Session, provider_payment_id: str) -> Payment | None:
    return db.scalar(select(Payment).where(Payment.provider_payment_id == provider_payment_id))

def payments_for_order(db: Session, order_id: int) -> Sequence[Payment]:
    return db.scalars(select(Payment).where(Payment.order_id == order_id)).all()