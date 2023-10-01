import socket
import threading
import time
import datetime
import sys
import re
from enum import Enum

# if sys.platform == "linux":
#     import readline
# elif sys.platform == "win32":
#     pass

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

version = "0.10.2"
command_registry = {}

class Messages:
    permission_error_msg = "#redYou lack the permission to use this command!#reset"
    command_not_found_msg = "#redCommand '%s' not found.#reset"
    not_enough_arguments = "#redNot enough arguments! Command requires %s arguments but %s were given#reset"

class Scapi:
    class LogLevel:
        INFO = "INFO"
        ERROR = "ERROR"
        MSG = "MSG"
        MESSAGE = "MSG"
                
    class Bot:    
        class PermissionLevel(Enum):
            CUSTOM  = -1
            ALL     = 0
            TRUSTED = 1
            ADMIN   = 2
            OWNER   = 3
            
        def __init__(self, username, token, host, port, enable_user_input=False, print_recv_msg=False):
            self.stbc_socket        = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.username           = username
            self.token              = token
            self.host               = host
            self.port               = port
            self.enable_user_input  = enable_user_input
            self.print_recv_msg     = print_recv_msg
            
            self.trusted_list       = []
            self.admin_list         = []
            self.custom_list        = []
            self.owner              = None
            
            self.req_permissions    = None
            self.count              = 0
            
            self.logger(f"{GREEN}Starting scapi.bot version {version}", type=Scapi.LogLevel.INFO)
            self.log_msg = f"{CYAN + BOLD}{datetime.date.today().strftime('%Y-%m-%d')} {datetime.datetime.now().strftime('%H:%M:%S')}  {BLUE}INFO   scapi  -->  {RESET}"
        
            
            try:
                self.connect()
                
            except: 
                self.logger(f"{RED}Could not connect to server", type=Scapi.LogLevel.ERROR)
                exit()

        def logger(self, message, type):
            if type.lower() == "info":
                print(f"{CYAN + BOLD}{datetime.date.today().strftime('%Y-%m-%d')} {datetime.datetime.now().strftime('%H:%M:%S')}  {BLUE}{type.upper()}{BLUE}   scapi  -->  {RESET}{message}{RESET}")            
            elif type.lower() == "error":
                print(f"{CYAN + BOLD}{datetime.date.today().strftime('%Y-%m-%d')} {datetime.datetime.now().strftime('%H:%M:%S')}  {RED}{type.upper()}{BLUE}  scapi  -->  {RESET}{message}{RESET}")            
            elif type.lower() == "msg":
                print(f"{CYAN + BOLD}{datetime.date.today().strftime('%Y-%m-%d')} {datetime.datetime.now().strftime('%H:%M:%S')}  {GREEN}{type.upper()}{BLUE}    scapi  -->  {RESET}{message}{RESET}")            
            
        
        def flag_handler(self, enable_user_input=False, print_recv_msg=False):
            self.enable_user_input  = enable_user_input
            self.print_recv_msg     = print_recv_msg
            
        def permission_handler(self, trusted_list: list = [], admin_list: list = [], owner: str = None, custom_list: list = []):
            self.trusted_list   = trusted_list
            self.admin_list     = admin_list
            self.owner          = owner
            self.custom_list    = custom_list

        def send_message(self, message):
            self.stbc_socket.send(message.encode("utf8"))
            
        def escape_ansi(self, line):
            ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
            return ansi_escape.sub('', line)
        
        def get_username_by_msg(self, message):
            username = message.split(":")[0]
            username = username.replace("[", "") \
                               .replace("]", "") \
                               .replace("👑", "") \
                               .replace("😎", "") \
                               .replace("🔥", "") \
                               .replace("🫐", "") \
                               .replace("🤖", "") \
                               .replace("💪", "") \
                               .replace("👍", "") \
                               .replace("🤡", "") \
                               .replace("😈", "") \
                               .replace("🤝", "") \
                               .replace("👋", "") \
                               .replace("😌", "") \
                               .replace("🍓", "") \
                               .replace("💫", "") \
                               .replace("9mm", "") \
                               .replace("1mm", "") \
                                           
            username_index  = username.find("(")
            raw_username    = username[username_index + 1:]
            raw_username    = raw_username.replace(")", "").replace("@", "").replace(" ", "")
            
            return raw_username     
        
        def send(self):
            threadFlag = True
            def delete_last_line():
                cursorUp = "\x1b[1A"
                eraseLine = "\x1b[2K"
                sys.stdout.write(cursorUp)
                sys.stdout.write(eraseLine)
            
            if self.enable_user_input is True:
                while threadFlag:
                    try:
                        message = input("")
                        delete_last_line()
                        self.stbc_socket.send(message.encode("utf8"))

                    except:
                        if threadFlag == False:
                            pass
                        
                        else:
                            self.logger(f"{RED}Message could not be sent", type=Scapi.LogLevel.ERROR)
                            break
        
        def recv_message(self, raw=False, ansi=False):
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
        
        def command(self, name, arg_count: int = 0, required_permissions=PermissionLevel.ALL, custom_permissions: list = None) -> None:
            def decorator(func):
                if custom_permissions is None:
                    self.custom_list = self.custom_list
                else:
                    self.custom_list = custom_permissions
                    
                self.req_permissions = required_permissions
                
                
                command_registry[name] = (func, arg_count, required_permissions)
                return func

            return decorator

        def execute_command(self, command_name, user: str, args: list, permission_error_msg=Messages.permission_error_msg, command_not_found_msg = Messages.command_not_found_msg):
            if self.escape_ansi(command_name) in command_registry:
                cmd = command_registry[self.escape_ansi(command_name)]

                if self.req_permissions == self.PermissionLevel.ALL:
                    pass
                
                elif self.req_permissions == self.PermissionLevel.TRUSTED:
                    if user not in self.trusted_list:
                        self.send_message(permission_error_msg)
                        return    
                    
                elif self.req_permissions == self.PermissionLevel.ADMIN:
                    if user not in self.admin_list:
                        self.send_message(permission_error_msg)
                        return
                
                elif self.req_permissions == self.PermissionLevel.OWNER:
                    if user.lower() != self.owner:
                        self.send_message(permission_error_msg)
                        return
                
                elif self.req_permissions == self.PermissionLevel.CUSTOM:
                    if user.lower() not in self.custom_list:
                        self.send_message(permission_error_msg)
                        return
                
                else:
                    self.logger(f"{RED}Invalid permission type!", type=Scapi.LogLevel.ERROR)
                    return
                
                if cmd[1] > args.__len__():
                    self.send_message(Messages.not_enough_arguments % (cmd[1], args.__len__()))
                    return
                
                cmd[0](user, args)
                
            else:
                self.send_message(command_not_found_msg % command_name)
            
        def run(self, ready_func):
            if self.enable_user_input is True:
                self.logger(f"{YELLOW}Flag {GREEN + BOLD}'enableUserInput'{RESET + YELLOW} is enabled", type=Scapi.LogLevel.INFO)
                
            if self.print_recv_msg is True:
                self.logger(f"{YELLOW}Flag {GREEN + BOLD}'printReceivedMessagesToTerminal'{RESET + YELLOW} is enabled", type=Scapi.LogLevel.INFO)
                
            time.sleep(0.5)
            ready_func()
            
            recvThread = threading.Thread(target=self.recv_message)
            sendThread = threading.Thread(target=self.send)
            
            recvThread.start()
            sendThread.start()