from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Payment

def save_and_return(db: Session, payment: Payment) -> Payment:
    db.commit()
    db.refresh(payment)
    return payment

def payment_create(db: Session, payment: Payment) -> Payment:
    db.add(payment)
    return save_and_return(db, payment)

def payment_get():
    pass

def payment_get_by_provider_id():
    pass

def payment_update():
    pass

def payments_for_order():
    pass