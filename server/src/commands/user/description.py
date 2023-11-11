from .. import register_command

import socket

from src.colors import *
from src.db import Database

from init import server_dir

@register_command("description", arg_count=0)
def description_command(socket: socket.socket, username: str, args: list, send):
    cmd_db = Database(server_dir + "/users.db", check_same_thread=False)
    
    desc = " ".join(args)
    
    if desc.lower() == "remove" or desc.lower() == "reset":
        cmd_db.execute("UPDATE users SET description = NULL WHERE username = ?", (username,))
        cmd_db.commit()
        
        send(f"{LIGHTGREEN_EX + Colors.BOLD}Removed Description{RESET + Colors.RESET}")
    
    elif desc.lower() == "" or desc.lower() == " ":
        cmd_db.execute("SELECT description FROM users WHERE username = ?", (username,))
        desc = cmd_db.fetchone()[0]
        
        send(f"{LIGHTGREEN_EX + Colors.BOLD}Your current description: {RESET}{desc}{Colors.RESET}")
        
    else:        
        cmd_db.execute("UPDATE users SET description = ? WHERE username = ?", (desc, username))
        cmd_db.commit()
        
        send(f"{LIGHTGREEN_EX + Colors.BOLD}Changed Description to {CYAN}{desc}{RESET + Colors.RESET}")
        

@register_command("desc")
def desc_command(socket: socket.socket, username: str, args: list, send):
    cmd_db = Database(server_dir + "/users.db", check_same_thread=False)
    cmd_db.execute("SELECT description FROM users WHERE username = ?", (username,))
    desc = cmd_db.fetchone()[0]
    send(f"{LIGHTGREEN_EX + Colors.BOLD}Your current description: {RESET}{desc}{Colors.RESET}")                