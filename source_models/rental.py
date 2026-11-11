from sqlalchemy import Column, ForeignKey, func
from sqlalchemy.dialects import mysql

from .base import SourceBase


class Rental(SourceBase):
    __tablename__ = "rental"

    rental_id = Column(mysql.INTEGER(), primary_key=True)
    rental_date = Column(mysql.DATETIME(), nullable=False)
    inventory_id = Column(
        mysql.MEDIUMINT(unsigned=True),
        ForeignKey("inventory.inventory_id"),
        nullable=False,
    )
    customer_id = Column(
        mysql.SMALLINT(unsigned=True), ForeignKey("customer.customer_id"), nullable=False
    )
    return_date = Column(mysql.DATETIME())
    staff_id = Column(
        mysql.TINYINT(unsigned=True), ForeignKey("staff.staff_id"), nullable=False
    )
    last_update = Column(
        mysql.TIMESTAMP(), nullable=False, server_default=func.current_timestamp()
    )
