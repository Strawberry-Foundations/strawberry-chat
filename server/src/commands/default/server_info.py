from .. import register_command

import socket
import yaml

from src.colors import *
from yaml import SafeLoader
from init import User, ClientSender, server_dir

# Open Configuration
with open(server_dir + "/config.yml") as config_data:
        config = yaml.load(config_data, Loader=SafeLoader)

@register_command("server-info")
@register_command("serverinfo")
@register_command("info")
@register_command("server-desc")
@register_command("server-description")
def server_info_command(socket: socket.socket, user: User, args: list, sender: ClientSender):
    desc = config['server']['description']
    sender.send(f"{WHITE + Colors.BOLD}{desc}{RESET + Colors.RESET}")