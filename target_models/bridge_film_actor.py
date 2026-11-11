from sqlalchemy import Column, ForeignKey, Integer

from .base import TargetBase


class BridgeFilmActor(TargetBase):
    """Represent each film/actor relationship once using a composite key."""

    __tablename__ = "bridge_film_actor"

    film_key = Column(Integer, ForeignKey("dim_film.film_key"), primary_key=True)
    actor_key = Column(Integer, ForeignKey("dim_actor.actor_key"), primary_key=True)
