from models.base import engine, Base
from connect import receive_connection
from multiprocessing import Pool
import socket

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client_socket.bind(("0.0.0.0", 12345))
    client_socket.listen(4)
    p = Pool(processes=4)
    while (True):
        receive_connection(client_socket, False, '')
