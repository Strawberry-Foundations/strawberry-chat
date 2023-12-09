from .. import register_command, PermissionLevel

import socket
import time

from src.colors import *
from src.functions import send_json
from init import User, ClientSender

@register_command("debug", arg_count=0, required_permissions=PermissionLevel.ADMIN)
def backend_debug_command(socket: socket.socket, user: User, args: list, sender: ClientSender):
    backend_builder = {
                        "message_type": "stbchat_backend",
                        "user_meta": {
                            "username": user.username
                        }
                    }
                
    socket.send(send_json(backend_builder).encode("utf-8"))
    