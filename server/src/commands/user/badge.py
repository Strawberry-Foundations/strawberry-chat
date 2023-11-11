from .. import register_command, PermissionLevel

import socket

from src.colors import *
from src.db import Database
from src.vars import role_colors

from init import server_dir, log, debug_logger, stbexceptions
from src.functions import doesUserExist

@register_command("badge", arg_count=1)
def badge_command(socket: socket.socket, username: str, args: list):
    cmd_db = Database(server_dir + "/users.db", check_same_thread=False)

    cmd = args[0]

    try: 
        cmd_db.execute('SELECT role FROM users WHERE username = ?', (username,))
        
    except Exception as e:
        log.error("An SQL error occured!")
        debug_logger(e, stbexceptions.sql_error)
        
    user_role = cmd_db.fetchone()

    if cmd == "set":
        if len(args) == 3:
            if user_role[0] == "admin":
                try:
                    uname = args[1]
                    badge_to_set = args[2]
                    
                except:
                    socket.send(f"{RED + Colors.BOLD}Please pass a valid argument!{RESET + Colors.RESET}".encode("utf8"))
                    return

                cmd_db.execute("SELECT badges FROM users WHERE username = ?", (uname,))
                
                user_badges = cmd_db.fetchone()[0]            
                
                if not badge_to_set in user_badges:
                    socket.send(f"{RED + Colors.BOLD}This user does not own this badge!{RESET + Colors.RESET}".encode("utf8"))
                    return
                
                cmd_db.execute("UPDATE users SET badge = ? WHERE username = ?", (badge_to_set, uname))
                cmd_db.commit()
                
                socket.send(f"{GREEN + Colors.BOLD}The main badge of {uname} has been updated to '{badge_to_set}'{RESET + Colors.RESET}".encode("utf8"))
            
            else:
                socket.send(f"{RED}Sorry, you do not have permissons for that.{RESET}".encode("utf8"))
                return
        
        elif len(args) == 2:
            try:
                badge_to_set = args[1]
                
            except:
                socket.send(f"{RED + Colors.BOLD}Please pass a valid argument!{RESET + Colors.RESET}".encode("utf8"))
                return

            cmd_db.execute("SELECT badges FROM users WHERE username = ?", (username,))
            
            user_badges = cmd_db.fetchone()[0]            
            
            if not badge_to_set in user_badges:
                socket.send(f"{RED + Colors.BOLD}You do not own this badge!{RESET + Colors.RESET}".encode("utf8"))
                return
            
            cmd_db.execute("UPDATE users SET badge = ? WHERE username = ?", (badge_to_set, username))
            cmd_db.commit()
            
            socket.send(f"{GREEN + Colors.BOLD}Your main badge has been updated to '{badge_to_set}'{RESET + Colors.RESET}".encode("utf8"))            
            
        else: 
            socket.send(f"{RED + Colors.BOLD}Please pass a valid argument!{RESET + Colors.RESET}".encode("utf8"))
    
    
    elif cmd == "add":
        if user_role[0] == "admin":
            if len(args) == 2:
                try:
                    badge_to_add = args[1]
                    
                except:
                    socket.send(f"{RED + Colors.BOLD}Please pass a valid argument!{RESET + Colors.RESET}".encode("utf8"))
                    return
                    
                cmd_db.execute("SELECT badges FROM users WHERE username = ?", (username,))
                
                user_badges = cmd_db.fetchone()[0]
                
                # Does the user already have this badge?
                if badge_to_add in user_badges:
                    socket.send(f"{RED + Colors.BOLD}This badge is already assigned to your profile!{RESET + Colors.RESET}".encode("utf8"))
                    return
                
                new_user_badges = user_badges + badge_to_add
                
                cmd_db.execute("UPDATE users SET badges = ? WHERE username = ?", (new_user_badges, username))
                cmd_db.commit()
               
                socket.send(f"{GREEN + Colors.BOLD}Added badge '{badge_to_add}' to your user profile{RESET + Colors.RESET}".encode("utf8"))
            
            elif len(args) == 3:
                try:
                    uname = args[1]
                    badge_to_add = args[2]
                    
                    
                except:
                    socket.send(f"{RED + Colors.BOLD}Please pass a valid argument!{RESET + Colors.RESET}".encode("utf8"))
                    return
                    
                if not doesUserExist(uname):
                    socket.send(f"{RED + Colors.BOLD}Sorry, this user does not exist!{RESET + Colors.RESET}".encode("utf8"))
                    return
                
                else: 
                    cmd_db.execute("SELECT badges FROM users WHERE username = ?", (uname,))
                
                    user_badges = cmd_db.fetchone()[0]
                    
                    # Does the user already have this badge?
                    if badge_to_add in user_badges:
                        socket.send(f"{RED + Colors.BOLD}This badge is already assigned to {uname}'s profile!{RESET + Colors.RESET}".encode("utf8"))
                        return
                    
                    new_user_badges = user_badges + badge_to_add
                    
                    cmd_db.execute("UPDATE users SET badges = ? WHERE username = ?", (new_user_badges, uname))
                    cmd_db.commit()
                    
                    socket.send(f"{GREEN + Colors.BOLD}Added badge '{badge_to_add}' to {uname}'s profile{RESET + Colors.RESET}".encode("utf8"))
                    
            else:
                socket.send(f"{RED + Colors.BOLD}Invalid command usage.{RESET + Colors.RESET}".encode("utf8"))
                return
        else:
            socket.send(f"{RED}Sorry, you do not have permissons for that.{RESET}".encode("utf8"))
            return