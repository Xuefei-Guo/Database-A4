from sqlalchemy.types import UserDefinedType


class Geometry(UserDefinedType):
    """Represent MySQL GEOMETRY columns using their native binary values."""

    cache_ok = True

    def get_col_spec(self, **kw):
        return "GEOMETRY"
