from .. import register_command

import socket

from src.colors import *
from src.functions import broadcast_all

from init import User, ClientSender, do_not_disturb

@register_command("dnd")
def dnd_command(socket: socket.socket, user: User, args: list, sender: ClientSender):
    if user.username in do_not_disturb:
        sender.send(f"{YELLOW + Colors.BOLD}You are already in Do not Disturb!{RESET + Colors.RESET}")
        
    else:
        do_not_disturb.append(user.username)
        sender.send(f"{GREEN + Colors.BOLD}You're now in Do not Disturb!{RESET + Colors.RESET}")
        
@register_command("undnd")
def undnd_command(socket: socket.socket, user: User, args: list, sender: ClientSender):
    if user.username not in do_not_disturb:
        sender.send(f"{YELLOW + Colors.BOLD}You are not in Do not Disturb!{RESET + Colors.RESET}")

    else:
        do_not_disturb.remove(user.username)
        sender.send(f"{GREEN + Colors.BOLD}You're no longer in Do not Disturb!{RESET + Colors.RESET}")
        
# @register_command("afks")
# @register_command("afklist")
# def afklist_command(socket: socket.socket, user: User, args: list, sender: ClientSender):
#     afkUsers = ', '.join([afks for afks in sorted(afks)])
#     afkUsersLen = len([afks for afks in sorted(afks)])
#     sender.send(f"""{GREEN +  Colors.UNDERLINE + Colors.BOLD}Users who are currently Afk ({afkUsersLen}){RESET + Colors.RESET}
#         {Colors.BOLD}->{Colors.RESET} {CYAN}{afkUsers}{RESET}""")