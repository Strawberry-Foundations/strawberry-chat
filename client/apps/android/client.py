import socket

class MySocket:
    def __init__(self,host="localhost",port=54545):
        self.sock = socket.socket()
        self.sock.connect((host, port))


    def get_data(self):
        return self.sock.recv(2048)