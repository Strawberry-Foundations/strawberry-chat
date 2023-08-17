import socket
import threading
import time
import datetime
import sys

BOLD = '\033[1m'
UNDERLINE = '\033[4m'
RESET = '\033[0m'
BLACK = '\033[30m'
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
PURPLE = '\033[35m'
CYAN = '\033[36m'
WHITE = '\033[37m'

version = "0.9.45b"

class Scapi:
    class Bot:
        def __init__(self, username, token, host, port, enableUserInput=False, printReceivedMessagesToTerminal=False):
            self.stbc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.username = username
            self.token = token
            self.host = host
            self.port = port
            self.enableUserInput = enableUserInput
            self.printReceivedMessagesToTerminal = printReceivedMessagesToTerminal
            
            self.logger(f"{GREEN}Starting scapi.bot version {version}", type="info")
            
            self.count = 0
            
            try:
                self.connect()
                
            except: 
                self.logger(f"{RED}Could not connect to server", type="error")
                exit()
        
        def logger(self, message, type):
            if type.lower() == "info":
                print(f"{CYAN + BOLD}{datetime.date.today().strftime('%Y-%m-%d')} {datetime.datetime.now().strftime('%H:%M:%S')}  {BLUE}{type.upper()}   scapi  -->  {RESET}{message}{RESET}")            
            elif type.lower() == "error":
                print(f"{CYAN + BOLD}{datetime.date.today().strftime('%Y-%m-%d')} {datetime.datetime.now().strftime('%H:%M:%S')}  {RED}{type.upper()}  scapi  -->  {RESET}{message}{RESET}")            
            
        
        def flagHandler(self, enableUserInput=False, printReceivedMessagesToTerminal=False):
            self.enableUserInput = enableUserInput
            self.printReceivedMessagesToTerminal = printReceivedMessagesToTerminal

        def send_message(self, message):
            self.stbc_socket.send(message.encode("utf8"))
        
        def send(self):
            threadFlag = True
            def delete_last_line():
                cursorUp = "\x1b[1A"
                eraseLine = "\x1b[2K"
                sys.stdout.write(cursorUp)
                sys.stdout.write(eraseLine)
            
            if self.enableUserInput is True:
                while threadFlag:
                    try:
                        message = input("")
                        delete_last_line()
                        self.stbc_socket.send(message.encode("utf8"))

                    except:
                        print("Message could not be sent")
                        break
        
        def recv_message(self, raw=False):
            global threadFlag
            threadFlag = True
            try:
                while threadFlag:
                    global message
                    message = self.stbc_socket.recv(2048).decode()
                    
                
                    if message:
                        self.count = self.count + 1
                
                        if self.count > 3:
                            self.logger(message, type="info")
                        
                        if raw == False:
                            return message
                        
                        elif raw == True:
                            index = message.find(":")
                            msg_splitted = message[index + 2:]
                            return msg_splitted
                    else:
                        break
                        
                    
                    
            except (KeyboardInterrupt, SystemExit):
                while threadFlag:
                    self.disconnect()
                    threadFlag = False
        
        # def print_messages(self):
        #     while threadFlag:
        #         if message:
                    
            
        def command(self, command_listener, ctx):
            def wrapper():
                message = self.recv_message()
                index = message.find(":")
                part = message[index + 2:]
                
                if part == command_listener:
                    ctx()
                    
            return wrapper
            
        
        def login(self):
            self.stbc_socket.send(self.username.encode("utf8"))
            time.sleep(1)
            self.stbc_socket.send(self.token.encode("utf8"))
            
        def connect(self):
            self.logger(f"{YELLOW}Connecting to {PURPLE}{self.host}:{self.port} {RESET + YELLOW}...", type="info")
            self.stbc_socket.connect((self.host, self.port))
            self.logger(f"{GREEN}Connected", type="info")
            
            
        def disconnect(self):
            self.stbc_socket.close()
        
        def run(self):
            if self.enableUserInput is True:
                self.logger(f"{YELLOW}Flag {GREEN + BOLD}'enableUserInput'{RESET + YELLOW} is enabled", type="info")
                
            if self.printReceivedMessagesToTerminal is True:
                self.logger(f"{YELLOW}Flag {GREEN + BOLD}'printReceivedMessagesToTerminal'{RESET + YELLOW} is enabled", type="info")
                
            time.sleep(0.5)
            
            recvThread = threading.Thread(target=self.recv_message)
            sendThread = threading.Thread(target=self.send)
            # printThread = threading.Thread(target=self.print_messages)
            
            recvThread.start()
            sendThread.start()
            # printThread.start()
            
