from .. import register_command, PermissionLevel

import socket

from src.colors import *
from src.functions import doesUserExist
from src.db import Database

from init import server_dir, log, queue

@register_command("queue", arg_count=1, required_permissions=PermissionLevel.ADMIN)
def queue_command(socket: socket.socket, username: str, args: list, send):
    cmd_db = Database(server_dir + "/users.db", check_same_thread=False)

    uname = args[0]
    
    match args[0]:
        case "remove":
            queue.remove()