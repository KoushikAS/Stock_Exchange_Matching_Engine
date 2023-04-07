import sys
import threading
import socket, time

amt = 1000

def place_order(input_file):
    input = open( input_file, "rb").read()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", 12345))
    s.sendall(input)
    data = s.recv(4096)
    # print(data.decode('utf-8'))
    s.close()

def buy_shares():
    print("Buying Share")
    for i in range(amt):
        place_order("resource/buyscriptloadtesting-input.txt")


def sell_shares():
    print("Sell Share")
    for i in range(amt):
        place_order("resource/sellscriptloadtesting-input.txt")

def query():
    for i in range(amt):
        place_order("resource/queryscriptloadTesting-input.txt")


if __name__ =="__main__":
    #account creation
    input_file = "resource/accountcreationloadTesting-input.txt"
    input = open(input_file, "rb").read()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", 12345))
    s.sendall(input)
    data = s.recv(4096)
    # print(repr(data.decode('utf-8')))
    s.close()

    lst = []
    sT = time.time()
    for i in range(0, 10):
        t1 = threading.Thread(target=buy_shares, args=())
        t2 = threading.Thread(target=sell_shares, args=())
        t3 = threading.Thread(targer=query, args=())

        startTime = time.time()
        t1.start()
        t2.start()
        t3.start()

        t1.join()
        t2.join()
        t3.join()

        endTime = time.time()

        diff = endTime - startTime
        lst.append(diff)

        # print(f'Difference: {diff}')
    eT = time.time()
    print(f'Average time: {sum(lst) / len(lst)}')
    print(f'Avg2: {(eT - sT) / 10}')

