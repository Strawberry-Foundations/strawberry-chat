from .. import register_command, PermissionLevel

import socket

from src.colors import *
from src.functions import doesUserExist
from src.db import Database

from init import server_dir

@register_command("unmute", arg_count=1, required_permissions=PermissionLevel.ADMIN)
def unmute_command(socket: socket.socket, username: str, args: list):
    cmd_db = Database(server_dir + "/users.db", check_same_thread=False)

    uname = args[0]

    if doesUserExist(uname) == False:
        socket.send(f"{RED + Colors.BOLD}Sorry, this user does not exist!{RESET + Colors.RESET}".encode("utf8"))
    
    else:
        cmd_db.execute("UPDATE users SET muted = 'false' WHERE username = ?", (uname,))
        cmd_db.commit()

        socket.send(f"{LIGHTGREEN_EX + Colors.BOLD}Unmuted {uname}{RESET + Colors.RESET}".encode("utf8"))
