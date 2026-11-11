"""Tests for newly inserted source rows."""

from datetime import timedelta
from decimal import Decimal

from sqlalchemy import select

import source_models as source
import target_models as target

from .helpers import next_id, next_update_time, run_command


def test_incremental_new(test_databases):
    run_command("init")
    run_command("full-load")
    changed_at = next_update_time(test_databases)
    rented_at = changed_at - timedelta(days=2)
    paid_at = changed_at - timedelta(days=1)
    amount = Decimal("3.25")

    with test_databases.SourceSession.begin() as session:
        # Insert a new rental and payment with a future last_update timestamp.
        rental_id = next_id(session, source.Rental.rental_id)
        payment_id = next_id(session, source.Payment.payment_id)
        inventory = session.scalars(select(source.Inventory).limit(1)).one()
        film_id, store_id = inventory.film_id, inventory.store_id
        customer_id = session.scalar(select(source.Customer.customer_id))
        staff_id = session.scalar(
            select(source.Staff.staff_id).where(source.Staff.store_id != store_id)
        )
        session.add(source.Rental(
            rental_id=rental_id, rental_date=rented_at, inventory_id=inventory.inventory_id,
            customer_id=customer_id, staff_id=staff_id, last_update=changed_at,
        ))
        session.flush()
        session.add(source.Payment(
            payment_id=payment_id, customer_id=customer_id, staff_id=staff_id,
            rental_id=rental_id, amount=amount, payment_date=paid_at, last_update=changed_at,
        ))

    run_command("incremental")
    with test_databases.TargetSession() as session:
        # Verify that the new rental and payment were copied to the target database.
        rental = session.scalars(
            select(target.FactRental).where(target.FactRental.rental_id == rental_id)
        ).one()
        payment = session.scalars(
            select(target.FactPayment).where(target.FactPayment.payment_id == payment_id)
        ).one()

        assert rental.fact_rental_key > 0
        assert rental.date_key_rented == int(rented_at.strftime("%Y%m%d"))
        assert session.get(target.DimDate, rental.date_key_rented).date == rented_at.date()
        assert rental.date_key_returned is None
        assert session.get(target.DimFilm, rental.film_key).film_id == film_id
        assert session.get(target.DimStore, rental.store_key).store_id == store_id
        assert session.get(target.DimCustomer, rental.customer_key).customer_id == customer_id
        assert rental.staff_id == staff_id
        assert rental.rental_duration_days is None

        assert payment.fact_payment_key > 0
        assert payment.date_key_paid == int(paid_at.strftime("%Y%m%d"))
        assert session.get(target.DimDate, payment.date_key_paid).date == paid_at.date()
        assert payment.customer_key == rental.customer_key
        assert payment.store_key == rental.store_key
        assert payment.staff_id == staff_id
        assert payment.amount == amount
