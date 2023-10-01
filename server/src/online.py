import requests
from src.vars import full_ver, chat_name, update_channel, api
from src.colors import * 
from init import update_channel as online_update_channel

def fetch_update_data():
    response = requests.get(api + 'versions')
    data = response.json()
    update_data = data['stbchat']['server'][online_update_channel]
    
    return update_data

def update():
    online_ver = fetch_update_data()
    
    print(f"{Colors.BOLD + GREEN}An update for {chat_name} is available.{RESET + Colors.RESET}\n")
    print(f"{Colors.BOLD + CYAN}strawberry-chat{GREEN}@{MAGENTA + online_update_channel} {RESET}{online_ver}{Colors.RESET}")
    print(f"↳ Upgrading from {CYAN + Colors.BOLD}strawberry-chat{GREEN}@{MAGENTA + update_channel} {RESET}{full_ver}{Colors.RESET}\n")
    
    w_cont = input(f"{Colors.BOLD}Do you want to continue? {CYAN}[Y/N]{RESET}: {GREEN}")
    
    if w_cont.lower() in ["y", "yes"]:
        print(f"{RESET + Colors.RESET}→ Starting strawberry-chat update ...{Colors.RESET}")
        
    else:
        print(f"{YELLOW}Cancelling update process...{RESET}")

def check_for_updates(subcommand_arg):
    online_ver = fetch_update_data()
    
    if subcommand_arg != "--force":
        if online_ver == full_ver:
            print(f"{Colors.BOLD + GREEN}You are on the latest version! ({online_ver}){RESET + Colors.RESET}")
            
        else:
            update()
    
    else:
        update()