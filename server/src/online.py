import requests
from src.vars import full_ver, chat_name, update_channel
from src.colors import * 
from init import update_channel as online_update_channel

response = requests.get('https://api.strawberryfoundations.xyz/v1/versions')
data = response.json()

online_ver = data['stbchat']['server'][online_update_channel]

def update():
    print(f"{Colors.BOLD + GREEN}An update for {chat_name} is available.{RESET + Colors.RESET}\n")
    print(f"{Colors.BOLD + CYAN}strawberry-chat{GREEN}@{MAGENTA + online_update_channel} {RESET}{online_ver}{Colors.RESET}")
    print(f"↳ Upgrading from {CYAN + Colors.BOLD}strawberry-chat{GREEN}@{MAGENTA + update_channel} {RESET}{full_ver}{Colors.RESET}")

def check_for_updates(subcommand_arg):
    if subcommand_arg != "--force":
        if online_ver == full_ver:
            print(f"{Colors.BOLD + GREEN}You are on the latest version! ({online_ver}){RESET + Colors.RESET}")
            
        else:
            update()
    
    else:
        update()