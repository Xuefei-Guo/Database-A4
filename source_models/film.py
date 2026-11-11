from sqlalchemy import Column, ForeignKey, func
from sqlalchemy.dialects import mysql

from .base import SourceBase


class Film(SourceBase):
    __tablename__ = "film"

    film_id = Column(mysql.SMALLINT(unsigned=True), primary_key=True)
    title = Column(mysql.VARCHAR(128), nullable=False)
    description = Column(mysql.TEXT())
    release_year = Column(mysql.YEAR())
    language_id = Column(
        mysql.TINYINT(unsigned=True), ForeignKey("language.language_id"), nullable=False
    )
    original_language_id = Column(
        mysql.TINYINT(unsigned=True), ForeignKey("language.language_id")
    )
    rental_duration = Column(
        mysql.TINYINT(unsigned=True), nullable=False, server_default="3"
    )
    rental_rate = Column(mysql.DECIMAL(4, 2), nullable=False, server_default="4.99")
    length = Column(mysql.SMALLINT(unsigned=True))
    replacement_cost = Column(
        mysql.DECIMAL(5, 2), nullable=False, server_default="19.99"
    )
    rating = Column(mysql.ENUM("G", "PG", "PG-13", "R", "NC-17"), server_default="G")
    special_features = Column(
        mysql.SET("Trailers", "Commentaries", "Deleted Scenes", "Behind the Scenes")
    )
    last_update = Column(
        mysql.TIMESTAMP(), nullable=False, server_default=func.current_timestamp()
    )
