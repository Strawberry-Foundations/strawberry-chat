from .. import register_command

import socket
import sqlite3 as sql

from src.colors import *
from src.db import Database

from init import User, ClientSender, server_dir, log

@register_command("block", arg_count=1)
def block_command(socket: socket.socket, user: User, args: list, sender: ClientSender):
    db = sql.connect(server_dir + "/users.db", check_same_thread=False)
    c = db.cursor()
    
    username = args[0].lower()
    
    if username == user.username.lower():
        sender.send(f"{YELLOW}{Colors.BOLD}Don't block yourself!{Colors.RESET}")
        return
    
    try:    
        c.execute("SELECT username FROM users WHERE LOWER(username) = ?", (username,))
        result = c.fetchall()

        if result:            
            if "".join(result[0]).lower() == username:
                c.execute("SELECT blocked_users FROM users WHERE LOWER(username) = ?", (user.username.lower(),))
                blocked_users = c.fetchall()
                
                if blocked_users[0][0] == None:
                    blocked_users[0] = (username,)
                    blocked_users = "".join(blocked_users[0])
                    
                else:
                    blocked_users_list = blocked_users[0][0].split(",")
                
                    if username in blocked_users_list:
                        sender.send(f"{YELLOW}{Colors.BOLD}This user is already blocked!{Colors.RESET}")
                        return
                
                    blocked_users = "".join(blocked_users[0])
                    blocked_users += "," + username 
                    
                with db:
                    db.execute("UPDATE users SET blocked_users = ? WHERE LOWER(username) = ?", (blocked_users, user.username.lower()))
                # cmd_db.commit()
                
                sender.send(f"{GREEN}{Colors.BOLD}{username.capitalize()} has been blocked{Colors.RESET}")
                
            else:
                sender.send(f"{RED}{Colors.BOLD}User does not exist{Colors.RESET}")
                
        else:
            sender.send(f"{RED}{Colors.BOLD}User does not exist{Colors.RESET}")
            
    except Exception as e:
        sender.send(f"{RED}{Colors.BOLD}User does not exist{Colors.RESET}")
        log.info(f"Exception in blocked_users: {e}")


@register_command("unblock", arg_count=1)
def unblock_command(socket: socket.socket, user: User, args: list, sender: ClientSender):
    db = sql.connect(server_dir + "/users.db", check_same_thread=False)
    c = db.cursor()
    
    username = args[0].lower()
    
    if username.lower() == user.username.lower():
        sender.send(f"{YELLOW}{Colors.BOLD}You cannot unblock yourself..{Colors.RESET}")
        return
    
    try:    
        c.execute("SELECT username FROM users WHERE LOWER(username) = ?", (username,))
        result = c.fetchall()

        if result:            
            if "".join(result[0]).lower() == username:
                c.execute("SELECT blocked_users FROM users WHERE LOWER(username) = ?", (user.username.lower(),))
                blocked_users = c.fetchall()
                
                if blocked_users[0][0] == None:
                    sender.send(f"{GREEN}{Colors.BOLD}Your Blocklist is empty!{Colors.RESET}")
                    return
                    
                else:
                    blocked_users_list = blocked_users[0][0].split(",")
                
                    if username not in blocked_users_list:
                        sender.send(f"{YELLOW}{Colors.BOLD}This user is not blocked{Colors.RESET}")
                        return
                    
                    if len(blocked_users[0]) == 1:
                        with db:
                            db.execute("UPDATE users SET blocked_users = NULL WHERE LOWER(username) = ?", (user.username.lower(),))
                        # cmd_db.commit()
                        
                        
                    else:
                        blocked_users_list.remove(username)
                        print(",".join(blocked_users_list))
                        
                        blocked_users = ",".join(blocked_users_list)

                        with db:
                            db.execute("UPDATE users SET blocked_users = ? WHERE LOWER(username) = ?", (blocked_users, user.username.lower()))
                        # cmd_db.commit()

                sender.send(f"{GREEN}{Colors.BOLD}{username.capitalize()} has been unblocked{Colors.RESET}")
                
            else:
                sender.send(f"{RED}{Colors.BOLD}User does not exist{Colors.RESET}")
                
        else:
            sender.send(f"{RED}{Colors.BOLD}User does not exist{Colors.RESET}")
            
    except Exception as e:
        sender.send(f"{RED}{Colors.BOLD}User does not exist{Colors.RESET}")
        log.info(f"Exception in blocked_users: {e}")


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
    