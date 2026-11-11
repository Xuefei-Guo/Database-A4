"""Shared query and date helpers for synchronization and validation."""

from sqlalchemy import or_, select, true


def begin_source_snapshot(source):
    """Keep related source reads on a consistent MySQL snapshot."""
    if source.get_bind().dialect.name == "mysql":
        source.connection(execution_options={"isolation_level": "REPEATABLE READ"})


def changed_since(model, markers):
    """Return a SQLAlchemy condition for rows changed since the last sync."""
    marker = markers[model.__tablename__]
    if marker is None:
        return true()

    condition = model.last_update >= marker
    if model.__table__.c.last_update.nullable:
        # Rows without a timestamp cannot be safely excluded by a time filter.
        condition = or_(condition, model.last_update.is_(None))
    return condition


def get_or_create(target, model, **natural_key):
    row = target.scalar(select(model).filter_by(**natural_key))
    if row is None:
        row = model(**natural_key)
        target.add(row)
    return row


def make_date_key(value):
    if value is None:
        return None
    return int(value.strftime("%Y%m%d"))
