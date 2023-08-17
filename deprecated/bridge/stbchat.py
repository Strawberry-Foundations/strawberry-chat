import socket
import yaml
from yaml import SafeLoader
import asyncio

class ChatClient():        
    def __init__(self):
        self.reload_conf()
        self.stbc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
    def console_out(self, message):
        print(message)
        
    def reload_conf(self):
        with open("config.yml", encoding="utf-8") as config:
            conf = yaml.load(config, Loader=SafeLoader)
        
        self.conf = conf
            
    def pong(self, quote=False):
        self.console_out("PING PONG")
        
        if not quote:
            self.irc_sock.send( bytes("PONG :pingis\n", "UTF-8") )
        else:
            self.irc_sock.send( bytes(f"PONG :{quote}\n", "UTF-8") )
    
    def login(self):
        username = self.conf["stbchat"]["username"]
        password = self.conf["stbchat"]["password"]
        
        if password:
            self.console_out("Logging in with " + password)
            self.send_message("NickServ", f"IDENTIFY {password}")
    
    def send_msg(self, message):
        self.stbc_socket.send(message.encode("utf8"))

    def connect(self):
        self.console_out(f"Connecting to {self.conf['stbchat']['server']['host']}:{self.conf['stbchat']['server']['port']}")
        self.stbc_socket.connect((self.conf['stbchat']['server']['host'], self.conf['stbchat']['server']['port']))
        
        
    async def main_loop(self):
        try:
            while True:
                await asyncio.sleep(0.1)
                message = self.stbc_socket_recv(2048).decode()
        
        except (KeyboardInterrupt, SystemExit):
            self.disconnect()
            
    def loop(self):
        asyncio.run(self.main_loop())