from database.models import Payment
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

class PaymentRepository:

    async def get_payment(self, payment_id, session: AsyncSession):
        result = await session.execute(select(Payment).where(Payment.payment_id == payment_id))
        return result.scalar_one_or_none()
    
    async def get_payments(self, session: AsyncSession):
        result = await session.execute(select(Payment))
        return result.scalars().all()
    
    async def update_payment_status(self, payment_id, session: AsyncSession):
        result = await session.execute(select(Payment)
            .where(Payment.payment_id == payment_id, Payment.status == False)
        )
        payment = result.scalar_one_or_none()
        payment.status = True
        await session.commit()
    
    async def create_payment(self, payment, session: AsyncSession):
        session.add(payment)
        await session.commit()