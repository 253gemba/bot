from datetime import datetime

from sqlalchemy import Column, Integer, String, BigInteger, inspect, DateTime, Float, SmallInteger
from sqlalchemy.ext.hybrid import hybrid_property

from .db_session import SqlAlchemyBase


class Stats(SqlAlchemyBase):
    __tablename__ = 'all_cities'
    __table_args__ = {'extend_existing': True}

    city_id = Column(Integer, primary_key=True)
    city_name = Column(String(127))
    city_area = Column(String(255))
    city_population = Column(Integer)
    is_city = Column(Integer)
    timezone = Column(Integer)

    def as_dict(self):
        return {
            key: getattr(self, key)
            for key in inspect(self).mapper.column_attrs.keys()
        }
