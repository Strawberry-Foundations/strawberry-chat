from .. import register_command

import socket
import yaml

from src.colors import *
from yaml import SafeLoader
from init import server_dir, addresses, users, user_logged_in
from src.functions import broadcast_all, userRoleColor

# Open Configuration
with open(server_dir + "/config.yml") as config_data:
        config = yaml.load(config_data, Loader=SafeLoader)

@register_command("exit")
@register_command("quit")
def exit_command(socket: socket.socket, username: str, args: list, send):
    send(f"{YELLOW + Colors.BOLD}You left the chat!{RESET + Colors.RESET}")
    del addresses[socket]
    del users[socket]
    socket.close()
    
    user_logged_in[username] = False
    
    # log.info(f"{user} ({address}) has left.")
    broadcast_all(f"{Colors.GRAY + Colors.BOLD}<--{Colors.RESET} {userRoleColor(username)}{username}{YELLOW + Colors.BOLD} has left the chat room!{RESET + Colors.RESET}")
