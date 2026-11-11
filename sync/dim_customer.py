"""Synchronize the dim_customer target table."""

from sqlalchemy import or_, select
from source_models import Address, City, Country, Customer
from .helpers import changed_since, get_or_create
from target_models import DimCustomer


def sync_customers(source, target, markers=None):
    statement = (
        select(Customer, City.city, Country.country)
        .join(Address, Customer.address_id == Address.address_id)
        .join(City, Address.city_id == City.city_id)
        .join(Country, City.country_id == Country.country_id)
        .order_by(Customer.customer_id)
    )
    # Check if this is an incremental sync and filter for changed rows only.
    if markers is not None:
        statement = statement.where(
            or_(
                changed_since(Customer, markers),
                changed_since(Address, markers),
                changed_since(City, markers),
                changed_since(Country, markers),
            )
        )

    count = 0
    for customer, city_name, country_name in source.execute(statement):
        dim_customer = get_or_create(target, DimCustomer, customer_id=customer.customer_id)
        dim_customer.first_name = customer.first_name
        dim_customer.last_name = customer.last_name
        dim_customer.active = customer.active
        dim_customer.city = city_name
        dim_customer.country = country_name
        dim_customer.last_update = customer.last_update
        count += 1

    return count
