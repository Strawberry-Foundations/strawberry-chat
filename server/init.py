import os
import yaml
import requests
import logging
import datetime
import json
import time

from enum import Enum
from yaml import SafeLoader
from colorama import Style

from src.colors import *
from src.vars import chat_name, short_ver, codename, server_edition, api

# Path of init.py
server_dir = os.path.dirname(os.path.realpath(__file__))

# Open Configuration
with open(server_dir + "/config.yml") as config_data:
    config = yaml.load(config_data, Loader=SafeLoader)

import sqlite3

"""
-- LogMessages --
All types of log messages
"""
class LogMessages:
    address_left        = "%s has left"
    user_left           = "%s (%s) has left"
    queue_kick          = "%s got kicked out of the queue"
    queue_left          = "%s (%s) left the queue"
    queue_join          = "%s (%s) is now in the queue"
    connected           = "%s has connected"
    login               = "%s (%s) logged in"
    login_error         = "A login error with %s occured!"
    communication_error = "A communication error with %s (%s) occured!"
    connection_error    = "A connection error occured!"
    transmission_error  = "A message transmission error occurred."
    sql_error           = "An SQL error occured!"
    client_side_error   = "A client-side error occurred."
    stc_error           = "A socket-to-client exception occured"
    registration_error  = "A registration exception occured"
    invalid_sessions_w  = "You should kick some invalid sessions."
    broadcast_error     = "A broadcasting error occurred."
    runtime_stop        = "Runtime has stopped."
    server_stop         = "Server stopped"
    badge_error         = "Something went wrong while... doing something with the badges?: "


class Database:
    def __init__(self, driver, **kwargs):
        self.driver     = driver
        self.connection = None
        self.cursor     = None
        
        if self.driver == "sqlite":
            self.connect_sqlite(kwargs.get('database_path', ':memory:'))

    def connect_sqlite(self, database_path):
        self.connection = sqlite3.connect(database_path)
        self.cursor = self.connection.cursor()


"""
-- ClientSender --
Class & functions for sending json-messages to clients
"""
class ClientSender:
    def __init__(self, socket):
        self.socket = socket
        
    def send_json(self, data): return json.dumps(data)
        
    def send(self, message):
        json_builder = {
            "message_type": StbCom.SYS_MSG,
            "message": {
                "content": message
            }
        }
        
        self.socket.send(self.send_json(json_builder).encode('utf8'))
    
    def close(self, call_exit: bool = True, del_address: bool = False, del_user: bool = False, log_exit: bool = False):
        if log_exit: log.info(LogMessages.address_left % addresses[self.socket][0])
        
        self.socket.close()
        
        if del_address: del addresses[self.socket]
        if del_user: del users[self.socket]
        if call_exit: exit()
        
"""
-- Queue --
Queue handling for users
"""
class Queue:
    def __init__(self):
        self.queue = []
        
    def add(self, user):
        self.queue.append(user)
        
    def remove(self, pos: int = 0):
        if self.queue: return self.queue.pop(pos)
        else: return None
        
    def show(self):
        for pos, user in enumerate(self.queue, start=1):
            print(f"#{pos}: {user}")
            
    def position_user(self, user):
        try:
            return self.queue.index(user) + 1
        
        except Exception as e:
            return 0
        
"""
-- Stopwatch --
Required class for the Queue
"""  
class Stopwatch:
    def __init__(self):
        self.start_time = None
        self.running = False

    def start(self):
        if not self.running:
            self.start_time = time.time()
            self.running = True
            
    def elapsed_time(self):
        elapsed_time = time.time() - self.start_time
        return int(elapsed_time)

    def stop(self):
        if self.running:
            elapsed_time = time.time() - self.start_time
            self.running = False

    def reset(self):
        self.start_time = None
        self.running = False

# StbTypes, required for the debug_logger
class StbTypes(Enum):
    INFO = 0
    WARNING = 2
    ERROR = 1

class StbCom:
    PLAIN = 0
    JSON = 1
    USER_MSG = "user_message"
    SYS_MSG = "system_message"

# stbexceptions class for better error handling  
class stbexceptions:
    connection_error        = "001"
    login_error             = "002"
    communication_error     = "003"
    client_error            = "004"
    stc_error               = "005"
    reg_error               = "021"
    sql_error               = "096"
    general_error           = "100"
    broken_pipe_error       = "122"
    broken_pipe_warning     = "123"
    transmition_error       = "242"
    server_banned_error     = "999"



# Init logger
class LogFormatter(logging.Formatter):
    class Fmt:
        info     = f"{RESET}[%(asctime)s] {BLUE}[%(levelname)s]{RESET + Colors.RESET}    %(message)s"
        error    = f"{RESET}[%(asctime)s] {RED}[%(levelname)s]{RESET + Colors.BOLD}   %(message)s"
        default  = f"{RESET}[%(asctime)s] {BLUE}[%(levelname)s]{RESET + Colors.RESET + Colors.BOLD}   %(message)s"
        warning  = f"{RESET}[%(asctime)s] {YELLOW}[%(levelname)s]{RESET + Colors.RESET + Colors.BOLD} %(message)s"
        critical = f"{RESET}[%(asctime)s] {RED}[%(levelname)s]{RESET + Colors.RESET + Colors.BOLD} %(message)s"

    FORMATS = {
        logging.DEBUG:    Colors.BOLD + Fmt.default,
        logging.INFO:     Colors.BOLD + Fmt.info,
        logging.WARNING:  Colors.BOLD + Fmt.warning,
        logging.ERROR:    Colors.BOLD + Fmt.error,
        logging.CRITICAL: Colors.BOLD + Fmt.critical
    }

    def format(self, record):
        log_fmt = Style.RESET_ALL + self.FORMATS.get(record.levelno) + Style.RESET_ALL
        formatter = logging.Formatter(log_fmt, datefmt='%H:%M')
        return formatter.format(record)

# Print debug error codes
def debug_logger(error_message, error_code, type: StbTypes = StbTypes.ERROR):
    if debug_mode:
        match error_code:
            case stbexceptions.connection_error:        error = "connection_error"
            case stbexceptions.login_error:             error = "login_error"
            case stbexceptions.communication_error:     error = "communication_error"
            case stbexceptions.client_error:            error = "client_error"
            case stbexceptions.stc_error:               error = "stc_error"
            case stbexceptions.reg_error:               error = "reg_error"
            case stbexceptions.sql_error:               error = "sql_error"
            case stbexceptions.general_error:           error = "general_error"
            case stbexceptions.broken_pipe_error:       error = "broken_pipe_error"
            case stbexceptions.broken_pipe_warning:     error = "broken_pipe_warning"
            case stbexceptions.transmition_error:       error = "transmition_error"
            case stbexceptions.server_banned_error:     error = "server_banned_error"
            case _:                                     error = "undefined_error"
            
        if type == StbTypes.ERROR:
            log.error(f"stbexceptions::{error} ({error_code}) -> {error_message}")

        elif type == StbTypes.WARNING:
            log.warning(f"stbexceptions::{error} ({error_code}) -> {error_message}")
    else:
        None

# Startup title
print(f"{CYAN + Colors.BOLD}* -- {chat_name} v{short_ver} {codename} ({server_edition}) -- *{RESET + Colors.RESET}")


# Configuration
ipaddr                  = config['server']['address']
port                    = config['server']['port']

enable_messages         = config['flags']['enable_messages']
enable_queue            = config['flags']['enable_queue']
max_message_length      = config['flags']['max_message_length']
max_users               = config['flags']['max_users']
max_registered_users    = config['flags']['max_registered_users']
debug_mode              = config['flags']['debug_mode']
online_mode             = config['flags']['online_mode']
update_channel          = config['server']['update_channel']
admins_wait_queue       = config['flags']['admins_wait_queue']
bots_wait_queue         = config['flags']['bots_wait_queue']
special_messages        = config['flags']['special_messages']

class DBConfig:
    driver      = config['database']['driver']
    host        = config['database']['host']
    port        = config['database']['port']
    db_name     = config['database']['database_name']
    db_table    = config['database']['database_table']
    

test_mode               = False

# Log configuration
log             = logging.getLogger("LOG")
log_fh          = logging.FileHandler(server_dir + '/log.txt')
log_fmt         = logging.Formatter(f"(%(asctime)s) [%(levelname)s]  %(message)s")
log_ch          = logging.StreamHandler()

# Lists, Dicts and Sets
afks            = list([])
queue           = Queue()
users           = {}
addresses       = {}
user_logged_in  = {}
blacklist       = set()



if os.environ.get("LOG_LEVEL") is not None:
    log.setLevel(os.environ.get("LOG_LEVEL").upper())
    
else:
    log.setLevel("INFO")
    

log_fh.setFormatter(log_fmt)
log_ch.setFormatter(LogFormatter())
log.addHandler(log_ch)
log.addHandler(log_fh)


# Receive your global ip address for verification
def get_global_ip():
    response    = requests.get(api + 'utils/user/ip')
    data        = response.json()
    return data['ip']

if online_mode:
    print(f"{YELLOW + Colors.BOLD}>>> Connecting to the Strawberry API ...{RESET + Colors.RESET}")
    global_ip   = get_global_ip()
    print(f"{GREEN + Colors.BOLD}>>> Connected{RESET + Colors.RESET}")
    
else:
    global_ip   = ""