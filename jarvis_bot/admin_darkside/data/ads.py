from datetime import datetime

import sqlalchemy
from sqlalchemy import Column, Integer, String, BigInteger, inspect, DateTime, Boolean
from sqlalchemy.ext.hybrid import hybrid_property

from .db_session import SqlAlchemyBase


class Ads(SqlAlchemyBase):
    __tablename__ = 'ads'

    ad_id = sqlalchemy.Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer)
    section_id = Column(Integer)
    ad_description = Column(String(1023))
    user_id = Column(BigInteger, default=0)
    ad_price = Column(Integer, default=0)
    tariff_price = Column(Integer, default=0)
    date_close = Column(DateTime)
    is_warning = Column(Boolean)

    def as_dict(self):
        return {
            key: (self.string_date if key == 'date_close' else getattr(self, key))
            for key in inspect(self).mapper.column_attrs.keys()
        }

    @hybrid_property
    def string_date(self):

        return self.date_close
