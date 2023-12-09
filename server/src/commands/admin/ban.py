from .. import register_command, PermissionLevel

import socket

from src.colors import *
from src.functions import doesUserExist
from src.db import Database

from init import User, ClientSender, server_dir, log

@register_command("ban", arg_count=1, required_permissions=PermissionLevel.ADMIN)
def ban_command(socket: socket.socket, user: User, args: list, sender: ClientSender):
    cmd_db = Database(server_dir + "/users.db", check_same_thread=False)

    uname = args[0]

    if doesUserExist(uname) == False:
        sender.send(f"{RED + Colors.BOLD}Sorry, this user does not exist!{RESET + Colors.RESET}")
    
    else:
        cmd_db.execute("UPDATE users SET account_enabled = 'false' WHERE username = ?", (uname,))
        cmd_db.commit()

        sender.send(f"{LIGHTGREEN_EX + Colors.BOLD}Banned {uname}{RESET + Colors.RESET}")
        log.info(f"{uname} has been banned by {user.username}")

@register_command("unban", arg_count=1, required_permissions=PermissionLevel.ADMIN)
def unban_command(socket: socket.socket, user: User, args: list, sender: ClientSender):
    cmd_db = Database(server_dir + "/users.db", check_same_thread=False)

    uname = args[0]

    if doesUserExist(uname) == False:
        sender.send(f"{RED + Colors.BOLD}Sorry, this user does not exist!{RESET + Colors.RESET}")
    
    else:
        cmd_db.execute("UPDATE users SET account_enabled = 'true' WHERE username = ?", (uname,))
        cmd_db.commit()

        sender.send(f"{LIGHTGREEN_EX + Colors.BOLD}Unbanned {uname}{RESET + Colors.RESET}")
        log.info(f"{uname} has been unbanned by {user.username}")