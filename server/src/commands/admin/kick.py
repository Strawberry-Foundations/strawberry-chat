from .. import register_command, PermissionLevel

import socket

from src.colors import *
from src.functions import doesUserExist
from src.db import Database

from init import server_dir

@register_command("kick", arg_count=2, required_permissions=PermissionLevel.ADMIN)
def kick_command(socket: socket.socket, username: str, args: list):
    cmd_db = Database(server_dir + "/users.db", check_same_thread=False)
    
    uname   = args[0]
    reason  = ' '.join(args[1:])

    uname = args[0]

    if doesUserExist(uname) == False:
        socket.send(f"{RED + Colors.BOLD}Sorry, this user does not exist!{RESET + Colors.RESET}".encode("utf8"))
    
    else:
        cmd_db.execute("UPDATE users SET muted = 'true' WHERE username = ?", (uname,))
        cmd_db.commit()

        socket.send(f"{LIGHTGREEN_EX + Colors.BOLD}Muted {uname}{RESET + Colors.RESET}".encode("utf8"))
