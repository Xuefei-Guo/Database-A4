from sqlalchemy import Column, func
from sqlalchemy.dialects import mysql

from .base import SourceBase


class Language(SourceBase):
    __tablename__ = "language"

    language_id = Column(mysql.TINYINT(unsigned=True), primary_key=True)
    name = Column(mysql.CHAR(20), nullable=False)
    last_update = Column(
        mysql.TIMESTAMP(), nullable=False, server_default=func.current_timestamp()
    )
