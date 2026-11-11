"""Coordinate synchronization, validation and atomic checkpoint updates."""

from sqlalchemy import func, select

from db import SourceSession, TargetSession, target_engine
from source_models import (
    Actor, Address, Category, City, Country, Customer,
    Film, FilmActor, FilmCategory, Inventory, Language,
    Payment, Rental, Staff, Store,
)
from .dim_date import sync_dates
from .dim_film import sync_films
from .dim_actor import sync_actors
from .dim_category import sync_categories
from .dim_store import sync_stores
from .dim_customer import sync_customers
from .bridge_film_actor import sync_film_actors
from .bridge_film_category import sync_film_categories
from .fact_rental import sync_rentals
from .fact_payment import sync_payments
from .helpers import begin_source_snapshot, get_or_create
from target_models import (
    BridgeFilmActor, BridgeFilmCategory,
    DimActor, DimCategory, DimCustomer, DimFilm, DimStore,
    FactPayment, FactRental, SyncState, TargetBase,
)
from validate import check_payment_totals


SOURCE_MODELS = (
    Actor, Address, Category, City, Country, Customer,
    Film, FilmActor, FilmCategory, Inventory, Language,
    Payment, Rental, Staff, Store,
)


def validate_counts_and_totals(source, target):
    """Compare row counts and key totals between source and target."""
    model_pairs = (
        (Film, DimFilm),
        (Actor, DimActor),
        (Category, DimCategory),
        (Store, DimStore),
        (Customer, DimCustomer),
        (FilmActor, BridgeFilmActor),
        (FilmCategory, BridgeFilmCategory),
        (Rental, FactRental),
        (Payment, FactPayment),
    )

    # Compare row counts for each source/target pair.
    for source_model, target_model in model_pairs:
        source_count = source.scalar(
            select(func.count()).select_from(source_model)
        )
        target_count = target.scalar(
            select(func.count()).select_from(target_model)
        )
        if source_count != target_count:
            raise ValueError(
                f"Row count mismatch: {source_model.__tablename__}={source_count}, "
                f"{target_model.__tablename__}={target_count}"
            )

    check_payment_totals(source, target)


def read_sync_state(target):
    markers = dict(
        target.execute(select(SyncState.table_name, SyncState.last_update)).all()
    )
    required_tables = {model.__tablename__ for model in SOURCE_MODELS}
    # Check that all source tables have a marker; otherwise, the incremental sync may miss changes.
    if not required_tables.issubset(markers):
        raise ValueError("Incomplete sync_state; run full-load first")
    return markers


def save_sync_state(source, target, previous_markers=None):
    for model in SOURCE_MODELS:
        # Use the source's max last_update as the new marker for this table.
        marker = source.scalar(select(func.max(model.last_update)))
        if previous_markers is not None:
            previous = previous_markers[model.__tablename__]
            if previous is not None and (marker is None or marker < previous):
                marker = previous
        state = get_or_create(
            target, SyncState, table_name=model.__tablename__
        )
        state.last_update = marker


def sync_data(source, target, markers=None):
    counts = {}
    counts["dim_film"] = sync_films(source, target, markers)
    counts["dim_actor"] = sync_actors(source, target, markers)
    counts["dim_category"] = sync_categories(source, target, markers)
    counts["dim_store"] = sync_stores(source, target, markers)
    counts["dim_customer"] = sync_customers(source, target, markers)
    counts["dim_date"] = sync_dates(source, target, markers)
    target.flush()
    counts["bridge_film_actor"] = sync_film_actors(source, target, markers)
    counts["bridge_film_category"] = sync_film_categories(source, target, markers)
    counts["fact_rental"] = sync_rentals(source, target, markers)
    counts["fact_payment"] = sync_payments(source, target, markers)
    target.flush()
    return counts


def init_db():
    with SourceSession() as source:
        begin_source_snapshot(source)
        TargetBase.metadata.create_all(target_engine)
        # Prepare dim_date and sync_state
        with TargetSession.begin() as target:
            sync_dates(source, target)
            for model in SOURCE_MODELS:
                if target.get(SyncState, model.__tablename__) is None:
                    target.add(SyncState(table_name=model.__tablename__))

    print("Initialization successful: MySQL connected; all 11 SQLite tables are ready")


def run_sync(incremental_mode):
    with SourceSession() as source, TargetSession.begin() as target:
        begin_source_snapshot(source)
        markers = read_sync_state(target) if incremental_mode else None
        counts = sync_data(source, target, markers)

        validate_counts_and_totals(source, target)
        save_sync_state(source, target, markers)

    sync_name = "Incremental sync" if incremental_mode else "Full load"
    print(f"{sync_name} completed successfully. Validation passed.")
    for table_name, count in counts.items():
        print(f"{table_name}: processed {count} rows")
    return counts


def full_load():
    return run_sync(incremental_mode=False)


def incremental():
    return run_sync(incremental_mode=True)
