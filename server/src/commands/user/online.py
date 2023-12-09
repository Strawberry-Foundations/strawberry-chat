from .. import register_command

import socket

from src.colors import *

from init import ClientSender, users, max_users

@register_command("online")
def online_command(socket: socket.socket, user, args: list, sender: ClientSender):
    onlineUsers = ', '.join([user for user in sorted(users.values())])
    onlineUsersLen2 = len([user for user in sorted(users.values())])
    
    _online_users = f"({onlineUsersLen2}/{max_users})"
    if max_users == -1: _online_users = f"({onlineUsersLen2})"
    
    sender.send(f"""{GREEN +  Colors.UNDERLINE + Colors.BOLD}Users who are currently online {_online_users}{RESET + Colors.RESET}
        {Colors.BOLD}->{Colors.RESET} {CYAN}{onlineUsers}{RESET + Colors.RESET}""")