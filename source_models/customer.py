from sqlalchemy import Column, ForeignKey, func
from sqlalchemy.dialects import mysql

from .base import SourceBase


class Customer(SourceBase):
    __tablename__ = "customer"

    customer_id = Column(mysql.SMALLINT(unsigned=True), primary_key=True)
    store_id = Column(
        mysql.TINYINT(unsigned=True), ForeignKey("store.store_id"), nullable=False
    )
    first_name = Column(mysql.VARCHAR(45), nullable=False)
    last_name = Column(mysql.VARCHAR(45), nullable=False)
    email = Column(mysql.VARCHAR(50))
    address_id = Column(
        mysql.SMALLINT(unsigned=True), ForeignKey("address.address_id"), nullable=False
    )
    active = Column(mysql.TINYINT(display_width=1), nullable=False, server_default="1")
    create_date = Column(mysql.DATETIME(), nullable=False)
    last_update = Column(mysql.TIMESTAMP(), server_default=func.current_timestamp())
