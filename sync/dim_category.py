"""Synchronize the dim_category target table."""

from sqlalchemy import select
from source_models import Category
from .helpers import changed_since, get_or_create
from target_models import DimCategory


def sync_categories(source, target, markers=None):
    statement = select(Category).order_by(Category.category_id)
    # Check if this is an incremental sync and filter for changed rows only.
    if markers is not None:
        statement = statement.where(changed_since(Category, markers))
    count = 0
    for category in source.scalars(statement):
        dim_category = get_or_create(target, DimCategory, category_id=category.category_id)
        dim_category.name = category.name
        dim_category.last_update = category.last_update
        count += 1

    return count
