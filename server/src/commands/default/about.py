from .. import register_command

import socket
import yaml

from src.vars import chat_name, short_ver, codename, server_edition, authors, ext_ver
from src.colors import *
from yaml import SafeLoader
from init import server_dir, User, ClientSender

# Open Configuration
with open(server_dir + "/config.yml") as config_data:
        config = yaml.load(config_data, Loader=SafeLoader)

@register_command("about")
def about_command(socket: socket.socket, user: User, args: list, sender: ClientSender):
    sender.send(f"""{GREEN +  Colors.UNDERLINE + Colors.BOLD}About {chat_name}{RESET + Colors.RESET}
        {BLUE + Colors.BOLD}Thank you for using {chat_name}!{RESET}
        {BLUE + Colors.BOLD}Version: {RESET}{short_ver} {codename} ({server_edition}) ({ext_ver})
        {BLUE + Colors.BOLD}Author: {RESET}{", ".join(authors)}{RESET + Colors.RESET}""")