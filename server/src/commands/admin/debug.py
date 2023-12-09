from .. import register_command, PermissionLevel

import socket
import time

from src.colors import *
from src.functions import replace_htpf, broadcast_all
from init import User, ClientSender, addresses, users

@register_command("debug", arg_count=0, required_permissions=PermissionLevel.ADMIN)
def debug_command(socket: socket.socket, user: User, args: list, sender: ClientSender):
    sender.send(f"""Client Object: {socket}
        IP Object: {addresses[socket]}
        User Object: {users[socket]}
        Addresses: {addresses}
        Users: {users}""")
    
@register_command("clientinfo", arg_count=0, required_permissions=PermissionLevel.MEMBER)
def clientinfo_command(socket: socket.socket, user: User, args: list, sender: ClientSender):
    sender.send(f"{addresses[socket]}")
    time.sleep(0.1)
    sender.send(f"{users[socket]}")
    time.sleep(0.1)
    sender.send(f"{socket}")