from sqlalchemy import Column, DateTime, String

from .base import TargetBase


class SyncState(TargetBase):
    __tablename__ = "sync_state"

    table_name = Column(String(64), primary_key=True)
    last_update = Column(DateTime)
