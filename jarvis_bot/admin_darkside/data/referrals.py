from sqlalchemy import Column, Integer, String, BigInteger, inspect


from .db_session import SqlAlchemyBase


class Referrals(SqlAlchemyBase):
    __tablename__ = 'referrals'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user = Column(BigInteger)
    referral = Column(String(127))
    bonus_balance = Column(Integer)
    referred = Column(Integer)
    attached_referrals = Column(String(127))

    def as_dict(self):
        return {
            key: getattr(self, key)
            for key in inspect(self).mapper.column_attrs.keys()
        }
