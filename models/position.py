from sqlalchemy import Column, Integer, Numeric, ForeignKey
from sqlalchemy.orm import relationship, backref
from models.base import Base


class Position(Base):
    __tablename__ = 'position'

    id = Column(Integer, primary_key=True)

    symbol_id = Column(Integer, ForeignKey('symbol.id'))
    symbol = relationship("Symbol")

    amount = Column(Numeric)

    account_id = Column(Integer, ForeignKey('account.id'))
    account = relationship("Account", back_populates= "positions")

    def __init__(self, symbol, amount, account):
        self.symbol = symbol
        self.amount = amount
        self.account = account

def create_position(session, symbol_id, amount, account)
