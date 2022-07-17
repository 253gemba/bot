from datetime import datetime

from sqlalchemy import Column, Integer, String, BigInteger, inspect, DateTime, Float, SmallInteger, Enum
from sqlalchemy.ext.hybrid import hybrid_property

from .db_session import SqlAlchemyBase


class Mailing(SqlAlchemyBase):
    __tablename__ = 'mailing'

    mail_id = Column(Integer, primary_key=True)
    mail_datetime = Column(DateTime)
    mail_text = Column(String(4000))
    mail_additional_ident = Column(String(255))
    city_id = Column(String(16))
    is_sent = Column(Integer, default=0)

    def as_dict(self):
        return {
            key: self.string_start_date if key == 'mail_datetime' else getattr(self, key)
            for key in inspect(self).mapper.column_attrs.keys()
        }

    @hybrid_property
    def string_start_date(self):
        return self.mail_datetime
