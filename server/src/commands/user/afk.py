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