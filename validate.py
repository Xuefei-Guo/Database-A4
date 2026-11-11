from datetime import datetime, time, timedelta
from decimal import Decimal

from sqlalchemy import case, func, select

from db import SourceSession, TargetSession
from source_models import (
    Actor, Category, Customer, Film, Inventory, Payment, Rental, Staff, Store,
)
from sync.helpers import begin_source_snapshot
from target_models import (
    DimActor, DimCategory, DimCustomer, DimDate, DimFilm, DimStore,
    FactPayment, FactRental,
)


def choose_period(source, date_from=None, date_to=None):
    """Default to 30 inclusive days ending at the latest source payment date."""
    if date_to is None:
        # Anchor historical Sakila data to its latest payment, not today's date.
        latest = source.scalar(select(func.max(Payment.payment_date)))
        if latest is None:
            raise ValueError("No source payment date; supply --to to set the validation end date")
        date_to = latest.date()
    if date_from is None:
        date_from = date_to - timedelta(days=29)
    if date_from > date_to:
        raise ValueError("--from must not be later than --to")
    return date_from, date_to


def compare_rows(label, source_rows, target_rows):
    """Compare row counts and ID sets to detect missing or extra records."""
    if len(source_rows) != len(target_rows):
        raise ValueError(
            f"Row count mismatch for {label}: MySQL={len(source_rows)}, SQLite={len(target_rows)}"
        )
    missing = set(source_rows) - set(target_rows)
    extra = set(target_rows) - set(source_rows)
    if missing or extra:
        raise ValueError(
            f"Record mismatch for {label}: missing sample={sorted(missing, key=str)[:5]}, "
            f"extra sample={sorted(extra, key=str)[:5]}"
        )


def check_duplicates(target):
    """Detect duplicate natural IDs in dimensions and facts."""
    keys = (
        (DimFilm, DimFilm.film_id),
        (DimActor, DimActor.actor_id),
        (DimCategory, DimCategory.category_id),
        (DimStore, DimStore.store_id),
        (DimCustomer, DimCustomer.customer_id),
        (FactRental, FactRental.rental_id),
        (FactPayment, FactPayment.payment_id),
    )
    for model, key in keys:
        duplicate = target.execute(
            select(key).group_by(key).having(func.count() > 1).limit(1)
        ).first()
        if duplicate is not None:
            raise ValueError(f"Duplicate natural key in {model.__tablename__}: {tuple(duplicate)}")


def check_orphans(target):
    """Check fact references while allowing a NULL returned-date key."""
    references = (
        (FactRental, FactRental.date_key_rented, DimDate, DimDate.date_key, False),
        (FactRental, FactRental.date_key_returned, DimDate, DimDate.date_key, True),
        (FactRental, FactRental.film_key, DimFilm, DimFilm.film_key, False),
        (FactRental, FactRental.store_key, DimStore, DimStore.store_key, False),
        (FactRental, FactRental.customer_key, DimCustomer, DimCustomer.customer_key, False),
        (FactPayment, FactPayment.date_key_paid, DimDate, DimDate.date_key, False),
        (FactPayment, FactPayment.customer_key, DimCustomer, DimCustomer.customer_key, False),
        (FactPayment, FactPayment.store_key, DimStore, DimStore.store_key, False),
    )
    for child, foreign_key, parent, parent_key, optional in references:
        statement = (
            select(func.count()).select_from(child)
            .outerjoin(parent, foreign_key == parent_key)
            .where(parent_key.is_(None))
        )
        if optional:
            statement = statement.where(foreign_key.is_not(None))
        count = target.scalar(statement)
        if count:
            raise ValueError(
                f"Missing dimension reference: {child.__tablename__}.{foreign_key.key} "
                f"has {count} rows without a matching dimension"
            )


def check_dimensions(source, target):
    pairs = (
        (Film.film_id, DimFilm.film_id),
        (Actor.actor_id, DimActor.actor_id),
        (Category.category_id, DimCategory.category_id),
        (Store.store_id, DimStore.store_id),
        (Customer.customer_id, DimCustomer.customer_id),
    )
    for source_key, target_key in pairs:
        compare_rows(
            target_key.class_.__tablename__,
            source.scalars(select(source_key)).all(),
            target.scalars(select(target_key)).all(),
        )


def check_payment_totals(source, target, source_filters=(), target_filters=()):
    """Compare payment totals by store, with optional date filters."""
    # Use the inventory store, or the staff store when the payment has no rental.
    store_id = case(
        (Payment.rental_id.is_(None), Staff.store_id), else_=Inventory.store_id
    )
    source_totals = dict(source.execute(
        select(store_id, func.sum(Payment.amount)).select_from(Payment)
        .outerjoin(Rental, Payment.rental_id == Rental.rental_id)
        .outerjoin(Inventory, Rental.inventory_id == Inventory.inventory_id)
        .join(Staff, Payment.staff_id == Staff.staff_id)
        .where(*source_filters)
        .group_by(store_id)
    ).all())
    target_totals = dict(target.execute(
        select(DimStore.store_id, func.sum(FactPayment.amount)).select_from(FactPayment)
        .join(DimStore, FactPayment.store_key == DimStore.store_key)
        .where(*target_filters)
        .group_by(DimStore.store_id)
    ).all())
    scope = " in selected period" if source_filters else ""
    for store in source_totals.keys() | target_totals.keys():
        expected = source_totals.get(store, Decimal("0.00"))
        actual = target_totals.get(store, Decimal("0.00"))
        if abs(expected - actual) > Decimal("0.01"):
            raise ValueError(
                f"Payment total mismatch for store {store}{scope}: "
                f"MySQL={expected}, SQLite={actual}"
            )


def check_period_facts(source, target, date_from, date_to):
    """Use rental/payment business dates, not the incremental last_update field."""
    start = datetime.combine(date_from, time.min)
    end = datetime.combine(date_to, time.max)
    first_key = int(date_from.strftime("%Y%m%d"))
    last_key = int(date_to.strftime("%Y%m%d"))

    source_rentals = source.scalars(
        select(Rental.rental_id).where(Rental.rental_date >= start, Rental.rental_date <= end)
    ).all()
    target_rentals = target.scalars(
        select(FactRental.rental_id).where(
            FactRental.date_key_rented >= first_key, FactRental.date_key_rented <= last_key
        )
    ).all()
    compare_rows("fact_rental (selected period)", source_rentals, target_rentals)

    source_payment_filters = (Payment.payment_date >= start, Payment.payment_date <= end)
    target_payment_filters = (
        FactPayment.date_key_paid >= first_key, FactPayment.date_key_paid <= last_key
    )
    source_payments = source.scalars(select(Payment.payment_id).where(*source_payment_filters)).all()
    target_payments = target.scalars(select(FactPayment.payment_id).where(*target_payment_filters)).all()
    compare_rows("fact_payment (selected period)", source_payments, target_payments)

    check_payment_totals(source, target, source_payment_filters, target_payment_filters)
    return len(source_rentals), len(source_payments)


def validate(date_from=None, date_to=None):
    with SourceSession() as source, TargetSession() as target:
        begin_source_snapshot(source)
        date_from, date_to = choose_period(source, date_from, date_to)
        check_duplicates(target)
        check_orphans(target)
        check_dimensions(source, target)
        rentals, payments = check_period_facts(source, target, date_from, date_to)

    print(f"Validation passed: {date_from.isoformat()} to {date_to.isoformat()} (inclusive)")
    print(f"Selected period: {rentals} rentals, {payments} payments; per-store payment differences <= 0.01")
    print("Dimension records checked; no duplicate natural keys or missing fact-to-dimension references")
