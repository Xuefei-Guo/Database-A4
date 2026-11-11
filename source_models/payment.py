from sqlalchemy import Column, ForeignKey, func
from sqlalchemy.dialects import mysql

from .base import SourceBase


class Payment(SourceBase):
    __tablename__ = "payment"

    payment_id = Column(mysql.SMALLINT(unsigned=True), primary_key=True)
    customer_id = Column(
        mysql.SMALLINT(unsigned=True), ForeignKey("customer.customer_id"), nullable=False
    )
    staff_id = Column(
        mysql.TINYINT(unsigned=True), ForeignKey("staff.staff_id"), nullable=False
    )
    rental_id = Column(mysql.INTEGER(), ForeignKey("rental.rental_id"))
    amount = Column(mysql.DECIMAL(5, 2), nullable=False)
    payment_date = Column(mysql.DATETIME(), nullable=False)
    last_update = Column(mysql.TIMESTAMP(), server_default=func.current_timestamp())
