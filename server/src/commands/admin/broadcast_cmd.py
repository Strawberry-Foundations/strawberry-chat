from .. import register_command, PermissionLevel

import socket

from src.colors import *
from src.functions import repl_htpf, broadcast_all

@register_command("broadcast", arg_count=1, required_permissions=PermissionLevel.ADMIN)
@register_command("rawsay", arg_count=1, required_permissions=PermissionLevel.ADMIN)
def broadcast_command(socket: socket.socket, username: str, args: list, send):
    text = " ".join(args)
    text = repl_htpf(text)
    broadcast_all(f"{text}{RESET}")