from sqlalchemy import Column, ForeignKey, func
from sqlalchemy.dialects import mysql

from .base import SourceBase


class Store(SourceBase):
    __tablename__ = "store"

    store_id = Column(mysql.TINYINT(unsigned=True), primary_key=True)
    manager_staff_id = Column(
        mysql.TINYINT(unsigned=True), ForeignKey("staff.staff_id"), nullable=False
    )
    address_id = Column(
        mysql.SMALLINT(unsigned=True), ForeignKey("address.address_id"), nullable=False
    )
    last_update = Column(
        mysql.TIMESTAMP(), nullable=False, server_default=func.current_timestamp()
    )
