from datetime import datetime

import sqlalchemy
from sqlalchemy import Column, Integer, String, BigInteger, inspect, DateTime, Boolean
from sqlalchemy.ext.hybrid import hybrid_property

from .db_session import SqlAlchemyBase


class BrandsPhotos(SqlAlchemyBase):
    __tablename__ = 'brands_photos'

    bp_id = sqlalchemy.Column(Integer, primary_key=True, autoincrement=True)
    brand_id = Column(Integer)
    color_id = Column(Integer)
    photo_link = Column(String(1023))

    def as_dict(self):
        return {
            key: (self.string_date if key == 'create_datetime' else getattr(self, key))
            for key in inspect(self).mapper.column_attrs.keys()
        }
