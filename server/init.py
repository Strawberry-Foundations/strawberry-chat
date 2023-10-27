import os
import yaml
import requests
from yaml import SafeLoader

from src.colors import YELLOW, Colors, RESET, GREEN, CYAN
from src.vars import chat_name, short_ver, codename, server_edition

# Startup title
print(f"{CYAN + Colors.BOLD}* -- {chat_name} v{short_ver} {codename} ({server_edition}) -- *{RESET + Colors.RESET}")

# Path of init.py
server_dir = os.path.dirname(os.path.realpath(__file__))

afks = list([])
users = {}
addresses = {}
user_logged_in = {}

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