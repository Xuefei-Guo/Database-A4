from sqlalchemy import Column, ForeignKey, Integer

from .base import TargetBase


class FactRental(TargetBase):
    __tablename__ = "fact_rental"

    fact_rental_key = Column(Integer, primary_key=True, autoincrement=True)
    rental_id = Column(Integer, nullable=False, unique=True, index=True)
    date_key_rented = Column(
        Integer, ForeignKey("dim_date.date_key"), nullable=False, index=True
    )
    date_key_returned = Column(
        Integer, ForeignKey("dim_date.date_key"), index=True
    )
    film_key = Column(
        Integer, ForeignKey("dim_film.film_key"), nullable=False, index=True
    )
    store_key = Column(
        Integer, ForeignKey("dim_store.store_key"), nullable=False, index=True
    )
    customer_key = Column(
        Integer, ForeignKey("dim_customer.customer_key"), nullable=False, index=True
    )
    staff_id = Column(Integer, nullable=False)
    rental_duration_days = Column(Integer)
