from .. import register_command

import socket

from src.colors import *
from src.db import Database

from init import User, ClientSender, server_dir

@register_command("block", arg_count=1)
def block_command(socket: socket.socket, user: User, args: list, sender: ClientSender):
    cmd_db = Database(server_dir + "/users.db", check_same_thread=False)
    
    username = args[0].lower()
    
    if username.lower() == user.username.lower():
        sender.send(f"{YELLOW}{Colors.BOLD}Don't block yourself!{Colors.RESET}")
        return
    
    try:    
        cmd_db.execute("SELECT username FROM users WHERE LOWER(username) = ?", (username.lower(),))
        result = cmd_db.fetchall()

        if result:            
            if "".join(result[0]).lower() == username:
                cmd_db.execute("SELECT blocked_users FROM users WHERE LOWER(username) = ?", (user.username.lower(),))
                blocked_users = cmd_db.fetchall()
                
                if blocked_users[0][0] == None:
                    # blocked_users = "".join(blocked_users[0])
                    blocked_users[0] = (username,)
                    print(blocked_users)
                    print(blocked_users[0])
                    blocked_users = "".join(blocked_users[0])
                    
                    
                else:
                    blocked_users = "".join(blocked_users[0])
                    blocked_users += "," + username 
                
                cmd_db.execute("UPDATE users SET blocked_users = ? WHERE LOWER(username) = ?", (blocked_users, user.username.lower()))
                cmd_db.commit()
                
                sender.send(f"{GREEN}{Colors.BOLD}{username.capitalize()} has been blocked{Colors.RESET}")
                
            else:
                sender.send(f"{RED}{Colors.BOLD}User does not exist{Colors.RESET}")
                
        else:
            sender.send(f"{RED}{Colors.BOLD}User does not exist{Colors.RESET}")
        
    except:
        sender.send(f"{RED}{Colors.BOLD}User does not exist{Colors.RESET}")


@register_command("blocklist", arg_count=0)
def blocklist_command(socket: socket.socket, user: User, args: list, sender: ClientSender):
    cmd_db = Database(server_dir + "/users.db", check_same_thread=False)
        
    cmd_db.execute("SELECT blocked_users FROM users WHERE LOWER(username) = ?", (user.username.lower(),))
    blocked_users = cmd_db.fetchall()
    
    if blocked_users[0][0] == None:
        sender.send(f"{GREEN}{Colors.BOLD}Your Blocklist is empty!{Colors.RESET}")
        return
        
    else:
        blocked_users = "".join(blocked_users[0]).split(",")
        blocked_users = ", ".join(blocked_users)
    
    sender.send(f"{GREEN}{Colors.BOLD}Your Blocklist: {CYAN}{blocked_users}{Colors.RESET}")
    