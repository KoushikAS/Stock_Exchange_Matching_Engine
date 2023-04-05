import socket

print("Are you here")
newline_rec = False
buffer = ''
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# socket.setblocking(0)
print("Did you create socket")
client_socket.bind(('localhost', 12345))
print("Did you bind the socket")
client_socket.listen()
print("Are you listening")
c, addr = client_socket.accept()
print("got a new request addr " + addr)

print (c)