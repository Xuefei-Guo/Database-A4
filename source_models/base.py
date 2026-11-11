from sqlalchemy.orm import DeclarativeBase


class SourceBase(DeclarativeBase):
    """Keep source metadata separate from the SQLite analytics metadata."""

    pass
