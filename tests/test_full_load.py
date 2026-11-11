"""Full-load tests."""

import source_models as source
import target_models as target

from .helpers import count_rows, run_command


def test_full_load(test_databases):
    run_command("init")
    run_command("full-load")
    pairs = (
        (source.Film, target.DimFilm),
        (source.Actor, target.DimActor),
        (source.Category, target.DimCategory),
        (source.Store, target.DimStore),
        (source.Customer, target.DimCustomer),
        (source.FilmActor, target.BridgeFilmActor),
        (source.FilmCategory, target.BridgeFilmCategory),
        (source.Rental, target.FactRental),
        (source.Payment, target.FactPayment),
    )
    with test_databases.SourceSession() as original, test_databases.TargetSession() as copied:
        for source_model, target_model in pairs:
            assert count_rows(original, source_model) == count_rows(copied, target_model)
