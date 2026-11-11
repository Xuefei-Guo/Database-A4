"""Synchronize the fact_payment target table."""

from sqlalchemy import and_, or_, select
from source_models import Inventory, Payment, Rental, Staff
from .helpers import changed_since, get_or_create, make_date_key
from target_models import DimCustomer, DimStore, FactPayment


def sync_payments(source, target, markers=None):
    store_keys = dict(
        target.execute(select(DimStore.store_id, DimStore.store_key)).all()
    )
    customer_keys = dict(
        target.execute(select(DimCustomer.customer_id, DimCustomer.customer_key)).all()
    )

    statement = (
        select(Payment, Inventory.store_id, Staff.store_id)
        .outerjoin(Rental, Payment.rental_id == Rental.rental_id)
        .outerjoin(Inventory, Rental.inventory_id == Inventory.inventory_id)
        .join(Staff, Payment.staff_id == Staff.staff_id)
        .order_by(Payment.payment_id)
    )
    # Check if this is an incremental sync and filter for changed rows only.
    if markers is not None:
        statement = statement.where(
            # payment changes or rental/inventory changes (if there is a rental) or staff changes (if no rental)
            or_(
                
                changed_since(Payment, markers),
                and_(
                    Payment.rental_id.is_not(None),
                    or_(
                        changed_since(Rental, markers),
                        changed_since(Inventory, markers),
                    ),
                ),
                and_(
                    Payment.rental_id.is_(None), changed_since(Staff, markers)
                ),
            )
        )

    count = 0
    for payment, rental_store_id, staff_store_id in source.execute(statement):
        store_id = (
            staff_store_id if payment.rental_id is None else rental_store_id
        )
        if store_id is None:
            raise ValueError(f"Payment {payment.payment_id} has no matching store")

        fact = get_or_create(target, FactPayment, payment_id=payment.payment_id)
        fact.date_key_paid = make_date_key(payment.payment_date)
        fact.customer_key = customer_keys[payment.customer_id]
        fact.store_key = store_keys[store_id]
        fact.staff_id = payment.staff_id
        fact.amount = payment.amount
        count += 1

    return count
