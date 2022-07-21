from datetime import datetime

from sqlalchemy import Column, Integer, String, BigInteger, inspect, DateTime, Float, SmallInteger, Enum
from sqlalchemy.ext.hybrid import hybrid_property

from .db_session import SqlAlchemyBase


class Payments(SqlAlchemyBase):
    __tablename__ = 'payments'

    payment_id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger)
    payment_date = Column(DateTime)
    payment_status = Column(Enum('wait', 'succeeded'))
    payment_amount = Column(Integer)
    system_id = Column(Integer)

    def as_dict(self):
        return {
            key: self.string_start_date if key == 'payment_date' else getattr(self, key)
            for key in inspect(self).mapper.column_attrs.keys()
        }

    @hybrid_property
    def string_start_date(self):

        return self.payment_date
