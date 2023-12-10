import socket 

client = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
client.connect(("2a02:908:e941:3080:b2a4:6e86:6dc4:b59a", 9999))

client.send("Hello from client!".encode())
print(client.recv(1024).decode())