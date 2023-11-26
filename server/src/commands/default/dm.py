from .. import register_command

import socket as _socket

from src.colors import *
from src.db import Database

from init import server_dir, users, afks, StbCom
from src.functions import escape_ansi, userRoleColor, send_json

@register_command("dm", arg_count=2)
def dm_command(socket: _socket.socket, username: str, args: list, send):
    cmd_db = Database(server_dir + "/users.db", check_same_thread=False)

    uname   = args[0]
    msg     = ' '.join(args[1:])
    msg     = escape_ansi(msg)
    msg     = msg.strip("\n")
    
    found_keys = []
    
    for sock_object, sock_uname in users.items():
        if sock_uname == uname:
            global to_sent
            to_sent = sock_object
            found_keys.append(sock_object)
            
    
    try:
        cmd_db.execute("SELECT enable_dms FROM users WHERE username = ?", (username,))
        has_dm_enabled = cmd_db.fetchone()[0]
        
    except:
        send(f"{RED + Colors.BOLD}User not found{RESET + Colors.RESET}")
    
    if uname == username:
        send(f"{YELLOW}You shouldn't send messages to yourself...{RESET}")
    
    elif uname in afks:
        send(f"{YELLOW}This user is currently afk...{RESET}")
    
    elif has_dm_enabled == "false":
        send(f"{YELLOW}This user has deactivated his/her DM's{RESET}")
    
    else:
        if found_keys:
            send(f"{userRoleColor(username)}You{RESET} {Colors.GRAY}-->{Colors.RESET} {userRoleColor(uname)}{uname}{RESET + Colors.RESET}: {msg}")
            
            json_builder = {
                "message_type": StbCom.SYS_MSG,
                "message": {
                    "content": f"{Colors.RESET + userRoleColor(username)}{username} {Colors.GRAY}-->{RESET + Colors.RESET}{userRoleColor(uname)} You{Colors.RESET + RESET}: {msg}"
                    }
            }
            
            to_sent.send(send_json(json_builder).encode("utf-8"))
            
        else:
            send(f"{RED + Colors.BOLD}User is offline.{RESET + Colors.RESET}")
            