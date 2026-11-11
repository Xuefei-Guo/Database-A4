from sqlalchemy import Column, DateTime, Integer, String

from .base import TargetBase


class DimCustomer(TargetBase):
    __tablename__ = "dim_customer"

    customer_key = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, nullable=False, unique=True, index=True)
    first_name = Column(String(45), nullable=False)
    last_name = Column(String(45), nullable=False)
    active = Column(Integer, nullable=False)
    city = Column(String(50), nullable=False)
    country = Column(String(50), nullable=False)
    last_update = Column(DateTime)
