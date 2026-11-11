"""Synchronize the bridge_film_category target table."""

from sqlalchemy import select
from source_models import FilmCategory
from .helpers import changed_since, get_or_create
from target_models import BridgeFilmCategory, DimCategory, DimFilm


def sync_film_categories(source, target, markers=None):
    film_keys = dict(
        target.execute(select(DimFilm.film_id, DimFilm.film_key)).all()
    )
    category_keys = dict(
        target.execute(select(DimCategory.category_id, DimCategory.category_key)).all()
    )

    statement = select(FilmCategory).order_by(
        FilmCategory.film_id, FilmCategory.category_id
    )
    # Check if this is an incremental sync and filter for changed rows only.
    if markers is not None:
        statement = statement.where(changed_since(FilmCategory, markers))
    count = 0
    for link in source.scalars(statement):
        film_key = film_keys[link.film_id]
        category_key = category_keys[link.category_id]

        get_or_create(
            target, BridgeFilmCategory, film_key=film_key, category_key=category_key
        )
        count += 1

    return count
