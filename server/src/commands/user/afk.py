from .. import register_command

import socket

from src.colors import *
from src.functions import broadcast_all

from init import afks

@register_command("afk")
def afk_command(socket: socket.socket, username: str, args: list, send):
    if username in afks:
        send(f"{YELLOW + Colors.BOLD}You are already AFK!{RESET + Colors.RESET}")
        
    else:
        broadcast_all(f"{username} is now AFK 🌙..")
        afks.append(username)