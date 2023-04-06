import socket
from multiprocessing import Pool

from connect import receive_connection
from models.base import engine, Base


def con(client_socket: socket.socket) -> socket.socket:
    while (True):
        c, addr = client_socket.accept()
        yield c


if __name__ == "__main__":
    Base.metadata.create_all(engine)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.bind(("0.0.0.0", 12345))
    client_socket.listen(4)
    engine.dispose()

    with Pool(5) as p:
        for _ in p.imap_unordered(receive_connection, con(client_socket)):
            continue
