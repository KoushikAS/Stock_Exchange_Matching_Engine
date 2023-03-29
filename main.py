from models.base import Session, engine, Base
from models.account import Account
from models.symbol import Symbol
from models.position import Position
from models.order import OrderType, Order, OrderStatus
from sqlalchemy import select

'''
Base.metadata.create_all(engine)
session = Session()


sym1 = Symbol("SPY")
sym2 = Symbol("BTC")
sym3 = Symbol("T5asdf")

account1 = Account(123456, 50)
account2 = Account(1234567890, 100)

position1 = Position(sym1, 123.5, account1)
position2 = Position(sym2, 55.5, account1)
position3 = Position(sym3, 123.001, account1)
position4 = Position(sym1, 123, account2)

session.add(sym1)
session.add(sym2)
session.add(sym3)
session.add(account1)
session.add(account2)
session.add(position1)
session.add(position2)
session.add(position3)
session.add(position4)

session.commit()
session.close()


sym1 = session.execute(select(Symbol).where(Symbol.name == "BTC")).first()
account1 = session.execute(select(Account).where(Account.id == 123456)).first()
account2 = session.execute(select(Account).where(Account.id == 1234567890)).first()


order1 = Order(account1[0], sym1[0], 25, 25, OrderType.BUY, OrderStatus.OPEN)
order2 = Order(account1[0], sym1[0], 30, 20, OrderType.BUY, OrderStatus.OPEN)
order3 = Order(account2[0], sym1[0], 25, 30, OrderType.SELL, OrderStatus.OPEN)

session.add(order1)
session.add(order2)
session.add(order3)

session.commit()
session.close()

print("Session committed")

'''