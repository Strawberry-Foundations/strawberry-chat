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


class Scapi:
    class Bot:
        def __init__(self, username, token, host, port, prefix, enableUserInput=False, printReceivedMessagesToTerminal=False):
            self.stbc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.username = username
            self.token = token
            self.host = host
            self.port = port
            self.prefix = prefix
            self.enableUserInput = enableUserInput
            self.printReceivedMessagesToTerminal = printReceivedMessagesToTerminal
            
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
        
        def recv_message(self):
            threadFlag = True
            try:
                while threadFlag:
                    global message
                    message = self.stbc_socket.recv(2048).decode()
                    
                    if message:
                        if self.printReceivedMessagesToTerminal == True:
                            self.logger(message, type="info")
                            
                        else:
                            pass
                        
                    else:
                        break
                    
            except (KeyboardInterrupt, SystemExit):
                while threadFlag:
                    self.disconnect()
                    threadFlag = False
        
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
            
            print()
            time.sleep(0.5)
            recvThread = threading.Thread(target=self.recv_message)
            sendThread = threading.Thread(target=self.send)
            recvThread.start()
            sendThread.start()
            
