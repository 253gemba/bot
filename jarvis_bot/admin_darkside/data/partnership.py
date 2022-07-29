from sqlalchemy import Column, Integer, DateTime, inspect, Enum, func, BigInteger, String

from .db_session import SqlAlchemyBase


class PartnershipUsers(SqlAlchemyBase):
    __tablename__ = 'partnership'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger)
    created_date = Column(DateTime(timezone=True), server_default=func.now())

    def as_dict(self):
        return {
            key: getattr(self, key)
            for key in inspect(self).mapper.column_attrs.keys()
        }
