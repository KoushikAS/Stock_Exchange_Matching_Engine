import socket
import sys
import re

input_file = sys.argv[1]
expected_file = sys.argv[2]

input = open("resource/" + input_file, "rb").read()
expected_output = open("resource/" + expected_file, "r").read()
expected_output = re.sub("\n", "", expected_output)
expected_output = re.sub("\t", "", expected_output)
expected_output = re.sub(" ", "", expected_output)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("127.0.0.1", 12345))
s.sendall(input)
data = s.recv(4096)
s.close()
actual_output = data.decode('utf-8')
actual_output = re.sub("time=\"(\d+)\"", "", actual_output)
actual_output = re.sub("\n", "", actual_output)
actual_output = re.sub("\t", "", actual_output)
actual_output = re.sub(" ", "", actual_output)
if repr(actual_output.strip()) == repr(expected_output.strip()):
    print("Success: Test passed")
else:
    print("Test failed" )
    print("Expected:" + repr(expected_output))
    print("Actual:" + repr(actual_output))

