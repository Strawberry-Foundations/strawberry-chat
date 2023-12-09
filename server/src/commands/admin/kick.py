from .. import register_command, PermissionLevel

import socket

from src.colors import *
from src.functions import doesUserExist, broadcast_all, userRoleColor
from src.db import Database

from init import User, ClientSender, server_dir, users, addresses, log

@register_command("kick", arg_count=1, required_permissions=PermissionLevel.ADMIN)
def kick_command(socket: socket.socket, user: User, args: list, sender: ClientSender):
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
            
    if uname == user.username:
        sender.send(f"{YELLOW}You shouldn't kick yourself...{RESET}")
        return
    
    else:
        if found_keys:
            try:
                log.info(f"{uname} ({addresses[socket][0]}) has been kicked out of the chat by {user.username} for following reason: {reason}")
                
                del addresses[to_kick]
                del users[to_kick]
                
                sender.send(f"{YELLOW + Colors.BOLD}Kicked {uname} for following reason: {reason}{RESET + Colors.RESET}")                
                to_kick.send(f"{YELLOW + Colors.BOLD}You have been kicked out of the chat for the following reason: {reason}{RESET + Colors.RESET}")
                
                
                broadcast_all(f"{Colors.GRAY + Colors.BOLD}<--{Colors.RESET} {userRoleColor(uname)}{uname}{YELLOW + Colors.BOLD} has left the chat room!{RESET + Colors.RESET}")
                
                
                try: to_kick.close()
                except Exception as e:
                    print(f"Could not kick {uname} ({to_kick}) (Closing connection): {e}")
                    pass
                
            except Exception as e: 
                print(f"Could not kick {uname} ({to_kick}): {e}")
                pass
            
        else:
            sender.send(f"{RED + Colors.BOLD}User not found or user is offline.{RESET + Colors.RESET}")
            return