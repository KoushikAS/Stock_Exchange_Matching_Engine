import decimal
import socket
import xml.etree.ElementTree as ET
from xml.dom import minidom

from models.account import Account, account_exists
from models.base import Session
from models.executed_order import ExecutedOrder
from models.order import OrderType, Order, OrderStatus
from models.position import Position
from models.symbol import Symbol


def getOpenOrder(session, sym, order_type, orderBy):
    return session.query(Order) \
        .filter(Order.symbol == sym, Order.order_type == order_type, Order.order_status == OrderStatus.OPEN) \
        .order_by(orderBy, Order.create_time) \
        .with_for_update() \
        .scalar()


def closeOrder(session, order, exchange_qty, exchange_price):
    execute_order = ExecutedOrder(order, exchange_qty, exchange_price)
    session.add(execute_order)

    if abs(order.amount) > exchange_qty:
        if order.amount < 0:
            order.amount += decimal.Decimal(exchange_qty)
        else:
            order.amount -= decimal.Decimal(exchange_qty)
    else:
        order.order_status = OrderStatus.EXECUTE

    session.add(order)


def bestPrice(buy_order, sell_order):
    if buy_order.create_time < sell_order.create_time:
        return buy_order.limit_price
    else:
        return sell_order.limit_price


def addPosition(session, account, symbol, exchange_qty):
    position = session.query(Position) \
        .filter(Position.account == account, Position.symbol == symbol) \
        .with_for_update() \
        .scalar()

    # Create a new position for the first time buyer
    if position is None:
        position = Position(symbol=symbol, amount=exchange_qty, account=account)
    else:
        position.amount += decimal.Decimal(exchange_qty)

    session.add(position)


def matchBuyOrder(session, buy_order, account):
    while True:
        sell_order = getOpenOrder(session, buy_order.symbol, OrderType.SELL, Order.limit_price.asc())
        if not sell_order:
            break

        if buy_order.limit_price < sell_order.limit_price:
            break

        exchange_qty = min(buy_order.amount, abs(sell_order.amount))
        exchange_price = bestPrice(buy_order, sell_order)

        closeOrder(session, buy_order, exchange_qty, exchange_price)
        closeOrder(session, sell_order, exchange_qty, exchange_price)

        addPosition(session, buy_order.account, buy_order.symbol, exchange_qty)

        expected_price_to_pay_for_exchange_qty = float(buy_order.limit_price) * float(exchange_qty)
        actual_price_to_paid_for_exchange_qty = float(exchange_price) * float(exchange_qty)

        if actual_price_to_paid_for_exchange_qty < expected_price_to_pay_for_exchange_qty:
            diff = float(expected_price_to_pay_for_exchange_qty) - float(actual_price_to_paid_for_exchange_qty)
            account.balance += float(diff)

        if buy_order.order_status == OrderStatus.EXECUTE:
            break


def matchSellOrder(session, sell_order, account):
    while True:
        buy_order = getOpenOrder(session, sell_order.symbol, OrderType.BUY, Order.limit_price.desc())

        if not buy_order:
            break

        if buy_order.limit_price < sell_order.limit_price:
            break

        exchange_qty = min(buy_order.amount, abs(sell_order.amount))
        exchange_price = bestPrice(buy_order, sell_order)

        closeOrder(session, buy_order, exchange_qty, exchange_price)
        closeOrder(session, sell_order, exchange_qty, exchange_price)

        addPosition(session, buy_order.account, buy_order.symbol, exchange_qty)

        price_earned_by_seller = float(exchange_qty) * float(exchange_price)
        account.balance += float(price_earned_by_seller)

        if sell_order.order_status == OrderStatus.CANCEL:
            break


def get_test_xml(path: str) -> str:
    i = 0
    action_xml = ''
    f = open(path, "r")
    for line in f:
        if i == 0:
            xml_size = int(line.strip())
        else:
            action_xml += line
        i += 1
    return action_xml


def get_xml(c: socket.socket) -> str:
    newline_rec = False
    buffer = ''
    while not newline_rec:
        xml_size_bytes = c.recv(1)
        xml_size_str = xml_size_bytes.decode()
        if xml_size_str == '\n':
            newline_rec = True
        else:
            buffer += xml_size_str
    xml_size = int(buffer)
    action_xml = c.recv(xml_size)
    return action_xml


def create_account(session: Session, entry: ET.Element, root: minidom.Document, res: minidom.Document) -> None:
    # can there be concurrency issues if multiple requests try to create the same account at the same time?
    id = entry.attrib.get('id')
    balance = entry.attrib.get('balance')
    if not account_exists(session, id):
        newAcc = Account(id=id, balance=balance)
        session.add(newAcc)
        session.commit()
        xml_result = root.createElement('created')
        xml_result.setAttribute('id', id)
    else:
        xml_result = root.createElement('error')
        xml_result.setAttribute('id', id)
        text = root.createTextNode("Account already exists")
        xml_result.appendChild(text)
    res.appendChild(xml_result)


def create_position(session: Session, entry: ET.Element, symbol: Symbol, root: minidom.Document,
                    res: minidom.Document) -> None:
    for e in entry:
        account_id = e.attrib.get('id')
        amt = int(e.text)
        if session.query(Account).filter(Account.id == account_id).first() is None:
            xml_result = root.createElement('error')
            xml_result.setAttribute('sym', symbol.name)
            xml_result.setAttribute('id', account_id)
            text = root.createTextNode("Account for position does not exists")
            xml_result.appendChild(text)
            res.appendChild(xml_result)
            continue

        # sanity check
        if session.query(Position).filter_by(symbol=symbol, account_id=account_id).count() > 1:
            print("Something has gone very wrong, and multiple positions exist for the same sym and account combo")
            raise Exception(
                "Something has gone very wrong, and multiple positions exist for the same sym and account combo")

        if session.query(Position).filter_by(symbol=symbol, account_id=account_id).first() is not None:
            # possibly check if there are more than one of this sym and account_id combo (should not be possible)
            session.query(Position).filter_by(symbol=symbol, account_id=account_id).update(
                {'amount': Position.amount + amt})
        else:
            # can there be concurrency issues if multiple requests try to create the same position for an account at the same time?
            newPosition = Position(symbol, amt, session.query(Account).filter(Account.id == account_id).scalar())
            session.add(newPosition)
        xml_result = root.createElement('created')
        xml_result.setAttribute('sym', symbol.name)
        xml_result.setAttribute('id', account_id)
        res.appendChild(xml_result)


def create_order(session: Session, entry: ET.Element, account: Account, root: minidom.Document,
                 res: minidom.Document) -> None:
    sym = entry.attrib.get('sym')
    amt = float(entry.attrib.get('amount'))
    limit = float(entry.attrib.get('limit'))
    cost = amt * limit
    if account.balance < cost:
        # reject the request
        xml_result = root.createElement('error')
        xml_result.setAttribute('sym', sym)
        xml_result.setAttribute('amount', str(amt))
        xml_result.setAttribute('limit', str(limit))
        text = root.createTextNode('Insufficient funds in account')
        xml_result.appendChild(text)
        res.appendChild(xml_result)
        return

    if amt < 0:
        order_type = OrderType.SELL
    else:
        order_type = OrderType.BUY

    account_entity = session.query(Account).filter(Account.id == account.id).scalar()
    symbol_entity = session.query(Symbol).filter(Symbol.name == sym).scalar()
    if order_type == OrderType.SELL:
        position = session.query(Position) \
            .filter(Position.symbol == symbol_entity, Position.account == account_entity) \
            .with_for_update().scalar()
        if position is None or position.amount < amt:
            # reject the request
            xml_result = root.createElement('error')
            xml_result.setAttribute('sym', sym)
            xml_result.setAttribute('amount', str(amt))
            xml_result.setAttribute('limit', str(limit))
            text = root.createTextNode('Insufficient shares in account')
            xml_result.appendChild(text)
            res.appendChild(xml_result)
            return

        position.amount -= decimal.Decimal(abs(amt))
        session.add(position)

    account.balance = account.balance - cost  # check that works for sell orders

    order_status = OrderStatus.OPEN
    # add a check that the symbol exists that you are trying to create an order for, create it if not
    # check if this account has some of the symbol in its positions actually???
    # check that the amount to sell is < amount owned
    newOrder = Order(account_entity, symbol_entity, amt, limit, order_type, order_status)
    session.add(newOrder)
    if order_type == OrderType.BUY:
        matchBuyOrder(session, newOrder, account)
    else:
        matchSellOrder(session, newOrder, account)
    xml_result = root.createElement('opened')
    xml_result.setAttribute('id', str(newOrder.id))
    xml_result.setAttribute('sym', sym)
    xml_result.setAttribute('amount', str(amt))
    xml_result.setAttribute('limit', str(limit))
    res.appendChild(xml_result)


def cancel_order(session: Session, entry: ET.Element, account: Account, root: minidom.Document,
                 res: minidom.Document) -> None:
    id = entry.attrib.get('id')
    order_to_cancel = session.query(Order).filter_by(id=id, order_status=OrderStatus.OPEN).with_for_update().scalar()
    if order_to_cancel is None:
        xml_result = root.createElement('error')
        xml_result.setAttribute('id', id)
        text = root.createTextNode('Order to cancel does not exist')
        xml_result.appendChild(text)
        res.appendChild(xml_result)
        return
    if account.id != order_to_cancel.account.id:
        xml_result = root.createElement('error')
        xml_result.setAttribute('id', id)
        text = root.createTextNode('Attempted to cancel an order account given does not own, not allowed')
        xml_result.appendChild(text)
        res.appendChild(xml_result)
        return

    order_to_cancel.order_status = OrderStatus.CANCEL
    account.balance = account.balance + (float(order_to_cancel.amount) * float(order_to_cancel.limit_price))
    if order_to_cancel.order_type == OrderType.SELL:
        # Adding back the position to the Seller
        addPosition(session, account, order_to_cancel.symbol, abs(order_to_cancel.amount))

    # cancel any order that is open, refund the account, reply with canceled
    xml_result = root.createElement('canceled')
    xml_result.setAttribute('id', id)
    child1 = root.createElement('canceled')
    child1.setAttribute('shares', str(order_to_cancel.amount))
    child1.setAttribute('time',
                        str(order_to_cancel.create_time))  # is this the right return time? or should it be the current time of cancel request
    xml_result.appendChild(child1)
    executed = session.query(ExecutedOrder).filter_by(order=order_to_cancel)
    for e in executed:
        c = root.createElement('executed')
        c.setAttribute('shares', str(e.executed_amount))
        c.setAttribute('price', str(e.executed_price))
        c.setAttribute('time', str(e.executed_time))
        xml_result.appendChild(c)
    res.appendChild(xml_result)


def query_order(session: Session, entry: ET.Element, account: Account, root: minidom.Document,
                res: minidom.Document) -> None:
    id = entry.attrib.get('id')
    order_to_query = session.query(Order).filter_by(id=id).first()
    if order_to_query is None:
        xml_result = root.createElement('error')
        xml_result.setAttribute('id', id)
        text = root.createTextNode('Order to query does not exist')
        xml_result.appendChild(text)
        res.appendChild(xml_result)
        return
    if account.id != order_to_query.account.id:
        xml_result = root.createElement('error')
        xml_result.setAttribute('id', id)
        text = root.createTextNode('Attempted to query an order account given does not own, not allowed')
        xml_result.appendChild(text)
        res.appendChild(xml_result)
        return
    # get this order from the db
    xml_result = root.createElement('status')
    xml_result.setAttribute('id', id)
    if order_to_query.order_status is OrderStatus.OPEN:
        child1 = root.createElement('open')
        child1.setAttribute('shares', str(order_to_query.amount))
    elif order_to_query.order_status is OrderStatus.CANCEL:
        child1 = root.createElement('canceled')
        child1.setAttribute('shares', str(order_to_query.amount))
        child1.setAttribute('time', str(order_to_query.create_time))
    else:
        xml_result = root.createElement('error')
        xml_result.setAttribute('id', id)
        text = root.createTextNode('Order finished executing and was closed')
        xml_result.appendChild(text)
        res.appendChild(xml_result)
        return
    xml_result.appendChild(child1)
    executed = session.query(ExecutedOrder).filter_by(order=order_to_query)
    for e in executed:
        c = root.createElement('executed')
        c.setAttribute('shares', str(e.executed_amount))
        c.setAttribute('price', str(e.executed_price))
        c.setAttribute('time', str(e.executed_time))
        xml_result.appendChild(c)
    res.appendChild(xml_result)


def receive_connection(c: socket.socket):
    with c:
        action_xml = get_xml(c)
        print(action_xml)
        try:
            xml_tree = ET.fromstring(action_xml)
        except:
            print("XML was malformatted")
            return
        results_xml = ''
        root = minidom.Document()
        res = root.createElement('results')
        root.appendChild(res)

        if xml_tree.tag == 'create':
            for entry in xml_tree:
                session = Session()
                if entry.tag == 'account':
                    try:
                        create_account(session, entry, root, res)
                    except:
                        xml_result = root.createElement('error')
                        xml_result.setAttribute('id', id)
                        text = root.createTextNode('Account already exists')
                        xml_result.appendChild(text)
                        res.appendChild(xml_result)
                    session.commit()

                elif entry.tag == 'symbol':
                    sym = entry.attrib.get('sym')
                    if session.query(Symbol).filter(Symbol.name == sym).first() is None:
                        newSymbol = Symbol(sym)
                        session.add(newSymbol)
                        # xml_child = root.createElement('created')
                        # xml_child.setAttribute('id', id)
                        # res.appendChild(xml_child)
                    try:
                        session.commit()
                    except:
                        print("Symbol was created during the creation of the same symbol (!should never happen!)")
                        pass

                    session2 = Session()
                    # should it be checked here if only one symbol exists with that name?
                    symbol = session2.query(Symbol).filter(Symbol.name == sym).scalar()
                    create_position(session2, entry, symbol, root, res)
                    session2.commit()
                else:
                    session.commit()
                    raise Exception("Malformatted xml in create")
                session.close()
        elif xml_tree.tag == 'transactions':
            session = Session()
            account_id = xml_tree.attrib.get('id')
            print("ACCCccc")
            print(account_id)
            account = session.query(Account).filter(Account.id == account_id).scalar()
            if account is None:
                print("account does not exists error")
                # generate error xml piece
                # need to figure out how to generate an error for each child here
                results_xml += "account error on transactions"
            session.commit()
            session.close()
            for entry in xml_tree:
                ses = Session()
                print("I just made a new session")
                account = ses.query(Account).filter(Account.id == account_id).with_for_update().scalar()
                if entry.tag == 'order':
                    print(f"ID: {account_id} into create_order")
                    create_order(ses, entry, account, root, res)
                    print(f"ID: {account_id} out of create_order")
                elif entry.tag == 'cancel':
                    cancel_order(ses, entry, account, root, res)
                elif entry.tag == 'query':
                    query_order(ses, entry, account, root, res)
                else:
                    raise Exception("Malformatted xml in transaction")
                ses.commit()
                ses.close()
        else:
            raise Exception("Got an XML that did not follow format")

        c.send(root.toprettyxml(encoding="utf-8"))
        c.close()
