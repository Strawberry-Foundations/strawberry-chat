from .. import register_command

import socket
import yaml

from src.colors import *
from yaml import SafeLoader
from init import server_dir

# Open Configuration
with open(server_dir + "/config.yml") as config_data:
        config = yaml.load(config_data, Loader=SafeLoader)

@register_command("server-info")
@register_command("info")
@register_command("server-desc")
@register_command("server-description")
def help_command(socket: socket.socket, username: str, args: list):
    desc = config['server']['description']
    socket.send(f"{WHITE + Colors.BOLD}{desc}{RESET + Colors.RESET}".encode("utf8"))