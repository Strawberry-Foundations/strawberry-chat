import socket

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = '0.0.0.0'
port = 54545

serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serversocket.bind((host, port))
serversocket.listen()
print("listening")

clientsocket, addr = serversocket.accept()
print("got a connection from %s" % str(addr))

while True:
    msg = input("> ") + "\r\n"
    clientsocket.send(msg.encode('utf-8s'))