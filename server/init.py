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

import socket as _socket

# Path of init.py
server_dir = os.path.dirname(os.path.realpath(__file__))

# Open Configuration
with open(server_dir + "/config.yml") as config_data:
    config = yaml.load(config_data, Loader=SafeLoader)
    
if config['database']['driver'] == "sqlite": 
    import sqlite3
elif config['database']['driver'] == "mysql": 
    import pymysql
else:
    pass

import pymysql

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
        self.driver                 = driver
        self.connection             = None
        self.cursor                 = None
        self.sqlite_database_dir    = server_dir + "/users.db"
        
        if self.driver == "sqlite":
            self.connect_sqlite(self.sqlite_database_dir)
            
        elif self.driver == 'mysql':
            try:
                self.connect_mysql(host=DatabaseConfig.host,
                                user=DatabaseConfig.user,
                                password=DatabaseConfig.password,
                                database=DatabaseConfig.db_name)
                
            except (pymysql.err.OperationalError, ConnectionRefusedError) as e:
                print(f"{RED + Colors.BOLD}>>>{RESET} Could not connect to MySQL server:{Colors.RESET} {e}")
                exit(1)


    def connect_sqlite(self, database_path):
        self.connection = sqlite3.connect(database_path, check_same_thread=DatabaseConfig.chck_thread)
        self.cursor = self.connection.cursor()
    
    def connect_mysql(self, host, user, password, database):
        self.connection = pymysql.connect(host=host,
                                          user=user,
                                          password=password,
                                          database=database,
                                          cursorclass=pymysql.cursors.DictCursor)
        self.cursor = self.connection.cursor()
        
    def disconnect(self):
        if self.connection:
            self.connection.close()

    def execute_query(self, query, parameters=None):
        if self.driver == "mysql":
            query = query.replace("?", "%s")
        
        if not self.cursor:
            raise RuntimeError("Not connected to the database. Call connect method first.")

        if parameters:
            if isinstance(parameters, (list, tuple)):
                self.cursor.execute(query, parameters)
            elif isinstance(parameters, dict):
                self.cursor.execute(query, parameters)
            else:
                raise ValueError("Unsupported parameter type. Use list, tuple, or dictionary.")
        else:
            self.cursor.execute(query)

        return self.cursor
    
    def _execute_query(self, query):
        self.cursor.execute(query)
        return self.cursor


    def fetch_all(self, query, parameters=None):            
        cursor = self.execute_query(query, parameters)
        return cursor.fetchall()

    def fetch_one(self, query, parameters=None):
        cursor = self.execute_query(query, parameters)
        return cursor.fetchone()

    def commit(self):
        if self.connection:
            self.connection.commit()

    def rollback(self):
        if self.connection:
            self.connection.rollback()


"""
-- ClientSender --
Class & functions for sending json-messages to clients
"""
class ClientSender:
    def __init__(self, socket):
        self.socket = socket
        
    def send_json(self, data): return json.dumps(data)
    
    def custom_send(self, json_data): self.socket.send(self.send_json(json_data).encode('utf8'))
        
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
-- User --
User property handling & login
"""
class User:
    class Status:
        afk     = "status.afk"
        dnd     = "status.dnd"
        online  = "status.online"
        offline = "status.offline"
        none    = "status.none"
        
    def __init__(self, socket="type.none"):
        if not socket == "type.none":          
            self.socket         = socket
            self.address        = addresses[socket][0]
            
        self.username       = ""
        self.user_status    = User.Status.none
        
    def login(self, func):
        self.username = func
        return self.username
    
    def set_username(self, username: str):
        self.username = username
        
    def set_user_status(self, status: Status):
        self.user_status = status
        user_index[self.username]["status"] = status
    
    def status(self):
        if self.username in users.values():
            if user_index[self.username]["status"] == "status.afk":
                return User.Status.afk
            elif user_index[self.username]["status"] == "status.dnd":
                return User.Status.dnd
            else:
                return User.Status.online
        else:
            return User.Status.offline
        
    def get_system_register(self):
        return user_index[self.username]
        
    def system_register(self):
        user_index[self.username] = {
            "status": User.Status.online
        }
        
        self.user_status = User.Status.online
        
        print(user_index)
        
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


"""
    --- Initial Strawberry Chat Startup ---
"""

# Startup title
print(f"{CYAN + Colors.BOLD}* -- {chat_name} v{short_ver} {codename} ({server_edition}) -- *{RESET + Colors.RESET}")


# Configuration
ipaddr                  = config['server']['address']
port                    = config['server']['port']
update_channel          = config['server']['update_channel']

enable_messages         = config['flags']['enable_messages']
max_message_length      = config['flags']['max_message_length']

enable_queue            = config['flags']['enable_queue']
admins_wait_queue       = config['flags']['admins_wait_queue']
bots_wait_queue         = config['flags']['bots_wait_queue']

max_users               = config['flags']['max_users']
max_registered_users    = config['flags']['max_registered_users']

debug_mode              = config['flags']['debug_mode']
online_mode             = config['flags']['online_mode']

special_messages        = config['flags']['special_messages']

require_signing         = config['security']['require_signing']
signing_key             = config['security']['signing_key']
banned_ips              = config['security']['banned_ips']

config_ver_yml          = config['config_ver']

class DatabaseConfig:
    driver      = config['database']['driver']
    chck_thread = config['database']['check_same_thread']
    
    host        = config['database']['host']
    port        = config['database']['port']
    user        = config['database']['user']
    password    = config['database']['password']
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
do_not_disturb  = list([])

# just an prototype
user_index = {}

queue           = Queue()
users           = {}
addresses       = {}
user_logged_in  = {}
blacklist       = set()
user_dm_screen  = {}


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