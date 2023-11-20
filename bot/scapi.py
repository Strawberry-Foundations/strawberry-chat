# Warning: This api requires Python 3.10 or higher.

# Copyright (C) 2023 Juliandev02

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses>

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

# Version-specified Variables & important variables
base_version    = "1.0.1"
ext_version     = base_version + "_stbmv1"
version         = "v" + ext_version
full_version    = ext_version + "-vacakes"
update_channel  = "dev"
codename        = "Vanilla Cake"
authors         = ["Juliandev02"]
api             = "http://api.strawberryfoundations.xyz/v1/"

command_registry = {}

class Messages:
    permission_error = "#redYou lack the permission to use this command!#reset"
    command_not_found = "#redCommand '%s' not found.#reset"
    not_enough_arguments = "#redNot enough arguments! Command requires %s arguments but %s were given#reset"

class Scapi:
    class LogLevel(Enum):
        INFO = 0
        ERROR = 1
        MESSAGE = 2
                
    class Bot:    
        class PermissionLevel(Enum):
            CUSTOM  = -1
            ALL     = 0
            TRUSTED = 1
            ADMIN   = 2
            OWNER   = 3
            
        def __init__(self, username: str, token: str, host: str, port: int, enable_user_input: bool = False, print_recv_msg: bool = False):
            self.socket        = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
            
            self.log_msg = f"{CYAN + BOLD}{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  %sscapi  -->  {RESET}"
            
            self.logger(f"{GREEN}Starting scapi {version}", Scapi.LogLevel.INFO)
        
            
            try:
                self.connect()
                
            except: 
                self.logger(f"{RED}Could not connect to server", Scapi.LogLevel.ERROR)
                exit()
                
        def flag_handler(self, enable_user_input: bool = False, print_recv_msg: bool = False, log_msg: str = None):
            self.enable_user_input  = enable_user_input
            self.print_recv_msg     = print_recv_msg
            self.log_msg            = log_msg or f"{CYAN + BOLD}{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  %sscapi  -->  {RESET}"
            
        def connect(self):
            self.logger(f"{YELLOW}Connecting to {PURPLE}{self.host}:{self.port} {RESET + YELLOW}...", type=Scapi.LogLevel.INFO)
            self.socket.connect((self.host, self.port))
            self.logger(f"{GREEN}Connected", type=Scapi.LogLevel.INFO)

        def logger(self, message, type: Enum):
            match type:
                case Scapi.LogLevel.INFO:
                    log_level = f"{BLUE}INFO   "
                    print(f"{self.log_msg % log_level}{message}{RESET}")      
                          
                case Scapi.LogLevel.ERROR:
                    log_level = f"{RED}ERROR  "
                    print(f"{self.log_msg % log_level}{message}{RESET}")     
                     
                case Scapi.LogLevel.MESSAGE:
                    log_level = f"{GREEN}MESSAGE "
                    print(f"{self.log_msg % log_level}{message}{RESET}")   
            
        def permission_handler(self, trusted_list: list = [], admin_list: list = [], owner: str = None, custom_list: list = []):
            self.trusted_list       = trusted_list
            self.admin_list         = admin_list
            self.owner              = owner
            self.custom_list        = custom_list

        def send_message(self, message):
            self.socket.send(message.encode("utf8"))
            
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
                        self.socket.send(message.encode("utf8"))

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
                    message = self.socket.recv(2048).decode()
                    
                    if message:
                        self.count = self.count + 1
                
                        if self.count > 3: self.logger(message, type=Scapi.LogLevel.INFO)
                        
                        if raw == False:
                            if ansi == True: return message
                            elif ansi == False: return self.escape_ansi(message)
                            else: return message
                        
                        elif raw == True:
                            index = message.find(":")
                            msg_splitted = message[index + 2:]
                            return self.escape_ansi(msg_splitted)
                    else: break
                        
                    
            except (KeyboardInterrupt, SystemExit):
                while threadFlag:
                    self.disconnect()
                    threadFlag = False
                
        def login(self):
            self.socket.send(self.username.encode("utf8"))
            time.sleep(1)
            self.socket.send(self.token.encode("utf8"))
            
        def disconnect(self):
            self.socket.close()
            
        def event(self, func):
            setattr(self, func.__name__, func)
            return func
        
        def command(self, name, arg_count: int = 0, required_permissions=PermissionLevel.ALL, custom_permissions: list = None) -> None:
            def decorator(func):
                if custom_permissions is None: self.custom_list = self.custom_list
                else: self.custom_list = custom_permissions
                    
                self.req_permissions = required_permissions
                
                command_registry[name] = (func, arg_count, required_permissions)
                return func

            return decorator

        def execute_command(self, command_name, user: str, args: list, permission_error_msg=Messages.permission_error, command_not_found_msg = Messages.command_not_found, not_enough_arguments = Messages.not_enough_arguments):
            if self.escape_ansi(command_name) in command_registry:
                cmd = command_registry[self.escape_ansi(command_name)]
                
                match self.req_permissions:
                    case self.PermissionLevel.ALL: pass
                    
                    case self.PermissionLevel.TRUSTED:
                        if user not in self.trusted_list:
                            self.send_message(permission_error_msg)
                            return    
                    
                    case self.PermissionLevel.ADMIN:
                        if user not in self.admin_list:
                            self.send_message(permission_error_msg)
                            return
                
                    case self.PermissionLevel.OWNER:
                        if user.lower() != self.owner:
                            self.send_message(permission_error_msg)
                            return
                
                    case self.PermissionLevel.CUSTOM:
                        if user.lower() not in self.custom_list:
                            self.send_message(permission_error_msg)
                            return
                
                    case _:
                        self.logger(f"{RED}Invalid permission type!", type=Scapi.LogLevel.ERROR)
                        return
                
                if cmd[1] > args.__len__():
                    self.send_message(not_enough_arguments % (cmd[1], args.__len__()))
                    return
                
                cmd[0](user, args)
                
            else: self.send_message(command_not_found_msg % command_name)
        
        def command_runner(self):
            while True:
                try:
                    recv_message = self.recv_message(raw=False, ansi=False)
                    index       = recv_message.find(":")
                    raw_message = recv_message[index + 2:]
                    
                    if raw_message.startswith("!"):
                        message = raw_message[1:]
                        args = message.split()
                        cmd = args[0]
                        args = args[1:]
                        
                        self.execute_command(cmd, self.get_username_by_msg(recv_message), args)
                        continue

                except Exception as e: 
                    self.logger(f"{RED}An unknown exception occured{RESET}", type=Scapi.LogLevel.ERROR)
                    self.logger(f"{RED}{e}{RESET}", type=Scapi.LogLevel.ERROR)
                    break
            
            
        def run(self, ready_func = None):
            if self.enable_user_input is True: self.logger(f"{YELLOW}Flag {GREEN + BOLD}'enableUserInput'{RESET + YELLOW} is enabled", type=Scapi.LogLevel.INFO)
            if self.print_recv_msg is True: self.logger(f"{YELLOW}Flag {GREEN + BOLD}'printReceivedMessagesToTerminal'{RESET + YELLOW} is enabled", type=Scapi.LogLevel.INFO)
                
            time.sleep(0.5)
            if not ready_func is None: ready_func()
            
            recv_thread = threading.Thread(target=self.recv_message)
            send_thread = threading.Thread(target=self.send)
            cmd_thread  = threading.Thread(target=self.command_runner)
            
            recv_thread.start()
            send_thread.start()
            cmd_thread.start()