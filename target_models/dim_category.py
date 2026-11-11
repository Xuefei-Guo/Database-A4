from sqlalchemy import Column, DateTime, Integer, String

from .base import TargetBase


class DimCategory(TargetBase):
    __tablename__ = "dim_category"

    category_key = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, nullable=False, unique=True, index=True)
    name = Column(String(25), nullable=False)
    last_update = Column(DateTime, nullable=False)
