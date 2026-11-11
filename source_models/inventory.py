from sqlalchemy import Column, ForeignKey, func
from sqlalchemy.dialects import mysql

from .base import SourceBase


class Inventory(SourceBase):
    __tablename__ = "inventory"

    inventory_id = Column(mysql.MEDIUMINT(unsigned=True), primary_key=True)
    film_id = Column(
        mysql.SMALLINT(unsigned=True), ForeignKey("film.film_id"), nullable=False
    )
    store_id = Column(
        mysql.TINYINT(unsigned=True), ForeignKey("store.store_id"), nullable=False
    )
    last_update = Column(
        mysql.TIMESTAMP(), nullable=False, server_default=func.current_timestamp()
    )
