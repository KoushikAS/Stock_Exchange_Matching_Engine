import socket
import sys
import re

input_file = sys.argv[1]
expected_file = sys.argv[2]

input = open("resource/" + input_file, "rb").read()
expected_output = open("resource/" + expected_file, "rb").read()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("127.0.0.1", 12345))
print(input)
s.sendall(input)
data = s.recv(4096)
s.close()
actual_output = data.decode('utf-8')
actual_output = re.sub(" time=[0-9a-zA-Z:.]+\/>", "/>", actual_output)
if actual_output == expected_output:
    print("Test passed")
else:
    print("Test failed")
    print("Expected: " + str(expected_output))
    print("Actual: " + actual_output)

