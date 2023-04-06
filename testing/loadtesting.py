import sys
import threading
import socket

def place_order( input_file):
    input = open( input_file, "rb").read()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", 12345))
    s.sendall(input)
    s.close()

def buy_shares():
    print("Buying Share")
    for i in range(1000000):
        t = threading.Thread(target=place_order, args=("resource/buyscriptloadtesting-input.txt"))
        t.start()


def sell_shares():
    print("Sell Share")
    for i in range(1000000):
        t = threading.Thread(target=place_order, args=("resource/sellscriptloadtesting-input.txt"))
        t.start()


if __name__ =="__main__":
    #account creation
    input_file = "resource/accountcreationloadTesting-input.txt"
    input = open(input_file, "rb").read()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", 12345))
    s.sendall(input)
    s.close()

    t1 = threading.Thread(target=buy_shares, args=())
    t2 = threading.Thread(target=sell_shares, args=())

    t1.start()
    t2.start()


