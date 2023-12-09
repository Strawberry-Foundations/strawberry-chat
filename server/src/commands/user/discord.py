from .. import register_command

import socket

from src.colors import *
from src.db import Database

from init import User, ClientSender, server_dir

@register_command("discord", arg_count=1)
def discord_command(socket: socket.socket, user: User, args: list, sender: ClientSender):
    cmd_db = Database(server_dir + "/users.db", check_same_thread=False)
    
    discord_name = args[0]

    if discord_name.lower() == "remove":
        cmd_db.execute("UPDATE users SET discord_name = NULL WHERE username = ?", (user.username,))
        cmd_db.commit()
        
        sender.send(f"{LIGHTGREEN_EX + Colors.BOLD}Removed Discord Link{RESET + Colors.RESET}")

    else:
        cmd_db.execute("UPDATE users SET discord_name = ? WHERE username = ?", (discord_name, user.username))
        cmd_db.commit()
        
        sender.send(f"{LIGHTGREEN_EX + Colors.BOLD}Changed Discord Link to {MAGENTA}{discord_name}{RESET + Colors.RESET}")   