from sqlalchemy import Column, ForeignKey, func
from sqlalchemy.dialects import mysql

from .base import SourceBase


class City(SourceBase):
    __tablename__ = "city"

    city_id = Column(mysql.SMALLINT(unsigned=True), primary_key=True)
    city = Column(mysql.VARCHAR(50), nullable=False)
    country_id = Column(
        mysql.SMALLINT(unsigned=True), ForeignKey("country.country_id"), nullable=False
    )
    last_update = Column(
        mysql.TIMESTAMP(), nullable=False, server_default=func.current_timestamp()
    )
