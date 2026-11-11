import os
from types import SimpleNamespace

import pytest
from sqlalchemy import MetaData, create_engine, delete, insert, select
from sqlalchemy.engine import URL
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.schema import CreateSchema

import db
import sync.runner as sync
import validate as validation
from source_models import SourceBase


@pytest.fixture(scope="session")
def test_source_engine():
    name = os.environ.get("MYSQL_TEST_DATABASE", "sakila_test")
    # Create the test database if it doesn't exist, then connect to it.
    with db.source_engine.begin() as connection:
        connection.execute(CreateSchema(name, if_not_exists=True))

    engine = create_engine(db.source_engine.url.set(database=name), hide_parameters=True)
    try:
        # Reset the test database before each test.
        SourceBase.metadata.create_all(engine)
        print(f"\nSeparate MySQL test database: {name} (15 tables reset before each test)")
        yield engine
    finally:
        engine.dispose()


def reset_source(engine):
    """Restore the test source from the original database."""
    original_db = db.source_engine.url.database
    original_metadata = MetaData()
    with engine.connect() as connection:
        # Disable foreign key checks to allow truncating and copying tables in any order.
        connection.exec_driver_sql("SET FOREIGN_KEY_CHECKS = 0")
        connection.commit()
        try:
            with Session(connection) as copy, copy.begin():
                # Clear the test database tables before copying from the original database.
                for model in sync.SOURCE_MODELS:
                    copy.execute(delete(model))
                # Copy each source table from the original database to the test database.
                for model in sync.SOURCE_MODELS:
                    table = model.__table__
                    # Use the original database's metadata to select from the original table.
                    original_table = table.to_metadata(original_metadata, schema=original_db)
                    # Insert all rows from the original table into the test database's table.
                    copy.execute(
                        insert(model).from_select(
                            table.c.keys(), select(original_table), include_defaults=False
                        )
                    )
        finally:
            connection.rollback()
            connection.exec_driver_sql("SET FOREIGN_KEY_CHECKS = 1")
            connection.commit()


@pytest.fixture
def test_databases(test_source_engine, tmp_path, monkeypatch):
    """Use a reset source copy and a temporary SQLite file for each test."""
    reset_source(test_source_engine)
    sqlite_path = tmp_path / "analytics.db"
    target_engine = create_engine(URL.create("sqlite", database=str(sqlite_path)))
    try:
        databases = SimpleNamespace(
            target_engine=target_engine,
            SourceSession=sessionmaker(bind=test_source_engine),
            TargetSession=sessionmaker(bind=target_engine),
        )
        for module in (sync, validation):
            monkeypatch.setattr(module, "SourceSession", databases.SourceSession)
            monkeypatch.setattr(module, "TargetSession", databases.TargetSession)
        monkeypatch.setattr(sync, "target_engine", target_engine)
        yield databases
    finally:
        target_engine.dispose()
