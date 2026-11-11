"""Synchronize the dim_film target table."""

from sqlalchemy import or_, select
from source_models import Film, Language
from .helpers import changed_since, get_or_create
from target_models import DimFilm


def sync_films(source, target, markers=None):
    statement = (
        select(Film, Language.name)
        .join(Language, Film.language_id == Language.language_id)
        .order_by(Film.film_id)
    )
    # Check if this is an incremental sync and filter for changed rows only.
    if markers is not None:
        statement = statement.where(
            or_(changed_since(Film, markers), changed_since(Language, markers))
        )

    count = 0
    for film, language_name in source.execute(statement):
        dim_film = get_or_create(target, DimFilm, film_id=film.film_id)
        dim_film.title = film.title
        dim_film.rating = film.rating
        dim_film.length = film.length
        dim_film.language = language_name
        dim_film.release_year = film.release_year
        dim_film.last_update = film.last_update
        count += 1

    return count
