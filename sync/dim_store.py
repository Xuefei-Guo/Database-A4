"""Synchronize the dim_store target table."""

from sqlalchemy import or_, select
from source_models import Address, City, Country, Store
from .helpers import changed_since, get_or_create
from target_models import DimStore


def sync_stores(source, target, markers=None):
    statement = (
        select(Store, City.city, Country.country)
        .join(Address, Store.address_id == Address.address_id)
        .join(City, Address.city_id == City.city_id)
        .join(Country, City.country_id == Country.country_id)
        .order_by(Store.store_id)
    )
    # Check if this is an incremental sync and filter for changed rows only.
    if markers is not None:
        statement = statement.where(
            or_(
                changed_since(Store, markers),
                changed_since(Address, markers),
                changed_since(City, markers),
                changed_since(Country, markers),
            )
        )

    count = 0
    for store, city_name, country_name in source.execute(statement):
        dim_store = get_or_create(target, DimStore, store_id=store.store_id)
        dim_store.city = city_name
        dim_store.country = country_name
        dim_store.last_update = store.last_update
        count += 1

    return count
