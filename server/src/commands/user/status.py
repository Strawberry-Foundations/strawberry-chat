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
                    
                case "dnd":
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
            sender.send(f"{BGREEN}Your current status: {user.status}{CRESET}")
            
        case "system_register":
            sender.send(user.get_system_register())
            
@register_command("afk")
def afk_command(socket: socket.socket, user: User, args: list, sender: ClientSender):
    if user.status == User.Status.afk:
        sender.send(f"{YELLOW + Colors.BOLD}You are already AFK!{RESET + Colors.RESET}")
    else:
        sender.send(f"{BGREEN}Status set to {YELLOW}afk{CRESET}")
        user.set_user_status(User.Status.afk)
        
@register_command("unafk")
def unafk_command(socket: socket.socket, user: User, args: list, sender: ClientSender):
    if user.username not in afks:
        sender.send(f"{YELLOW + Colors.BOLD}You are not AFK!{RESET + Colors.RESET}")

    else:
        broadcast_all(f"{user.username} is no longer AFK 🌻!")
        afks.remove(user.username)
        
@register_command("afks")
@register_command("afklist")
def afklist_command(socket: socket.socket, user: User, args: list, sender: ClientSender):
    afkUsers = ', '.join([afks for afks in sorted(afks)])
    afkUsersLen = len([afks for afks in sorted(afks)])
    sender.send(f"""{GREEN +  Colors.UNDERLINE + Colors.BOLD}Users who are currently Afk ({afkUsersLen}){RESET + Colors.RESET}
        {Colors.BOLD}->{Colors.RESET} {CYAN}{afkUsers}{RESET}""")