from sqlalchemy import Column, func
from sqlalchemy.dialects import mysql

from .base import SourceBase


class Country(SourceBase):
    __tablename__ = "country"

    country_id = Column(mysql.SMALLINT(unsigned=True), primary_key=True)
    country = Column(mysql.VARCHAR(50), nullable=False)
    last_update = Column(
        mysql.TIMESTAMP(), nullable=False, server_default=func.current_timestamp()
    )
