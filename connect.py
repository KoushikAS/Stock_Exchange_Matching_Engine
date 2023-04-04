import socket, time
from random import randint 
import xml.etree.ElementTree as ET
from sqlalchemy import select
from models.order import OrderType, Order, OrderStatus
from models.account import Account, account_exists
from models.base import Session
from models.symbol import Symbol
from models.position import Position
from models.executed_order import ExecutedOrder


def get_test_xml():
    i = 0
    action_xml = ''
    f = open("model_xml.txt", "r")
    for line in f:
        if i == 0:
            xml_size = int(line.strip())
        else:
            action_xml += line
        i += 1
    return action_xml

def get_xml():
    newline_rec = False
    buffer = ''
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # socket.setblocking(0)
    client_socket.bind(('localhost', 12345))
    client_socket.listen(5)
    c, addr = client_socket.accept()
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

# def generate_results(tag, ):
#     results_xml = ''

def create_account(session: Session, entry: ET.Element) -> str:
    id = entry.attrib.get('id')
    balance = entry.attrib.get('balance')
    if not account_exists(session, id):
        newAcc = Account(id=id, balance=balance)
        session.add(newAcc)
        session.commit()
        # generate response xml piece
        return 'result\n'
    else:
        print("account already exists error")
        # generate error xml piece
        return 'error\n'

def create_position(session: Session, entry: ET.Element, symbol: Symbol) -> str:
    results = ''
    for e in entry:
        account = e.attrib.get('id')
        amt = int(e.text)
        if session.query(Account).filter(Account.id==account).first() is None:
            print("account does not exists error")
            results += 'account error\n'
            continue
        pos = session.query(Position).filter(Position.symbol==symbol, Position.account_id==account).first()
        if pos is not None:
            pos.amount += amt
        else:
            newPosition = Position(symbol, amt, session.query(Account).filter(Account.id==account).one())
            session.add(newPosition)
        results += "successfully added\n"
    return results

def create_order(session: Session, entry: ET.Element, account: Account) -> str:
    sym = entry.attrib.get('sym')
    amt = entry.attrib.get('amount')
    limit = entry.attrib.get('limit')
    cost = amt * limit
    if account.balance < cost:
        # reject the request
        return "order fail due to insufficient funds\n"
    account.balance -= cost # check that works for sell orders
    order_type = None
    if amt < 0:
        order_type = OrderType.SELL
    else:
        order_type = OrderType.BUY
    order_status = OrderStatus.OPEN
    newOrder = Order(session.query(Account).filter(Account.id==account).one(), session.query(Symbol).filter(Symbol.name==sym).one(), amt, limit, order_type, order_status)
    session.add(newOrder)
    return 'success\n'

def cancel_order(session: Session, entry: ET.Element, account: Account) -> str:
    id = entry.attrib.get('id')
    order_to_cancel = session.query(Order).filter(Order.id==id).first()
    if order_to_cancel is None:
        print("tried to cancel an order that does not exist")
        return "error: tried to cancel an order that does not exist\n"
    if account != order_to_cancel.account:
        print("tried to cancel a order that you do not own")
        return "error: tried to cancel a order that you do not own\n"
    
    order_to_cancel.order_status = OrderStatus.CLOSE
    account.balance += order_to_cancel.amt * order_to_cancel.limit
    # cancel any order that is open, refund the account, reply with canceled

def query_order(session: Session, entry: ET.Element, account: Account) -> str:
    results = ''
    id = entry.attrib.get('id')
    order_to_query = session.query(Order).filter(Order.id==id).first()
    if order_to_query is None:
        print("tried to cancel an order that does not exist")
        return "error: tried to cancel an order that does not exist\n"
    if account != order_to_query.account:
        print("tried to cancel a order that you do not own")
        return "error: tried to cancel a order that you do not own\n"
    # get this order from the db
    results += f"Order is {order_to_query.order_status} with {order_to_query.amount} shares\n"
    executed = session.query(ExecutedOrder).filter(ExecutedOrder.order==order_to_query)
    for e in executed:
        results += f"Executed {e.executed_amount} at {e.executed_price}, at {e.executed_time}\n"

def receive_connection(testing: bool):
    action_xml = ''
    if testing:
        action_xml = get_test_xml()
    else:
        action_xml = get_xml()
    print(action_xml)
    try:
        xml_tree = ET.fromstring(action_xml)
    except:
        print("XML was malformatted")
        return
    results_xml = ''

    if xml_tree.tag == 'create':
        for entry in xml_tree:
            session = Session()
            if entry.tag == 'account':
                results_xml += create_account(session, entry)
            elif entry.tag == 'symbol':
                sym = entry.attrib.get('sym')
                if session.query(Symbol).filter(Symbol.name==sym).first() is None:
                    newSymbol = Symbol(sym)
                    session.add(newSymbol)
                symbol = session.query(Symbol).filter(Symbol.name==sym).one()
                session.commit()

                session2 = Session()
                results_xml += create_position(session2, entry, symbol)
                session2.commit()
            else:
                raise Exception("Malformatted xml in create")
        # Call a response function to generate the response xml and send on socket connected to 12345
        # returns either an error xml or results xml for each transaction
        return
    elif xml_tree.tag == 'transactions':
        session = Session()
        account_id = xml_tree.attrib.get('id')
        account = session.query(Account).filter(Account.id==account_id).first()
        if account is None:
            print("account does not exists error")
            # generate error xml piece
            results_xml += "account error on transactions"
        session.commit()
        for entry in xml_tree:
            ses = Session()
            if entry.tag == 'order':
                results_xml += create_order(ses, entry, account)
            elif entry.tag == 'cancel':
                results_xml += cancel_order(ses, entry, account)
            elif entry.tag == 'query':
                results_xml += query_order(ses, entry, account)
            else:
                raise Exception("Malformatted xml in transaction")
            ses.commit()
    else:
        raise Exception("Got an XML that did not follow format")