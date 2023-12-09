from .. import register_command

import socket

from src.colors import *
from src.functions import broadcast_all

from init import User, ClientSender, do_not_disturb, afks

@register_command("status", arg_count=1)
def status_command(socket: socket.socket, user: User, args: list, sender: ClientSender):
    match args[0]:
        case "set":
            pass