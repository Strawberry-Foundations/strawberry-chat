from .. import register_command

import socket

from src.colors import *
from src.db import Database

from init import User, ClientSender, server_dir

@register_command("description", arg_count=0)
def description_command(socket: socket.socket, user: User, args: list, sender: ClientSender):
    cmd_db = Database(server_dir + "/users.db", check_same_thread=False)
    
    desc = " ".join(args)
    
    if desc.lower() == "remove" or desc.lower() == "reset":
        cmd_db.execute("UPDATE users SET description = NULL WHERE username = ?", (user.username,))
        cmd_db.commit()
        
        sender.send(f"{LIGHTGREEN_EX + Colors.BOLD}Removed Description{RESET + Colors.RESET}")
    
    elif desc.lower() == "" or desc.lower() == " ":
        cmd_db.execute("SELECT description FROM users WHERE username = ?", (user.username,))
        desc = cmd_db.fetchone()[0]
        
        sender.send(f"{LIGHTGREEN_EX + Colors.BOLD}Your current description: {RESET}{desc}{Colors.RESET}")
        
    else:        
        cmd_db.execute("UPDATE users SET description = ? WHERE username = ?", (desc, user.username))
        cmd_db.commit()
        
        sender.send(f"{LIGHTGREEN_EX + Colors.BOLD}Changed Description to {CYAN}{desc}{RESET + Colors.RESET}")
        

@register_command("desc")
def desc_command(socket: socket.socket, user: User, args: list, sender: ClientSender):
    cmd_db = Database(server_dir + "/users.db", check_same_thread=False)
    cmd_db.execute("SELECT description FROM users WHERE username = ?", (user.username,))
    desc = cmd_db.fetchone()[0]
    sender.send(f"{LIGHTGREEN_EX + Colors.BOLD}Your current description: {RESET}{desc}{Colors.RESET}")                