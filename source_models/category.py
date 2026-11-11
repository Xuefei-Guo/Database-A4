from sqlalchemy import Column, func
from sqlalchemy.dialects import mysql

from .base import SourceBase


class Category(SourceBase):
    __tablename__ = "category"

    category_id = Column(mysql.TINYINT(unsigned=True), primary_key=True)
    name = Column(mysql.VARCHAR(25), nullable=False)
    last_update = Column(
        mysql.TIMESTAMP(), nullable=False, server_default=func.current_timestamp()
    )
