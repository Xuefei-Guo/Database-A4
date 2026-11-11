from sqlalchemy import Column, ForeignKey, Integer

from .base import TargetBase


class BridgeFilmCategory(TargetBase):
    """Represent each film/category relationship once using a composite key."""

    __tablename__ = "bridge_film_category"

    film_key = Column(Integer, ForeignKey("dim_film.film_key"), primary_key=True)
    category_key = Column(
        Integer, ForeignKey("dim_category.category_key"), primary_key=True
    )
