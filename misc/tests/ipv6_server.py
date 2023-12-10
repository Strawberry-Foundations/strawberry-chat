import socket 

server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
server.bind(("2a02:908:e941:3080:b2a4:6e86:6dc4:b59a", 9999))

server.listen()

while True:
    client, addr = server.accept()
    print(client.recv(1024).decode())
    client.send("Hello from Server".encode())