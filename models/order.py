import enum
from sqlalchemy import Column, Integer, Numeric, ForeignKey, Enum
from sqlalchemy.orm import relationship
from models.base import Base


class OrderType(enum.Enum):
    BUY = 'BUY'
    SELL = 'SELL'


class Order(Base):
    __tablename__ = 'order'

    id = Column(Integer, primary_key=True)

    account_id = Column(Integer, ForeignKey('account.id'))
    account = relationship("Account")

    symbol_id = Column(Integer, ForeignKey('symbol.id'))
    symbol = relationship("Symbol")

    amount = Column(Numeric)
    limit_price = Column(Numeric)
    order_type = Column(Enum(OrderType))

    def __init__(self, account, symbol, amount, limit_price, order_type):
        self.account = account
        self.symbol = symbol
        self.amount = amount
        self.limit_price = limit_price
        self.order_type = order_type
