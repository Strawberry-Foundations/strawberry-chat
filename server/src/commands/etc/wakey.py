import socket
from .. import register_command

from src.colors import *
from src.functions import send_json, broadcast_all

from init import StbCom, User, ClientSender, users


@register_command("wakey", 0)
def test_command(socket: socket.socket, user: User, args: list, sender: ClientSender):
    if len(args) == 1:
        uname   = args[0]
    
        found_keys = []
        
        for sock_object, sock_uname in users.items():
            if sock_uname.lower() == uname.lower():
                global to_sent
                to_sent = sock_object
                found_keys.append(sock_object)
                
        
        if found_keys:
            sender.send(f"{Colors.BOLD + GREEN}Send Wakey wakey to {uname}{Colors.RESET}")
            
            json_builder = {
                "message_type": StbCom.SYS_MSG,
                "message": {
                    "content": f"{Colors.ITALIC + YELLOW}Wakey, wakey ...{Colors.RESET}\a"
                    }
            }
            
            to_sent.send(send_json(json_builder).encode("utf-8"))  
        
            
        else:
            sender.send(f"{RED + Colors.BOLD}User is offline.{RESET + Colors.RESET}")
            
    else:
        broadcast_all(f"{Colors.ITALIC + YELLOW}Wakey, wakey ...{Colors.RESET}\a")