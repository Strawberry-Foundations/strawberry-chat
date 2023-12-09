from .. import register_command, PermissionLevel

import socket

from src.colors import *
from src.functions import doesUserExist
from src.db import Database

from init import User, ClientSender, server_dir, log

@register_command("mute", arg_count=1, required_permissions=PermissionLevel.ADMIN)
def mute_command(socket: socket.socket, user: User, args: list, sender: ClientSender):
    cmd_db = Database(server_dir + "/users.db", check_same_thread=False)

    uname = args[0]

    if doesUserExist(uname) == False:
        sender.send(f"{RED + Colors.BOLD}Sorry, this user does not exist!{RESET + Colors.RESET}")
    
    else:
        cmd_db.execute("UPDATE users SET muted = 'true' WHERE username = ?", (uname,))
        cmd_db.commit()

        sender.send(f"{LIGHTGREEN_EX + Colors.BOLD}Muted {uname}{RESET + Colors.RESET}")
        log.info(f"{uname} has been muted by {user.username}")

@register_command("unmute", arg_count=1, required_permissions=PermissionLevel.ADMIN)
def unmute_command(socket: socket.socket, user: User, args: list, sender: ClientSender):
    cmd_db = Database(server_dir + "/users.db", check_same_thread=False)

    uname = args[0]

    if doesUserExist(uname) == False:
        sender.send(f"{RED + Colors.BOLD}Sorry, this user does not exist!{RESET + Colors.RESET}")
    
    else:
        cmd_db.execute("UPDATE users SET muted = 'false' WHERE username = ?", (uname,))
        cmd_db.commit()

        sender.send(f"{LIGHTGREEN_EX + Colors.BOLD}Unmuted {uname}{RESET + Colors.RESET}")
        log.info(f"{uname} has been unmuted by {user.username}")
