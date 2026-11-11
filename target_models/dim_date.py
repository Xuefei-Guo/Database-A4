from sqlalchemy import Column, Date, Integer

from .base import TargetBase


class DimDate(TargetBase):
    __tablename__ = "dim_date"

    date_key = Column(Integer, primary_key=True, autoincrement=False)
    date = Column(Date, nullable=False, unique=True)
    year = Column(Integer, nullable=False)
    quarter = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    day_of_month = Column(Integer, nullable=False)
    day_of_week = Column(Integer, nullable=False)
    is_weekend = Column(Integer, nullable=False)
