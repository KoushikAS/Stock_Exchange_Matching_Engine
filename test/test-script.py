import socket
import sys

input_file = sys.argv[1]
expected_file = sys.argv[2]

input = open("resource/" + input_file, "r").read()
expected_output = open("resource/" + expected_file, "r").read()



host = socket.gethostname()
port = 12345                   # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
s.sendall(input)
data = s.recv(4096)
s.close()
actual_output = data.decode('utf-8')

f2 = f = open("resource/accountcreationerror-input.txt", "r")

if actual_output == expected_output:
    print("Account creation Test passed")
else:
    print("Account creation Test failed")
    print("Expected: "+ expected_output)
    print("Actual: " + actual_output)

