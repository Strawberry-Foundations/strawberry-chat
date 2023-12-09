from .. import register_command

import socket

from src.colors import *
from src.functions import broadcast_all
from src.db import Database

from init import User, ClientSender, do_not_disturb, afks, server_dir

@register_command("status", arg_count=1)
def status_command(socket: socket.socket, user: User, args: list, sender: ClientSender):
    cmd_db = Database(server_dir + "/users.db", check_same_thread=False)
    
    match args[0]:
        case "set":
            match args[1]:
                case "afk":
                    sender.send(f"{BGREEN}Status set to {YELLOW}afk{CRESET}")
                    user.set_user_status(User.Status.afk)
                    
                case "afk":
                    sender.send(f"{BGREEN}Status set to {RED}do not disturb{CRESET}")
                    user.set_user_status(User.Status.dnd)
                    
                case "offline":
                    sender.send(f"{BGREEN}Status set to {GRAY}offline{CRESET}")
                    user.set_user_status(User.Status.offline)
                
                case "online" | "reset":
                    sender.send(f"{BGREEN}Status set to online{CRESET}")
                    user.set_user_status(User.Status.online)
                
                case _:
                    sender.send(f"{BRED}Invalid status type{CRESET}")
                    return
                
        case "get":
            sender.send(f"{BGREEN}Your current status: {user.user_status}{CRESET}")