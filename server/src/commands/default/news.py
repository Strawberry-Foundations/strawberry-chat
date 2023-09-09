from .. import register_command

import socket
import yaml

from src.vars import chat_name, short_ver, base_ver
from src.colors import *
from yaml import SafeLoader
from init import server_dir

# Open news
with open(server_dir + "/news.yml") as news_file:
    news_data = yaml.load(news_file, Loader=SafeLoader)

news = f"""{GREEN +  Colors.UNDERLINE + Colors.BOLD}{chat_name} News - {short_ver}{RESET + Colors.RESET}{CYAN + Colors.BOLD}
{news_data['news'][base_ver]['text']}{RESET + Colors.RESET}"""

@register_command("news")
def help_command(socket: socket.socket, username: str, args: list):
    socket.send(news.encode("utf8"))