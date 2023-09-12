import socket
import threading
import time
import datetime
import sys
import re
from enum import Enum

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

version = "0.10.0+u1"

class Scapi:
    class LogLevel:
        INFO = "INFO"
        ERROR = "ERROR"
        MSG = "MSG"
        MESSAGE = "MSG"
            
    class PermissionLevel(Enum):
        MEMBER = 0
        ADMIN = 1
    
    class Bot:    
        def __init__(self, username, token, host, port, enableUserInput=False, printReceivedMessagesToTerminal=False):
            self.stbc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.username = username
            self.token = token
            self.host = host
            self.port = port
            self.enableUserInput = enableUserInput
            self.printReceivedMessagesToTerminal = printReceivedMessagesToTerminal
            
            self.logger(f"{GREEN}Starting scapi.bot version {version}", type=Scapi.LogLevel.INFO)
            
            self.count = 0
            self.log_msg = f"{CYAN + BOLD}{datetime.date.today().strftime('%Y-%m-%d')} {datetime.datetime.now().strftime('%H:%M:%S')}  {BLUE}INFO   scapi  -->  {RESET}"
            
            try:
                self.connect()
                
            except: 
                self.logger(f"{RED}Could not connect to server", type=Scapi.LogLevel.error)
                exit()

        def logger(self, message, type):
            if type.lower() == "info":
                print(f"{CYAN + BOLD}{datetime.date.today().strftime('%Y-%m-%d')} {datetime.datetime.now().strftime('%H:%M:%S')}  {BLUE}{type.upper()}{BLUE}   scapi  -->  {RESET}{message}{RESET}")            
            elif type.lower() == "error":
                print(f"{CYAN + BOLD}{datetime.date.today().strftime('%Y-%m-%d')} {datetime.datetime.now().strftime('%H:%M:%S')}  {RED}{type.upper()}{BLUE}  scapi  -->  {RESET}{message}{RESET}")            
            elif type.lower() == "msg":
                print(f"{CYAN + BOLD}{datetime.date.today().strftime('%Y-%m-%d')} {datetime.datetime.now().strftime('%H:%M:%S')}  {GREEN}{type.upper()}{BLUE}    scapi  -->  {RESET}{message}{RESET}")            
            
        
        def flagHandler(self, enableUserInput=False, printReceivedMessagesToTerminal=False):
            self.enableUserInput = enableUserInput
            self.printReceivedMessagesToTerminal = printReceivedMessagesToTerminal

        def send_message(self, message):
            self.stbc_socket.send(message.encode("utf8"))
            
        def escape_ansi(self, line):
            ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
            return ansi_escape.sub('', line)
        
        
        def get_username_by_msg(self, message):
            username = message.split(":")[0]
            username = username.replace("[", ""
                                       ).replace("]", ""
                                       ).replace("👑", ""
                                       ).replace("😎", ""
                                       ).replace("🔥", ""
                                       ).replace("🫐", ""
                                       ).replace("🤖", ""
                                       ).replace("💪", ""
                                       ).replace("👍", ""
                                       ).replace("🤡", ""
                                       ).replace("😈", ""
                                       ).replace("🤝", ""
                                       ).replace("👋", ""
                                       ).replace("😌", ""
                                       ).replace("🍓", ""
                                       ).replace("💫", ""
                                       )
            
            uname_index = username.find("(")
            raw_username = username[uname_index + 1:]
            raw_username = raw_username.replace(")", "").replace("@", "").replace(" ", "")
            
            return raw_username
        
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
        
        def recv_message(self, raw=False, ansi=True):
            global threadFlag
            threadFlag = True
            try:
                while threadFlag:
                    global message
                    message = self.stbc_socket.recv(2048).decode()
                    
                    if message:
                        self.count = self.count + 1
                
                        if self.count > 3:
                            self.logger(message, type=Scapi.LogLevel.INFO)
                        
                        if raw == False:
                            if ansi == True:
                                return message
                            
                            elif ansi == False:
                                return self.escape_ansi(message)
                            
                            else: 
                                return message
                        
                        elif raw == True:
                            index = message.find(":")
                            msg_splitted = message[index + 2:]
                            return self.escape_ansi(msg_splitted)
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
            self.logger(f"{YELLOW}Connecting to {PURPLE}{self.host}:{self.port} {RESET + YELLOW}...", type=Scapi.LogLevel.INFO)
            self.stbc_socket.connect((self.host, self.port))
            self.logger(f"{GREEN}Connected", type=Scapi.LogLevel.INFO)
            
            
        def disconnect(self):
            self.stbc_socket.close()
            
        def event(self, func):
            setattr(self, func.__name__, func)
            return func
            
        def run(self, ready_func):
            if self.enableUserInput is True:
                self.logger(f"{YELLOW}Flag {GREEN + BOLD}'enableUserInput'{RESET + YELLOW} is enabled", type=Scapi.LogLevel.INFO)
                
            if self.printReceivedMessagesToTerminal is True:
                self.logger(f"{YELLOW}Flag {GREEN + BOLD}'printReceivedMessagesToTerminal'{RESET + YELLOW} is enabled", type=Scapi.LogLevel.INFO)
                
            time.sleep(0.5)
            ready_func()
            
            recvThread = threading.Thread(target=self.recv_message)
            sendThread = threading.Thread(target=self.send)
            
            recvThread.start()
            sendThread.start()