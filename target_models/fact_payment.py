from sqlalchemy import Column, ForeignKey, Integer, Numeric

from .base import TargetBase


class FactPayment(TargetBase):
    __tablename__ = "fact_payment"

    fact_payment_key = Column(Integer, primary_key=True, autoincrement=True)
    payment_id = Column(Integer, nullable=False, unique=True, index=True)
    date_key_paid = Column(
        Integer, ForeignKey("dim_date.date_key"), nullable=False, index=True
    )
    customer_key = Column(
        Integer, ForeignKey("dim_customer.customer_key"), nullable=False, index=True
    )
    store_key = Column(
        Integer, ForeignKey("dim_store.store_key"), nullable=False, index=True
    )
    staff_id = Column(Integer, nullable=False)
    amount = Column(Numeric(5, 2), nullable=False)
