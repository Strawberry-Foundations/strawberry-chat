from .. import register_command, PermissionLevel

import socket

from src.colors import *
from src.functions import replace_htpf, broadcast_all

@register_command("broadcast", arg_count=1, required_permissions=PermissionLevel.ADMIN)
@register_command("rawsay", arg_count=1, required_permissions=PermissionLevel.ADMIN)
def broadcast_command(socket: socket.socket, user, args: list, sender):
    text = " ".join(args)
    text = replace_htpf(text)
    broadcast_all(f"{text}{RESET}")