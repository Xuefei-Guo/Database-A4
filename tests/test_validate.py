"""Validation command tests."""

from decimal import Decimal

from sqlalchemy import select

import main
import target_models as target

from .helpers import run_command


def test_validate(test_databases, capsys):
    run_command("init")
    run_command("full-load")
    run_command("validate")

    with test_databases.TargetSession.begin() as session:
        payment = session.scalar(
            select(target.FactPayment).order_by(target.FactPayment.date_key_paid.desc()).limit(1)
        )
        payment.amount += Decimal("1.00")

    assert main.main(["validate"]) == 1
    output = capsys.readouterr()
    assert "Payment total mismatch" in output.err
    print(output.out + output.err, end="")
