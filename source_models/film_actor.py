from sqlalchemy import Column, ForeignKey, func
from sqlalchemy.dialects import mysql

from .base import SourceBase


class FilmActor(SourceBase):
    __tablename__ = "film_actor"

    actor_id = Column(
        mysql.SMALLINT(unsigned=True), ForeignKey("actor.actor_id"), primary_key=True
    )
    film_id = Column(
        mysql.SMALLINT(unsigned=True), ForeignKey("film.film_id"), primary_key=True
    )
    last_update = Column(
        mysql.TIMESTAMP(), nullable=False, server_default=func.current_timestamp()
    )
