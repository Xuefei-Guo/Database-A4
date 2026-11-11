from sqlalchemy import Column, DateTime, Integer, String

from .base import TargetBase


class DimStore(TargetBase):
    __tablename__ = "dim_store"

    store_key = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(Integer, nullable=False, unique=True, index=True)
    city = Column(String(50), nullable=False)
    country = Column(String(50), nullable=False)
    last_update = Column(DateTime, nullable=False)
