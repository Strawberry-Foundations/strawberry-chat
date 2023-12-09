from .. import register_command, PermissionLevel

import socket

from src.colors import *
from src.db import Database
from src.vars import role_colors

from init import User, ClientSender, server_dir

@register_command("role", arg_count=1, required_permissions=PermissionLevel.ADMIN)
def role_command(socket: socket.socket, user: User, args: list, sender: ClientSender):
    cmd_db = Database(server_dir + "/users.db", check_same_thread=False)

    cmd = args[0]
    
    # /role set Command
    if cmd == "set":
        try:
            uname = args[1]
            role = args[2]
            
            if role not in ["member", "bot", "admin"]:
                sender.send(f"{RED + Colors.BOLD}Invalid role!{RESET + Colors.RESET}")
                return
        
            cmd_db.execute("UPDATE users SET role = ? WHERE username = ?", (role, uname))
            cmd_db.commit()
            
            sender.send(f"{LIGHTGREEN_EX + Colors.BOLD}Role of {uname} was set to {role}{RESET + Colors.RESET}")
        
        except:
            sender.send(f"{RED + Colors.BOLD}Invalid username and/or role!{RESET + Colors.RESET}")
    
    # /role get Command
    elif cmd == "get":
        try:
            uname = args[1]
        
            cmd_db.execute("SELECT role FROM users WHERE username = ?", (uname,))
            role = cmd_db.fetchone()[0]
            
            sender.send(f"{LIGHTGREEN_EX + Colors.BOLD}Role of {uname}: {MAGENTA}{role}{RESET + Colors.RESET}")
        
        except:
            sender.send(f"{RED + Colors.BOLD}Invalid username!{RESET + Colors.RESET}")
    
    # /role color Command
    elif cmd == "color":
        try:
            uname = args[1]
            color = args[2]
            
            if color.lower() not in role_colors:
                sender.send(f"{RED + Colors.BOLD}Invalid color!{RESET + Colors.RESET}")
                return
        
            cmd_db.execute("UPDATE users SET role_color = ? WHERE username = ?", (color.lower(), uname))
            cmd_db.commit()
            
            sender.send(f"{LIGHTGREEN_EX + Colors.BOLD}Role Color of {uname} was set to {color}{RESET + Colors.RESET}")
    
        except:
            sender.send(f"{RED + Colors.BOLD}Invalid username and/or color!{RESET + Colors.RESET}")
        
    else:
        sender.send(f"{RED + Colors.BOLD}Invalid command usage.{RESET + Colors.RESET}")