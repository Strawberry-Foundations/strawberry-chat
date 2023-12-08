from .. import register_command

import socket as _socket

from src.colors import *
from src.db import Database

from init import server_dir, users, afks, StbCom, user_dm_screen
from src.functions import escape_ansi, userRoleColor, send_json

@register_command("dm", arg_count=2)
def dm_command(socket: _socket.socket, username: str, args: list, send):
    cmd_db = Database(server_dir + "/users.db", check_same_thread=False)

    uname   = args[0]
    msg     = ' '.join(args[1:])
    msg     = escape_ansi(msg)
    msg     = msg.strip("\n")
    
    found_keys = []
    
    for sock_object, sock_uname in users.items():
        if sock_uname.lower() == uname.lower():
            global to_sent
            to_sent = sock_object
            found_keys.append(sock_object)
            
    
    try:
        cmd_db.execute("SELECT enable_dms FROM users WHERE username = ?", (username,))
        has_dm_enabled = cmd_db.fetchone()[0]
        
    except:
        send(f"{RED + Colors.BOLD}User not found{RESET + Colors.RESET}")
        has_dm_enabled = "false"
    
    if uname == username:
        send(f"{YELLOW}You shouldn't send messages to yourself...{RESET}")
    
    elif uname in afks:
        send(f"{YELLOW}This user is currently afk...{RESET}")
    
    elif has_dm_enabled == "false":
        send(f"{YELLOW}This user has deactivated his/her DM's{RESET}")
    
    else:
        if found_keys:
            send(f"{userRoleColor(username)}You{RESET} {Colors.GRAY}-->{Colors.RESET} {userRoleColor(uname)}{uname}{RESET + Colors.RESET}: {msg}")
            
            try:
                _to_sent_dmscreen = user_dm_screen[uname]
            except KeyError:
                _to_sent_dmscreen = ""
                
            
            if _to_sent_dmscreen == username:
                json_builder = {
                    "message_type": StbCom.SYS_MSG,
                    "message": {
                        "content": f"{Colors.GRAY}[{Colors.RESET}{userRoleColor(username)}{username}'s DM{RESET + Colors.RESET + Colors.GRAY}]{Colors.RESET} {userRoleColor(username)}{username}{RESET}{Colors.GRAY}:{Colors.RESET} {msg}"
                        }
                }
                
                to_sent.send(send_json(json_builder).encode("utf-8"))  
            
            else:
                json_builder = {
                    "message_type": StbCom.SYS_MSG,
                    "message": {
                        "content": f"{Colors.RESET + userRoleColor(username)}{username} {Colors.GRAY}-->{RESET + Colors.RESET}{userRoleColor(uname)} You{Colors.RESET + RESET}: {msg}"
                        }
                }
                
                to_sent.send(send_json(json_builder).encode("utf-8"))
            
        else:
            send(f"{RED + Colors.BOLD}User is offline.{RESET + Colors.RESET}")
    
@register_command("joindm", arg_count=1)
def dm_command(socket: _socket.socket, username: str, args: list, send):
    cmd_db = Database(server_dir + "/users.db", check_same_thread=False)
    
    _to_sent = args[0]
    found_keys = []
    to_sent = {}
    
    for sock_object, sock_uname in users.items():
        if sock_uname.lower() == _to_sent.lower():
            to_sent[username] = sock_object
            found_keys.append(sock_object)
            
    try:
        cmd_db.execute("SELECT enable_dms FROM users WHERE username = ?", (username,))
        has_dm_enabled = cmd_db.fetchone()[0]
        
    except:
        send(f"{RED + Colors.BOLD}User not found{RESET + Colors.RESET}")
        has_dm_enabled = "false"
    
    if _to_sent == username:
        send(f"{YELLOW}You shouldn't send messages to yourself...{RESET}")
        
    elif _to_sent in afks:
        send(f"{YELLOW}This user is currently afk...{RESET}")    
        
    elif has_dm_enabled == "false":
        send(f"{YELLOW}This user has deactivated his/her DM's{RESET}")
    
    else:
        if found_keys:
            user_dm_screen[username] = _to_sent
            
            send(f"{GREEN + Colors.BOLD}You're now on {_to_sent}'s DM page!{Colors.RESET}")
            
            while True:
                try:
                    msg = socket.recv(2048).decode("utf8")
                        
                    if len(msg) == 0:
                        return
                    
                    if msg == "/exit":
                        send(f"{YELLOW + Colors.BOLD}You left {_to_sent}'s DM page!{Colors.RESET}")
                        break
                        
                    
                    send(f"{Colors.GRAY}[{Colors.RESET}{userRoleColor(_to_sent)}{_to_sent}'s DM{RESET + Colors.RESET + Colors.GRAY}]{Colors.RESET} {userRoleColor(username)}You{RESET}{Colors.GRAY}:{Colors.RESET} {msg}")
                    
                    
                    try:
                        _to_sent_dmscreen = user_dm_screen[_to_sent]
                    except KeyError:
                        _to_sent_dmscreen = ""
                    
                    if _to_sent_dmscreen == username:
                        json_builder = {
                            "message_type": StbCom.SYS_MSG,
                            "message": {
                                "content": f"{Colors.GRAY}[{Colors.RESET}{userRoleColor(username)}{username}'s DM{RESET + Colors.RESET + Colors.GRAY}]{Colors.RESET} {userRoleColor(username)}{username}{RESET}{Colors.GRAY}:{Colors.RESET} {msg}"
                                }
                        }
                        
                        to_sent[username].send(send_json(json_builder).encode("utf-8"))  
                        
                    
                    else:
                        json_builder = {
                            "message_type": StbCom.SYS_MSG,
                            "message": {
                                "content": f"{Colors.RESET + userRoleColor(username)}{username} {Colors.GRAY}-->{RESET + Colors.RESET}{userRoleColor(_to_sent)} You{Colors.RESET + RESET}: {msg}"
                                }
                        }
                        
                        to_sent[username].send(send_json(json_builder).encode("utf-8"))

                except OSError:
                    return
                
        else:
            send(f"{RED + Colors.BOLD}User is offline.{RESET + Colors.RESET}")
        