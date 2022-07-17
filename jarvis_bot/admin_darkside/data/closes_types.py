from datetime import datetime

from sqlalchemy import Column, Integer, String, BigInteger, inspect, Enum, SmallInteger
from sqlalchemy.ext.hybrid import hybrid_property

from .db_session import SqlAlchemyBase


class ClosesTypes(SqlAlchemyBase):
    __tablename__ = 'closes_types'

    type_id = Column(Integer, primary_key=True, autoincrement=True)
    type_name = Column(String(127), default='')
    parent_id = Column(Integer)
    body_part = Column(String(16), default=None)
    is_type = Column(SmallInteger, default=None)

    def as_dict(self):
        return {
            key: getattr(self, key)
            for key in inspect(self).mapper.column_attrs.keys()
        }
