import os
import yaml
import requests
import logging
import datetime

from enum import Enum
from yaml import SafeLoader
from colorama import Style

from src.colors import *
from src.vars import chat_name, short_ver, codename, server_edition

# Path of init.py
server_dir = os.path.dirname(os.path.realpath(__file__))

class StbTypes(Enum):
    INFO = 0
    WARNING = 2
    ERROR = 1
    
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
    transmition_error       = "242"
    server_banned_error     = "999"
    
    
afks = list([])
users = {}
addresses = {}
user_logged_in = {}

# Init logger
class LogFormatter(logging.Formatter):
    class Fmt:
        info     = f"{RESET}[{datetime.datetime.now().strftime('%H:%M')}] {BLUE}[%(levelname)s]{RESET + Colors.RESET}    %(message)s"
        error    = f"{RESET}[{datetime.datetime.now().strftime('%H:%M')}] {RED}[%(levelname)s]{RESET + Colors.BOLD}   %(message)s"
        default  = f"{RESET}[{datetime.datetime.now().strftime('%H:%M')}] {BLUE}[%(levelname)s]{RESET + Colors.RESET + Colors.BOLD}   %(message)s"
        warning  = f"{RESET}[{datetime.datetime.now().strftime('%H:%M')}] {YELLOW}[%(levelname)s]{RESET + Colors.RESET + Colors.BOLD} %(message)s"
        critical = f"{RESET}[{datetime.datetime.now().strftime('%H:%M')}] {RED}[%(levelname)s]{RESET + Colors.RESET + Colors.BOLD} %(message)s"

    FORMATS = {
        logging.DEBUG:    Colors.BOLD + Fmt.default,
        logging.INFO:     Colors.BOLD + Fmt.info,
        logging.WARNING:  Colors.BOLD + Fmt.warning,
        logging.ERROR:    Colors.BOLD + Fmt.error,
        logging.CRITICAL: Colors.BOLD + Fmt.critical
    }

    def format(self, record):
        log_fmt = Style.RESET_ALL + self.FORMATS.get(record.levelno) + Style.RESET_ALL
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


log = logging.getLogger("LOG")

if os.environ.get("LOG_LEVEL") is not None:
    log.setLevel(os.environ.get("LOG_LEVEL").upper())
    
else:
    log.setLevel("INFO")
    
log_fh  = logging.FileHandler(server_dir + '/log.txt')
log_fmt = logging.Formatter(f"(%(asctime)s) [%(levelname)s]  %(message)s")
log_fh.setFormatter(log_fmt)

log_ch = logging.StreamHandler()
log_ch.setFormatter(LogFormatter())

log.addHandler(log_ch)
log.addHandler(log_fh)

# Startup title
print(f"{CYAN + Colors.BOLD}* -- {chat_name} v{short_ver} {codename} ({server_edition}) -- *{RESET + Colors.RESET}")

# Open Configuration
with open(server_dir + "/config.yml") as config_data:
        config = yaml.load(config_data, Loader=SafeLoader)

# Configuration
ipaddr                  = config['server']['address']
port                    = config['server']['port']

enable_messages         = config['flags']['enable_messages']
max_message_length      = config['flags']['max_message_length']
debug_mode              = config['flags']['debug_mode']
online_mode             = config['flags']['online_mode']
update_channel          = config['server']['update_channel']

# Receive your global ip address for verification
def get_global_ip():
    response = requests.get('https://api.ipify.org?format=json')
    data = response.json()
    return data['ip']

if online_mode:
    print(f"{YELLOW + Colors.BOLD}>>> Connecting to the Strawberry API ...{RESET + Colors.RESET}")
    global_ip           = get_global_ip()
    print(f"{GREEN + Colors.BOLD}>>> Connected{RESET + Colors.RESET}")
    
else:
    global_ip = ""