from datetime import datetime

from sqlalchemy import Column, Integer, String, BigInteger, inspect, Enum
from sqlalchemy.ext.hybrid import hybrid_property

from .db_session import SqlAlchemyBase


class ParamOptions(SqlAlchemyBase):
    __tablename__ = 'options'

    option_id = Column(Integer, primary_key=True, autoincrement=True)
    param_id = Column(Integer)
    option_name = Column(String(127))

    def as_dict(self):
        return {
            key: getattr(self, key)
            for key in inspect(self).mapper.column_attrs.keys()
        }
