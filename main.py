from models.base import engine, Base
from connect import receive_connection
from multiprocessing import Pool
import socket



if __name__ == "__main__":
    Base.metadata.create_all(engine)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # socket.setblocking(0)
    client_socket.bind(("0.0.0.0", 12345))
    client_socket.listen(4)
    p = Pool(processes=4)
    while (True):
        # p.map_async(receive_connection, [False, ''])
        receive_connection(client_socket, False, '')
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
