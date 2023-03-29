import enum
from sqlalchemy import Column, Integer, Numeric, ForeignKey, Enum
from sqlalchemy.orm import relationship
from models.base import Base


class OrderType(enum.Enum):
    BUY = 'BUY'
    SELL = 'SELL'

class OrderStatus(enum.Enum):
    OPEN = 'OPEN'
    CLOSE = 'CLOSE'

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
    order_status = Column(Enum(OrderStatus))

    def __init__(self, account, symbol, amount, limit_price, order_type, order_status):
        self.account = account
        self.symbol = symbol
        self.amount = amount
        self.limit_price = limit_price
        self.order_type = order_type
        self.order_status = order_status
