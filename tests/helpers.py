from datetime import datetime, timedelta

from sqlalchemy import func, select

import main
import target_models as target


def run_command(command):
    assert main.main([command]) == 0


def count_rows(session, model):
    return session.scalar(select(func.count()).select_from(model))


def next_id(session, column):
    return (session.scalar(select(func.max(column))) or 0) + 1


def next_update_time(databases):
    with databases.TargetSession() as session:
        latest = session.scalar(select(func.max(target.SyncState.last_update)))
    now = datetime.now().replace(microsecond=0)
    return max(now, latest or now) + timedelta(seconds=1)
