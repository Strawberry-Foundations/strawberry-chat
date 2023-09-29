from .. import register_command, PermissionLevel

import socket

from src.colors import *
from src.functions import repl_htpf, broadcast_all

from init import users

@register_command("online")
def online_command(socket: socket.socket, username: str, args: list):
    onlineUsers = ', '.join([user for user in sorted(users.values())])
    onlineUsersLen2 = len([user for user in sorted(users.values())])
    socket.send(f"""{GREEN +  Colors.UNDERLINE + Colors.BOLD}Users who are currently online ({onlineUsersLen2}){RESET + Colors.RESET}
        {Colors.BOLD}->{Colors.RESET} {CYAN}{onlineUsers}{RESET + Colors.RESET}""".encode("utf8"))