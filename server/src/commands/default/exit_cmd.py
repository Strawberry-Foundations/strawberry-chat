from .. import register_command

import socket
import yaml

from src.colors import *
from yaml import SafeLoader
from init import LogMessages, User, ClientSender, server_dir, addresses, users, user_logged_in, log
from src.functions import broadcast_all, userRoleColor

# Open Configuration
with open(server_dir + "/config.yml") as config_data:
        config = yaml.load(config_data, Loader=SafeLoader)

@register_command("exit")
@register_command("quit")
def exit_command(socket: socket.socket, user: User, args: list, sender: ClientSender):
    sender.send(f"{YELLOW + Colors.BOLD}You left the chat!{RESET + Colors.RESET}")
    log.info(LogMessages.user_left % (user.username, user.address))
    
    del addresses[socket]
    del users[socket]
    socket.close()
    
    
    user_logged_in[user.username] = False
    
    
    broadcast_all(f"{Colors.GRAY + Colors.BOLD}<--{Colors.RESET} {userRoleColor(user.username)}{user.username}{YELLOW + Colors.BOLD} has left the chat room!{RESET + Colors.RESET}")
