from .. import register_command

import socket

from src.colors import *
from src.db import Database

from init import User, ClientSender, server_dir

@register_command("strawberry-id", arg_count=0)
def description_command(socket: socket.socket, user: User, args: list, sender: ClientSender):
    cmd_db = Database(server_dir + "/users.db", check_same_thread=False)
    
    cmd = " ".join(args)
    
    if cmd.lower() == "remove" or cmd.lower() == "reset":
        cmd_db.execute("UPDATE users SET strawberry_id = NULL WHERE username = ?", (user.username,))
        cmd_db.commit()
        
        sender.send(f"{LIGHTGREEN_EX + Colors.BOLD}Removed Strawberry ID Connection{RESET + Colors.RESET}")