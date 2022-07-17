from datetime import datetime

from sqlalchemy import Column, Integer, String, BigInteger, inspect
from sqlalchemy.ext.hybrid import hybrid_property

from .db_session import SqlAlchemyBase


class Categories(SqlAlchemyBase):
    __tablename__ = 'categories'

    category_id = Column(Integer, primary_key=True, autoincrement=True)
    category_name = Column(String(127))
    parent_id = Column(Integer)
    tariff_first_price = Column(Integer, default='')
    tariff_second_price = Column(Integer, default='')

    def as_dict(self):
        return {
            key: getattr(self, key)
            for key in inspect(self).mapper.column_attrs.keys()
        }
