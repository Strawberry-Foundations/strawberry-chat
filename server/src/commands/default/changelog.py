from .. import register_command

import socket
import yaml

from src.vars import chat_name
from src.colors import *
from yaml import SafeLoader
from init import server_dir

# Open Configuration
with open(server_dir + "/config.yml") as config_data:
        config = yaml.load(config_data, Loader=SafeLoader)

@register_command("changelog")
def changelog_command(socket: socket.socket, username: str, args: list):
    with open(server_dir + "/CHANGELOG.txt") as f:
        changelog = f.read()
        socket.send(f"{GREEN + Colors.BOLD + Colors.UNDERLINE}{chat_name} Changelog{RESET + Colors.RESET}".encode("utf8"))
        socket.send((Colors.BOLD + changelog + Colors.RESET).encode("utf8"))