import os
import yaml
import requests
import logging

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

# StbTypes, required for the debug_logger
class StbTypes(Enum):
    INFO = 0
    WARNING = 2
    ERROR = 1

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
debug_mode              = config['flags']['debug_mode']
online_mode             = config['flags']['online_mode']

# Log configuration
log             = logging.getLogger("LOG")
log_fh          = logging.FileHandler(server_dir + '/log.txt')
log_fmt         = logging.Formatter(f"(%(asctime)s) [%(levelname)s]  %(message)s")
log_ch          = logging.StreamHandler()

# Lists, Dicts and Sets
afks            = list([])
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