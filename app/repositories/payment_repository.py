from sqlalchemy import select, Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Payment

async def payment_create(db: AsyncSession, payment: Payment) -> Payment:
    db.add(payment)
    await db.flush()
    await db.refresh(payment)
    return payment

async def payment_update(db: AsyncSession, payment: Payment) -> Payment:
    await db.flush()
    await db.refresh(payment)
    return payment

async def payment_get(db: AsyncSession, payment_id: int) -> Payment | None:
    stmt = (
        select(Payment)
        .where(Payment.payment_id == payment_id)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def payment_get_by_provider_id(db: AsyncSession, provider_payment_id: str) -> Payment | None:
    stmt = (
        select(Payment)
        .where(Payment.provider_payment_id == provider_payment_id)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def payments_for_order(db: AsyncSession, order_id: int) -> Sequence[Payment]:
    stmt = (
        select(Payment)
        .where(Payment.order_id == order_id)
    )
    result = await db.execute(stmt)
    return result.scalars().all()