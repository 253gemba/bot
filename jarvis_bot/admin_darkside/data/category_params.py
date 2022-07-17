from datetime import datetime

from sqlalchemy import Column, Integer, String, BigInteger, inspect, Enum
from sqlalchemy.ext.hybrid import hybrid_property

from .db_session import SqlAlchemyBase


class CategoryParams(SqlAlchemyBase):
    __tablename__ = 'category_params'

    param_id = Column(Integer, primary_key=True, autoincrement=True)
    param_type = Column(Enum('int', 'float', 'list', 'multilist'))
    category_id = Column(Integer)
    is_required = Column(Integer, default=0)
    in_find = Column(Integer, default=0)
    param_name = Column(String(127), default='')
    param_question = Column(String(127), default='')

    def as_dict(self):
        return {
            key: getattr(self, key)
            for key in inspect(self).mapper.column_attrs.keys()
        }
