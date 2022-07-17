from datetime import datetime

from sqlalchemy import Column, Integer, String, BigInteger, inspect, DateTime, Float, SmallInteger, Enum
from sqlalchemy.ext.hybrid import hybrid_property

from .db_session import SqlAlchemyBase


class Utm(SqlAlchemyBase):
    __tablename__ = 'utm'

    utm_id = Column(Integer, primary_key=True)
    date_create = Column(DateTime, default=datetime.now())
    bonus = Column(Integer, default=0)

    def as_dict(self):
        return {
            key: self.string_start_date if key == 'date_create' else getattr(self, key)
            for key in inspect(self).mapper.column_attrs.keys()
        }

    @hybrid_property
    def string_start_date(self):
        return self.date_create
