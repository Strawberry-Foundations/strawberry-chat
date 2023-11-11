from .. import register_command, PermissionLevel

import socket
import time

from src.colors import *
from src.functions import repl_htpf, broadcast_all
from init import addresses, users

@register_command("debug", arg_count=0, required_permissions=PermissionLevel.ADMIN)
def debug_command(socket: socket.socket, username: str, args: list, send):
    socket.send(f"""Client Object: {socket}
        IP Object: {addresses[socket]}
        User Object: {users[socket]}
        Addresses: {addresses}
        Users: {users}""".encode("utf8"))
    
@register_command("clientinfo", arg_count=0, required_permissions=PermissionLevel.MEMBER)
def clientinfo_command(socket: socket.socket, username: str, args: list, send):
    socket.send(f"{addresses[socket]}".encode("utf8"))
    time.sleep(0.1)
    socket.send(f"{users[socket]}".encode("utf8"))
    time.sleep(0.1)
    socket.send(f"{socket}".encode("utf8"))