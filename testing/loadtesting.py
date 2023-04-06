import sys
import threading
import socket, datetime

def place_order(input_file):
    input = open( input_file, "rb").read()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", 12345))
    s.sendall(input)
    data = s.recv(4096)
    print(data.decode('utf-8'))
    s.close()

def buy_shares():
    print("Buying Share")
    for i in range(10):
        place_order("resource/buyscriptloadtesting-input.txt")


def sell_shares():
    print("Sell Share")
    for i in range(10):
        place_order("resource/sellscriptloadtesting-input.txt")


if __name__ =="__main__":
    #account creation
    input_file = "resource/accountcreationloadTesting-input.txt"
    input = open(input_file, "rb").read()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", 12345))
    s.sendall(input)
    data = s.recv(4096)
    print(repr(data.decode('utf-8')))
    s.close()

    t1 = threading.Thread(target=buy_shares, args=())
    t2 = threading.Thread(target=sell_shares, args=())

    startTime = datetime.datetime.now()
    t1.start()
    t2.start()

    t1.join()
    t2.join()

    endTime = datetime.datetime.now()

    diff = endTime - startTime

    print(f'Difference: {diff}')

