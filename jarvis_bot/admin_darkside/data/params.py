from datetime import datetime

from sqlalchemy import Column, Integer, String, BigInteger, inspect, Enum
from sqlalchemy.ext.hybrid import hybrid_property

from .db_session import SqlAlchemyBase


class Params(SqlAlchemyBase):
    __tablename__ = 'params'

    param_id = Column(Integer, primary_key=True, autoincrement=True)
    param_name = Column(String(127), default='')
    param_type = Column(Enum('int', 'float', 'list', 'multilist'))
    question_text = Column(String(511), default='')

    def as_dict(self):
        return {
            key: getattr(self, key)
            for key in inspect(self).mapper.column_attrs.keys()
        }
