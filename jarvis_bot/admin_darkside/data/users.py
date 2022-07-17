from datetime import datetime

from sqlalchemy import Column, Integer, String, BigInteger, inspect, DateTime, Float, SmallInteger
from sqlalchemy.ext.hybrid import hybrid_property

from .db_session import SqlAlchemyBase


class Users(SqlAlchemyBase):
    __tablename__ = 'users'

    user_id = Column(BigInteger, primary_key=True)
    create_date = Column(DateTime)
    tg_first_name = Column(String(255))
    tg_last_name = Column(String(255))
    tg_username = Column(String(255))
    is_live = Column(SmallInteger)
    is_block = Column(SmallInteger, default=0)
    balance = Column(Integer, default='')
    city_id = Column(Integer, default='')

    def as_dict(self):
        return {
            key: self.string_start_date if key == 'create_datetime' else getattr(self, key)
            for key in inspect(self).mapper.column_attrs.keys()
        }

    @hybrid_property
    def string_start_date(self):
        return self.create_date.strftime('%d.%m.%Y %H:%M')
