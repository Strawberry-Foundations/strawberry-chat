from .. import register_command, PermissionLevel

import socket

from src.colors import *
from src.functions import repl_htpf, broadcast_all

from init import afks

@register_command("afks")
@register_command("afklist")
def afklist_command(socket: socket.socket, username: str, args: list):
    afkUsers = ', '.join([afks for afks in sorted(afks)])
    afkUsersLen = len([afks for afks in sorted(afks)])
    socket.send(f"""{GREEN +  Colors.UNDERLINE + Colors.BOLD}Users who are currently Afk ({afkUsersLen}){RESET + Colors.RESET}
        {Colors.BOLD}->{Colors.RESET} {CYAN}{afkUsers}{RESET}""".encode("utf8"))