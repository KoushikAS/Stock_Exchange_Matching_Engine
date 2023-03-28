from sqlalchemy import Column, Integer

from models.base import Base


class Account(Base):
    __tablename__ = 'account'

    id = Column(Integer, primary_key=True)
    balance = Column(Integer)


    def __init__(self, id, balance):
        self.id = id
        self.balance = balance