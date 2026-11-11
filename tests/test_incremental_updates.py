"""Tests for changes to existing source rows."""

from datetime import timedelta

from sqlalchemy import select

import source_models as source
import target_models as target

from .helpers import next_update_time, run_command


def test_incremental_updates(test_databases):
    run_command("init")
    run_command("full-load")
    changed_at = next_update_time(test_databases)

    with test_databases.SourceSession.begin() as session:
        rental, customer = session.execute(
            select(source.Rental, source.Customer)
            .join(source.Customer, source.Rental.customer_id == source.Customer.customer_id)
            .where(source.Rental.return_date.is_(None), source.Customer.last_update.is_not(None))
            .order_by(source.Rental.rental_id)
        ).first()
        rental_id, customer_id = rental.rental_id, customer.customer_id
        address = session.get(source.Address, customer.address_id)
        old_city = session.get(source.City, address.city_id)
        new_city = session.scalars(
            select(source.City).where(
                source.City.city != old_city.city,
                source.City.country_id != old_city.country_id,
            )
            .order_by(source.City.city_id)
        ).first()
        expected_city = new_city.city
        expected_country = session.get(source.Country, new_city.country_id).country
        address.city_id = new_city.city_id
        address.last_update = changed_at
        returned_at = rental.rental_date + timedelta(days=3)
        rental.return_date = returned_at
        rental.last_update = changed_at

    # Keep unchanged related rows from qualifying at the timestamp boundary.
    with test_databases.TargetSession.begin() as session:
        for name in ("customer", "city", "country", "inventory"):
            session.get(target.SyncState, name).last_update = changed_at

    run_command("incremental")
    with test_databases.TargetSession() as session:
        customer = session.scalar(select(target.DimCustomer).where(target.DimCustomer.customer_id == customer_id))
        rental = session.scalar(select(target.FactRental).where(target.FactRental.rental_id == rental_id))
        assert customer.city == expected_city
        assert customer.country == expected_country
        assert rental.date_key_returned == int(returned_at.strftime("%Y%m%d"))
        assert rental.rental_duration_days == 3
