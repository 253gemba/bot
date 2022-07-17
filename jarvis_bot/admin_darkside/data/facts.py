from sqlalchemy import Column, Integer, String, inspect
from .db_session import SqlAlchemyBase


class Facts(SqlAlchemyBase):
    __tablename__ = 'dark_facts'

    fact_id = Column(Integer, primary_key=True, autoincrement=True)
    fact_text = Column(String(2048), default='')
    fact_photo = Column(String(512), default='')

    def as_dict(self):
        return {
            key:  getattr(self, key)
            for key in inspect(self).mapper.column_attrs.keys()
        }