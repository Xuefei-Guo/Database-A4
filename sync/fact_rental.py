"""Synchronize the fact_rental target table."""

from sqlalchemy import or_, select
from source_models import Inventory, Rental
from .helpers import changed_since, get_or_create, make_date_key
from target_models import DimCustomer, DimFilm, DimStore, FactRental


def sync_rentals(source, target, markers=None):
    film_keys = dict(
        target.execute(select(DimFilm.film_id, DimFilm.film_key)).all()
    )
    store_keys = dict(
        target.execute(select(DimStore.store_id, DimStore.store_key)).all()
    )
    customer_keys = dict(
        target.execute(select(DimCustomer.customer_id, DimCustomer.customer_key)).all()
    )

    statement = (
        select(Rental, Inventory.film_id, Inventory.store_id)
        .join(Inventory, Rental.inventory_id == Inventory.inventory_id)
        .order_by(Rental.rental_id)
    )
    # Check if this is an incremental sync and filter for changed rows only.
    if markers is not None:
        statement = statement.where(
            or_(changed_since(Rental, markers), changed_since(Inventory, markers))
        )

    count = 0
    for rental, film_id, store_id in source.execute(statement):
        fact = get_or_create(target, FactRental, rental_id=rental.rental_id)
        fact.date_key_rented = make_date_key(rental.rental_date)
        fact.date_key_returned = make_date_key(rental.return_date)
        fact.film_key = film_keys[film_id]
        fact.store_key = store_keys[store_id]
        fact.customer_key = customer_keys[rental.customer_id]
        fact.staff_id = rental.staff_id
        fact.rental_duration_days = (
            (rental.return_date.date() - rental.rental_date.date()).days
            if rental.return_date is not None
            else None
        )
        count += 1

    return count
