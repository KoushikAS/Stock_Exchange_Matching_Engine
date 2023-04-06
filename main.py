from models.base import engine, Base, Session
from models.account import Account
from models.symbol import Symbol
from models.position import Position
from models.order import OrderType, Order, OrderStatus
from connect import receive_connection
from multiprocessing import Pool


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

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    p = Pool(processes=4)
    while (True):
        p.map_async(receive_connection, [False, ''])
    # add the ability to schedule from a core pool here
    # receive_connection(True, "test/resource/accountcreation-input.txt")
    # receive_connection(True, "test/resource/buyscript-input.txt")
    # receive_connection(False, None)
    # receive_connection(True, "model_xml.txt")
    # receive_connection(True, "model_xml_2.txt")
    # s = Session()
    # for e in s.query(Account).all():
    #     print("Account: " + str(e.id) + " : " + str(e.balance))
    # s.commit()
    # receive_connection(True, "model_xml_3.txt")
    # receive_connection(True, "model_xml_4.txt")
    # session = Session()
    # for e in session.query(Account).all():
    #     print("Account: " + str(e.id) + " : " + str(e.balance))
    #     # print(e.positions)
    #     # print("_________________________")
    # for entry in session.query(Position).all():
    #     print("Position: " + str(entry.id) + " : " + str(entry.account) + " : " + str(entry.amount))
    # for en in session.query(Symbol).all():
    #     print("Symbol: " + str(en.name))
    # for en in session.query(Order).all():
    #     print("Order: " + str(en.id) + " : " + str(en.account) + " : " + str(en.symbol) + " : " + str(en.amount) + " : " + str(en.order_status))