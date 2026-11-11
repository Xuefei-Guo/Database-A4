"""Synchronize the dim_actor target table."""

from sqlalchemy import select
from source_models import Actor
from .helpers import changed_since, get_or_create
from target_models import DimActor


def sync_actors(source, target, markers=None):
    statement = select(Actor).order_by(Actor.actor_id)
    # Check if this is an incremental sync and filter for changed rows only.
    if markers is not None:
        statement = statement.where(changed_since(Actor, markers))
    count = 0
    for actor in source.scalars(statement):
        dim_actor = get_or_create(target, DimActor, actor_id=actor.actor_id)
        dim_actor.first_name = actor.first_name
        dim_actor.last_name = actor.last_name
        dim_actor.last_update = actor.last_update
        count += 1

    return count
