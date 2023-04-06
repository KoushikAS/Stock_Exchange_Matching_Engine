from sqlalchemy import Column, Integer, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from models.base import Base
import time


class ExecutedOrder(Base):
    __tablename__ = 'executed_order'

    id = Column(Integer, primary_key=True)

    order_id = Column(Integer, ForeignKey('order.id'))
    order = relationship("Order")

    executed_amount = Column(Numeric)
    executed_price = Column(Numeric)
    executed_time = Column(Integer, default=int(time.time()))

    def __init__(self, order, executed_amount, executed_price):
        self.order = order
        self.executed_amount = executed_amount
        self.executed_price = executed_price
