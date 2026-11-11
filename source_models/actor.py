from sqlalchemy import Column, func
from sqlalchemy.dialects import mysql

from .base import SourceBase


class Actor(SourceBase):
    __tablename__ = "actor"

    actor_id = Column(mysql.SMALLINT(unsigned=True), primary_key=True)
    first_name = Column(mysql.VARCHAR(45), nullable=False)
    last_name = Column(mysql.VARCHAR(45), nullable=False)
    last_update = Column(
        mysql.TIMESTAMP(), nullable=False, server_default=func.current_timestamp()
    )
