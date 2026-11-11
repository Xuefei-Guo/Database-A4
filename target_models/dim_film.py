from sqlalchemy import Column, DateTime, Integer, String

from .base import TargetBase


class DimFilm(TargetBase):
    __tablename__ = "dim_film"

    film_key = Column(Integer, primary_key=True, autoincrement=True)
    film_id = Column(Integer, nullable=False, unique=True, index=True)
    title = Column(String(128), nullable=False)
    rating = Column(String(10))
    length = Column(Integer)
    language = Column(String(20), nullable=False)
    release_year = Column(Integer)
    last_update = Column(DateTime, nullable=False)
