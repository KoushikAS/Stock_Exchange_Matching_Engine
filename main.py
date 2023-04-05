from models.base import Session, engine, Base
from models.account import Account
from models.symbol import Symbol
from models.position import Position
from models.order import OrderType, Order, OrderStatus
from sqlalchemy import select


def getOpenOrder(session, sym, order_type, orderBy):
    return session.query(Order).where(Order.symbol == sym) \
        .where(Order.order_type == order_type) \
        .where(Order.order_status == OrderStatus.OPEN) \
        .order_by(orderBy, Order.create_time) \
        .first()


def closeOrder(session, order, exchange_qty, exchange_price):
    if order.amount > exchange_qty:
        order.amount -= exchange_qty
        closed_order = Order(order.account, order.symbol, exchange_qty, exchange_price,
                             order.order_type, OrderStatus.CLOSE)
        session.add(closed_order)
    else:
        order.order_status = OrderStatus.CLOSE
        order.limit_price = exchange_price

    session.add(order)


def bestPrice(buy_order, sell_order):
    if buy_order.create_time < sell_order.create_time:
        return buy_order.limit_price
    else:
        return sell_order.limit_price


def matchOrder(session, sym):
    while True:
        buy_order = getOpenOrder(session, sym, OrderType.BUY, Order.limit_price.desc())
        sell_order = getOpenOrder(session, sym, OrderType.SELL, Order.limit_price.asc())

        if not buy_order or not sell_order:
            break

        if buy_order.limit_price < sell_order.limit_price:
            break

        exchange_qty = min(buy_order.amount, sell_order.amount)
        exchange_price = bestPrice(buy_order, sell_order)

        closeOrder(session, buy_order, exchange_qty, exchange_price)
        closeOrder(session, sell_order, exchange_qty, exchange_price)

        session.commit()


Base.metadata.create_all(engine)
session = Session()

sym1 = session.execute(select(Symbol).where(Symbol.name == "BTC")).first()

'''
matchOrder(session, sym1[0])


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


order1 = Order(account1[0], sym1[0], 500, 128, OrderType.SELL, OrderStatus.OPEN)
order2 = Order(account2[0], sym1[0], 200, 140, OrderType.SELL, OrderStatus.OPEN)
order3 = Order(account2[0], sym1[0], 400, 125, OrderType.BUY, OrderStatus.OPEN)
order4 = Order(account2[0], sym1[0], 400, 124, OrderType.SELL, OrderStatus.OPEN)

session.add(order1)
session.add(order2)
session.add(order3)
session.add(order4)

session.commit()
session.close()
'''
print("Session committed")
