from .. import register_command

import socket

from src.colors import *
from src.functions import broadcast_all

from init import afks

@register_command("unafk")
def unafk_command(socket: socket.socket, username: str, args: list, send):
    if username not in afks:
        socket.send(f"{YELLOW + Colors.BOLD}You are not AFK!{RESET + Colors.RESET}".encode("utf8"))

    else:
        broadcast_all(f"{username} is no longer AFK 🌻!")
        afks.remove(username)