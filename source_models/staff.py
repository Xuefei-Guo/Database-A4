from sqlalchemy import Column, ForeignKey, func
from sqlalchemy.dialects import mysql

from .base import SourceBase


class Staff(SourceBase):
    __tablename__ = "staff"

    staff_id = Column(mysql.TINYINT(unsigned=True), primary_key=True)
    first_name = Column(mysql.VARCHAR(45), nullable=False)
    last_name = Column(mysql.VARCHAR(45), nullable=False)
    address_id = Column(
        mysql.SMALLINT(unsigned=True), ForeignKey("address.address_id"), nullable=False
    )
    picture = Column(mysql.BLOB())
    email = Column(mysql.VARCHAR(50))
    store_id = Column(
        mysql.TINYINT(unsigned=True), ForeignKey("store.store_id"), nullable=False
    )
    active = Column(mysql.TINYINT(display_width=1), nullable=False, server_default="1")
    username = Column(mysql.VARCHAR(16), nullable=False)
    password = Column(mysql.VARCHAR(40, charset="utf8mb4", collation="utf8mb4_bin"))
    last_update = Column(
        mysql.TIMESTAMP(), nullable=False, server_default=func.current_timestamp()
    )
