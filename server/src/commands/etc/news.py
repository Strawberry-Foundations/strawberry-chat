from .. import register_command

import socket
import yaml

from src.vars import chat_name, short_ver, base_ver
from src.colors import *
from yaml import SafeLoader
from init import User, ClientSender, server_dir


@register_command("news")
def about_command(socket: socket.socket, user: User, args: list, sender: ClientSender):
    # Open Configuration
    with open(server_dir + "/news.yml") as config_data:
            news_data = yaml.load(config_data, Loader=SafeLoader)
        
    news = f"""{GREEN +  Colors.UNDERLINE + Colors.BOLD}{chat_name} News - {short_ver}{RESET + Colors.RESET}{CYAN + Colors.BOLD}
{news_data['news'][base_ver]['text']}{RESET + Colors.RESET}"""
    
    try: cmd = args[0]
    except: cmd = ""
    
    if cmd == "list":
        version_list = ", ".join(news_data['versions'])
        sender.send(f"{CYAN + Colors.BOLD}{chat_name} Versions:{RESET + Colors.RESET} {GREEN}{version_list}{RESET}")
        
    elif cmd == "show":
        try:
            i_ver = args[1] 
            sender.send(f"{GREEN + Colors.BOLD + Colors.UNDERLINE}{chat_name} News - v{i_ver}{RESET + Colors.RESET + CYAN + Colors.BOLD}\n{news_data['news'][i_ver]['text']}{RESET + Colors.RESET}")
            
        except:
            sender.send(f"{RED + Colors.BOLD}This version of {chat_name} does not exist.{RESET + Colors.RESET}")
            
    
    else:
        sender.send(f"{news}")