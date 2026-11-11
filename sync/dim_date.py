"""Synchronize the dim_date target table."""

from sqlalchemy import select
from source_models import Payment, Rental
from .helpers import changed_since, make_date_key
from target_models import DimDate


def sync_dates(source, target, markers=None):
    rental_statement = select(Rental.rental_date, Rental.return_date)
    payment_statement = select(Payment.payment_date)
    # Check if this is an incremental sync and filter for changed rows only.
    if markers is not None:
        rental_statement = rental_statement.where(changed_since(Rental, markers))
        payment_statement = payment_statement.where(changed_since(Payment, markers))

    dates = set()
    for rental_date, return_date in source.execute(rental_statement):
        dates.add(rental_date.date())
        if return_date is not None:
            dates.add(return_date.date())

    for payment_date in source.scalars(payment_statement):
        dates.add(payment_date.date())

    for day in sorted(dates):
        date_key = make_date_key(day)
        dim_date = target.get(DimDate, date_key)
        if dim_date is None:
            dim_date = DimDate(date_key=date_key)
            target.add(dim_date)

        dim_date.date = day
        dim_date.year = day.year
        dim_date.quarter = (day.month - 1) // 3 + 1
        dim_date.month = day.month
        dim_date.day_of_month = day.day
        # ISO weekdays are Monday=1 through Sunday=7; weekends are 6 and 7.
        dim_date.day_of_week = day.isoweekday()
        dim_date.is_weekend = int(day.isoweekday() >= 6)

    return len(dates)
