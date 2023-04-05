import socket
import xml.etree.ElementTree as ET
from models.order import OrderType, Order, OrderStatus
from models.account import Account, account_exists
from models.base import Session
from models.symbol import Symbol
from models.position import Position
from models.executed_order import ExecutedOrder
from xml.dom import minidom


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

def get_xml() -> str:
    newline_rec = False
    buffer = ''
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # socket.setblocking(0)
    client_socket.bind(("0.0.0.0", 12345))
    client_socket.listen(5)
    c, addr = client_socket.accept()
    print ("connection accepted")
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
        text = root.createTextNode('Account already exists')
        xml_result.appendChild(text)
    res.appendChild(xml_result)

def create_position(session: Session, entry: ET.Element, symbol: Symbol, root: minidom.Document, res: minidom.Document) -> None:
    for e in entry:
        account_id = e.attrib.get('id')
        amt = int(e.text)
        if session.query(Account).filter(Account.id==account_id).first() is None:
            xml_result = root.createElement('error')
            xml_result.setAttribute('sym', symbol.name)
            xml_result.setAttribute('id', account_id)
            text = root.createTextNode('Account for position does not exists')
            xml_result.appendChild(text)
            res.appendChild(xml_result)
            continue
        
        # sanity check
        if session.query(Position).filter_by(symbol=symbol, account_id=account_id).count() > 1:
            print("Something has gone very wrong, and multiple positions exist for the same sym and account combo")
            raise Exception("Something has gone very wrong, and multiple positions exist for the same sym and account combo")
        
        if session.query(Position).filter_by(symbol=symbol, account_id=account_id).first() is not None:
            # possibly check if there are more than one of this sym and account_id combo (should not be possible)
            session.query(Position).filter_by(symbol=symbol, account_id=account_id).update({"amount": Position.amount + amt})
        else:
        # can there be concurrency issues if multiple requests try to create the same position for an account at the same time?
            newPosition = Position(symbol, amt, session.query(Account).filter(Account.id==account_id).scalar())
            session.add(newPosition)
        xml_result = root.createElement('created')
        xml_result.setAttribute('sym', symbol.name)
        xml_result.setAttribute('id', account_id)
        res.appendChild(xml_result)

def create_order(session: Session, entry: ET.Element, account: Account, root: minidom.Document, res: minidom.Document) -> None:
    sym = entry.attrib.get('sym')
    amt = float(entry.attrib.get('amount'))
    limit = float(entry.attrib.get('limit'))
    cost = amt * limit
    if account.balance < cost:
        # reject the request
        xml_result = root.createElement('error')
        xml_result.setAttribute('sym', sym)
        xml_result.setAttribute('amount', amt)
        xml_result.setAttribute('limit', limit)
        text = root.createTextNode('Insufficient funds in account')
        xml_result.appendChild(text)
        res.appendChild(xml_result)
        return

    account.balance = account.balance - cost # check that works for sell orders
    order_type = None
    if amt < 0:
        order_type = OrderType.SELL
    else:
        order_type = OrderType.BUY
    order_status = OrderStatus.OPEN
    # add a check that the symbol exists that you are trying to create an order for, create it if not
    # check if this account has some of the symbol in its positions actually???
    # check that the amount to sell is < amount owned
    newOrder = Order(session.query(Account).filter(Account.id==account.id).scalar(), session.query(Symbol).filter(Symbol.name==sym).scalar(), amt, limit, order_type, order_status)
    session.add(newOrder)
    xml_result = root.createElement('opened')
    xml_result.setAttribute('id', newOrder.id)
    xml_result.setAttribute('sym', sym)
    xml_result.setAttribute('amount', str(amt))
    xml_result.setAttribute('limit', str(limit))
    res.appendChild(xml_result)

def cancel_order(session: Session, entry: ET.Element, account: Account, root: minidom.Document, res: minidom.Document) -> None:
    result = ''
    id = entry.attrib.get('id')
    order_to_cancel = session.query(Order).filter(Order.id==id).first()
    if order_to_cancel is None:
        print("tried to cancel an order that does not exist")
        return "error: tried to cancel an order that does not exist\n"
    if account.id != order_to_cancel.account.id:
        print("tried to cancel a order that you do not own")
        return "error: tried to cancel a order that you do not own\n"
    
    order_to_cancel.order_status = OrderStatus.CLOSE
    account.balance += float(order_to_cancel.amount) * float(order_to_cancel.limit_price)
    # cancel any order that is open, refund the account, reply with canceled
    return f"Cancelled Order: {order_to_cancel.id} with {order_to_cancel.amount} shares and price: {order_to_cancel.limit_price}\n"

def query_order(session: Session, entry: ET.Element, account: Account, root: minidom.Document, res: minidom.Document) -> None:
    results = ''
    id = entry.attrib.get('id')
    order_to_query = session.query(Order).filter(Order.id==id).first()
    if order_to_query is None:
        print("tried to cancel an order that does not exist")
        return "error: tried to cancel an order that does not exist\n"
    if account.id != order_to_query.account.id:
        print("tried to cancel a order that you do not own")
        return "error: tried to cancel a order that you do not own\n"
    # get this order from the db
    results += f"Order is {order_to_query.order_status} with {order_to_query.amount} shares\n"
    executed = session.query(ExecutedOrder).filter(ExecutedOrder.order==order_to_query)
    for e in executed:
        results += f"Executed {e.executed_amount} at {e.executed_price}, at {e.executed_time}\n"
    return results

def receive_connection(testing: bool, path: str):
    action_xml = ''
    if testing:
        action_xml = get_test_xml(path)
        print(action_xml)
    else:
        action_xml = get_xml()
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

            elif entry.tag == 'symbol':
                sym = entry.attrib.get('sym')
                if session.query(Symbol).filter(Symbol.name==sym).first() is None:
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
                symbol = session2.query(Symbol).filter(Symbol.name==sym).scalar()
                create_position(session2, entry, symbol, root, res)
                session2.commit()
            else:
                raise Exception("Malformatted xml in create")
    elif xml_tree.tag == 'transactions':
        session = Session()
        account_id = xml_tree.attrib.get('id')
        account = session.query(Account).filter(Account.id==account_id).scalar()
        if account is None:
            print("account does not exists error")
            # generate error xml piece
            # need to figure out how to generate an error for each child here
            results_xml += "account error on transactions"
        session.commit()
        for entry in xml_tree:
            ses = Session()
            account = ses.query(Account).filter(Account.id==account_id).with_for_update().scalar()
            if entry.tag == 'order':
                create_order(ses, entry, account, root, res)
            elif entry.tag == 'cancel':
                cancel_order(ses, entry, account, root, res)
            elif entry.tag == 'query':
                query_order(ses, entry, account, root, res)
            else:
                raise Exception("Malformatted xml in transaction")
            ses.commit()
    else:
        raise Exception("Got an XML that did not follow format")
    if testing:
        print(root.toprettyxml(encoding="utf-8").decode())