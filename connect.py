import socket, time
from random import randint 
import xml.etree.ElementTree as ET
from sqlalchemy import select
from models.order import OrderType, Order, OrderStatus
from models.account import Account, account_exists
from models.base import Session
from models.symbol import Symbol


def receive_connection():
    testing = True
    xml_size = 0
    action_xml = ''
    if testing:
        i = 0
        f = open("model_xml.txt", "r")
        for line in f:
            if i == 0:
                xml_size = int(line.strip())
            else:
                action_xml += line
            i += 1
    else:
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
    print(action_xml)
    try:
        xml_tree = ET.fromstring(action_xml)
    except:
        print("XML was malformatted")
        return
    if xml_tree.tag == 'create':
        for entry in xml_tree:
            session = Session()
            if entry.tag == 'account':
                id = entry.attrib.get('id')
                balance = entry.attrib.get('balance')
                if not account_exists(session, id):
                    newAcc = Account(id=id, balance=balance)
                    session.add(newAcc)
                    session.commit()
                    print(f"new acc: {id} added")
                    # generate response xml piece
                else:
                    print("account already exists error")
                    # generate error xml piece
            elif entry.tag == 'symbol':
                print("got a symbol tag")
                # create a symbol for the given account
                # error if the given account does not exist
                sym = entry.attrib.get('sym')
                for e in entry:
                    account = e.attrib.get('id')
                    amt = int(e.text)
                    print(sym)
                    if select(Symbol).where(Symbol.c.name == sym) == None:
                        pass
                    # TODO: Get matching account for ^, either add a position or add to position amt
                    if select(Account).where(Account.c.id == account) != None:
                        pass    
                pass
            else:
                raise Exception("Malformatted xml in create")
        # Call a response function to generate the response xml and send on socket connected to 12345
        # returns either an error xml or results xml for each transaction
        return
    elif xml_tree.tag == 'transactions':
        # can process in any order -> threads here?
        account = xml_tree.attrib.get('id')
        for entry in xml_tree:
            if entry.tag == 'order':
                sym = entry.attrib.get('sym')
                amt = entry.attrib.get('amount')
                limit = entry.attrib.get('limit')
                # generate a unique id
                order_id = randint(100, 1000000000)
                # check in the database if an order exists with this id, if it does, re-pick
                order_type = None
                if amt < 0:
                    order_type = OrderType.SELL
                else:
                    order_type = OrderType.BUY
                order_status = OrderStatus.OPEN
                print(account)
                pass
            elif entry.tag == 'cancel':
                id = entry.attrib.get('id')
                # get this order from the db
                pass
            elif entry.tag == 'query':
                id = entry.attrib.get('id')
                # cancel any order that is open, refund the account, reply with canceled
                pass
            else:
                raise Exception("Malformatted xml in transaction")
    else:
        raise Exception("Got an XML that did not follow format")