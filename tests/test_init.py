from sqlalchemy import inspect

from .helpers import run_command


def test_init(test_databases):
    run_command("init")
    tables = inspect(test_databases.target_engine).get_table_names()
    assert set(tables) == {
        "dim_date", "dim_film", "dim_actor", "dim_category", "dim_store",
        "dim_customer", "bridge_film_actor", "bridge_film_category",
        "fact_rental", "fact_payment", "sync_state",
    }
