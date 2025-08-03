from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from .base import Base

class Payment(Base):
    __tablename__ = 'payments'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    amount = Column(Integer) 
    status = Column(Boolean, default=False)  # pending/paid/canceled
    payment_id = Column(String, index=True)  # ID платежа в системе
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __init__(self, user_id: int, amount: int, payment_id: str):
        self.user_id = user_id
        self.amount = amount
        self.payment_id = payment_id
