from datetime import datetime

import sqlalchemy
from sqlalchemy import Column, Integer, String, BigInteger, inspect, DateTime, Boolean
from sqlalchemy.ext.hybrid import hybrid_property

from .db_session import SqlAlchemyBase


class AdsPhotos(SqlAlchemyBase):
    __tablename__ = 'ads_photos'

    photo_id = sqlalchemy.Column(Integer, primary_key=True, autoincrement=True)
    create_datetime = Column(DateTime)
    ad_id = Column(Integer)
    photo_link = Column(String(1023))

    def as_dict(self):
        return {
            key: (self.string_date if key == 'create_datetime' else getattr(self, key))
            for key in inspect(self).mapper.column_attrs.keys()
        }

    @hybrid_property
    def string_date(self):
        return self.create_datetime
