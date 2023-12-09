from .. import register_command

import socket

from src.colors import *
from src.functions import broadcast_all

from init import User, ClientSender, afks

@register_command("afk")
def afk_command(socket: socket.socket, user: User, args: list, sender: ClientSender):
    if user.username in afks:
        sender.send(f"{YELLOW + Colors.BOLD}You are already AFK!{RESET + Colors.RESET}")
        
    else:
        broadcast_all(f"{user.username} is now AFK 🌙..")
        afks.append(user.username)