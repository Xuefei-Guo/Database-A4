"""Synchronize the bridge_film_actor target table."""

from sqlalchemy import select
from source_models import FilmActor
from .helpers import changed_since, get_or_create
from target_models import BridgeFilmActor, DimActor, DimFilm


def sync_film_actors(source, target, markers=None):
    film_keys = dict(
        target.execute(select(DimFilm.film_id, DimFilm.film_key)).all()
    )
    actor_keys = dict(
        target.execute(select(DimActor.actor_id, DimActor.actor_key)).all()
    )

    statement = select(FilmActor).order_by(FilmActor.film_id, FilmActor.actor_id)
    # Check if this is an incremental sync and filter for changed rows only.
    if markers is not None:
        statement = statement.where(changed_since(FilmActor, markers))
    count = 0
    for link in source.scalars(statement):
        film_key = film_keys[link.film_id]
        actor_key = actor_keys[link.actor_id]

        get_or_create(
            target, BridgeFilmActor, film_key=film_key, actor_key=actor_key
        )
        count += 1

    return count
