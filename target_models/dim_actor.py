from sqlalchemy import Column, DateTime, Integer, String

from .base import TargetBase


class DimActor(TargetBase):
    __tablename__ = "dim_actor"

    actor_key = Column(Integer, primary_key=True, autoincrement=True)
    actor_id = Column(Integer, nullable=False, unique=True, index=True)
    first_name = Column(String(45), nullable=False)
    last_name = Column(String(45), nullable=False)
    last_update = Column(DateTime, nullable=False)
