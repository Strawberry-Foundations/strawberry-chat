from .. import register_command, PermissionLevel

import socket

from src.colors import *
from src.functions import doesUserExist
from src.db import Database

from init import server_dir, users, addresses

@register_command("kick", arg_count=1, required_permissions=PermissionLevel.ADMIN)
def kick_command(socket: socket.socket, username: str, args: list):
    cmd_db  = Database(server_dir + "/users.db", check_same_thread=False)
    
    uname   = args[0]
    reason  = ' '.join(args[1:])
    
    if reason == "":
        reason = "No reason provided"
        
    search_val = uname
    found_keys = []
        
    for key, value in users.items():
        if value == search_val:
            global to_kick
            to_kick = key
            found_keys.append(key)
            
    if uname == username:
        socket.send(f"{YELLOW}You shouldn't kick yourself...{RESET}".encode("utf8"))
        return
    
    else:
        if found_keys:
            socket.send(f"{YELLOW + Colors.BOLD}Kicked {uname} for following reason: {reason}{RESET + Colors.RESET}".encode("utf8"))
            to_kick.send(f"{YELLOW + Colors.BOLD}You have been kicked out of the chat for the following reason: {reason}{RESET + Colors.RESET}".encode("utf8"))
            
            try:
                del addresses[to_kick]
                del users[to_kick]
                to_kick.close()
                
            except Exception as e: 
                pass
            
        else:
            socket.send(f"{RED + Colors.BOLD}User not found or user is offline.{RESET + Colors.RESET}".encode("utf8"))
            return