from datetime import datetime

import sqlalchemy
from sqlalchemy import Column, Integer, String, BigInteger, inspect, DateTime, Boolean
from sqlalchemy.ext.hybrid import hybrid_property

from .db_session import SqlAlchemyBase


class BrandParams(SqlAlchemyBase):
    __tablename__ = 'brand_params'

    brand_param_id = sqlalchemy.Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer)
    brand_id = Column(Integer)
    param_id = Column(Integer)
    option_id = Column(Integer)
    param_position = Column(Integer)

    def as_dict(self):
        return {
            key: (self.string_date if key == 'create_datetime' else getattr(self, key))
            for key in inspect(self).mapper.column_attrs.keys()
        }
