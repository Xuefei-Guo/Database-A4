"""Create separate connections and ORM session factories for both databases."""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker


# Read connection settings from the environment; keep .env out of Git.
load_dotenv()


# MySQL connection URL
source_url = URL.create(
    drivername="mysql+pymysql",
    username=os.environ["MYSQL_USER"],
    password=os.environ["MYSQL_PASSWORD"],
    host=os.environ["MYSQL_HOST"],
    port=int(os.environ["MYSQL_PORT"]),
    database=os.environ["MYSQL_DATABASE"],
)

# SQLite connection URL
target_url = URL.create(
    drivername="sqlite",
    database=os.environ["SQLITE_PATH"],
)


source_engine = create_engine(source_url)
target_engine = create_engine(target_url)

SourceSession = sessionmaker(bind=source_engine)
TargetSession = sessionmaker(bind=target_engine)
