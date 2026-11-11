from sqlalchemy import Column, ForeignKey, func
from sqlalchemy.dialects import mysql

from .base import SourceBase
from .types import Geometry


class Address(SourceBase):
    __tablename__ = "address"

    address_id = Column(mysql.SMALLINT(unsigned=True), primary_key=True)
    address = Column(mysql.VARCHAR(50), nullable=False)
    address2 = Column(mysql.VARCHAR(50))
    district = Column(mysql.VARCHAR(20), nullable=False)
    city_id = Column(
        mysql.SMALLINT(unsigned=True), ForeignKey("city.city_id"), nullable=False
    )
    postal_code = Column(mysql.VARCHAR(10))
    phone = Column(mysql.VARCHAR(20), nullable=False)
    location = Column(Geometry(), nullable=False)
    last_update = Column(
        mysql.TIMESTAMP(), nullable=False, server_default=func.current_timestamp()
    )
