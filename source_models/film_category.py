from sqlalchemy import Column, ForeignKey, func
from sqlalchemy.dialects import mysql

from .base import SourceBase


class FilmCategory(SourceBase):
    __tablename__ = "film_category"

    film_id = Column(
        mysql.SMALLINT(unsigned=True), ForeignKey("film.film_id"), primary_key=True
    )
    category_id = Column(
        mysql.TINYINT(unsigned=True), ForeignKey("category.category_id"), primary_key=True
    )
    last_update = Column(
        mysql.TIMESTAMP(), nullable=False, server_default=func.current_timestamp()
    )
