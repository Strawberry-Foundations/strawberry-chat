import requests
from src.vars import short_ver
from src.colors import * 

# Receive your global ip address for verification
def get_global_ip():
    response = requests.get('https://api.ipify.org?format=json')
    data = response.json()
    return data['ip']

def check_for_updates():
    response = requests.get('https://api.strawberryfoundations.xyz/v1/versions')
    data = response.json()
    
    if data['strawberry-chat'] == short_ver:
        print(f"{Colors.BOLD + GREEN}You are on the latest version! ({data['strawberry-chat']}){RESET + Colors.RESET}")
    else:
        print(f"{Colors.BOLD + GREEN}An update is available.{RESET + Colors.RESET}")
        print(f"{Colors.BOLD}strawberry-chat {short_ver} -> {data['strawberry-chat']}{RESET + Colors.RESET}")
    
    # return data['strawberry-chat']