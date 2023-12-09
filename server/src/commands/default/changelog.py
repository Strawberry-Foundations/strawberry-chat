from .. import register_command

import socket

from src.vars import chat_name
from src.colors import *
from init import server_dir, User, ClientSender

@register_command("changelog")
def changelog_command(socket: socket.socket, user: User, args: list, sender: ClientSender):
    with open(server_dir + "/CHANGELOG.txt") as f:
        changelog = f.read()
        sender.send(f"{GREEN + Colors.BOLD + Colors.UNDERLINE}{chat_name} Changelog{RESET + Colors.RESET}")
        sender.send((Colors.BOLD + changelog + Colors.RESET))