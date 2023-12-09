from .. import register_command, PermissionLevel

import socket

from src.colors import *
from src.db import Database
from src.vars import server_settings_help
from src.functions import hash_password, verify_password, escape_ansi

from init import User, ClientSender, \
                 server_dir, ipaddr, port, \
                 enable_messages, enable_queue, \
                 max_message_length, max_users, \
                 debug_mode, online_mode, update_channel, \
                 afks, queue, users, addresses, user_logged_in, blacklist


@register_command("config", arg_count=1, required_permissions=PermissionLevel.ADMIN)
def user_settings_command(socket: socket.socket, user: User, args: list, sender: ClientSender):
    cmd_db = Database(server_dir + "/users.db", check_same_thread=False)
    
    try:
        match args[0]:
            case "help":
                sender.send(f"{server_settings_help}{RESET}")
            
            case _:
                sender.send(f"{Colors.RESET + RED}Invalid subcommand!{RESET + Colors.RESET}")
                    
    except Exception as e: 
        sender.send(f"{RED}Not enough arguments!{RESET}")
        print(e)