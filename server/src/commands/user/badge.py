from .. import register_command, PermissionLevel

import socket

from src.colors import *
from src.db import Database
from src.vars import role_colors, badge_list
from src.functions import doesUserExist

from init import stbexceptions, User, ClientSender, server_dir, log, debug_logger


@register_command("badge", arg_count=1)
def badge_command(socket: socket.socket, user: User, args: list, sender: ClientSender):
    cmd_db = Database(server_dir + "/users.db", check_same_thread=False)

    cmd = args[0]

    try: 
        cmd_db.execute('SELECT role FROM users WHERE username = ?', (user.username,))
        
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
                    sender.send(f"{RED + Colors.BOLD}Please pass a valid argument!{RESET + Colors.RESET}")
                    return

                cmd_db.execute("SELECT badges FROM users WHERE username = ?", (uname,))
                
                user_badges = cmd_db.fetchone()[0]            
                
                if not badge_to_set in user_badges:
                    sender.send(f"{RED + Colors.BOLD}This user does not own this badge!{RESET + Colors.RESET}")
                    return
                
                cmd_db.execute("UPDATE users SET badge = ? WHERE username = ?", (badge_to_set, uname))
                cmd_db.commit()
                
                sender.send(f"{GREEN + Colors.BOLD}The main badge of {uname} has been updated to '{badge_to_set}'{RESET + Colors.RESET}")
            
            else:
                sender.send(f"{RED}Sorry, you do not have permissons for that.{RESET}")
                return
        
        elif len(args) == 2:
            try:
                badge_to_set = args[1]
                
            except:
                sender.send(f"{RED + Colors.BOLD}Please pass a valid argument!{RESET + Colors.RESET}")
                return

            cmd_db.execute("SELECT badges FROM users WHERE username = ?", (user.username,))
            
            user_badges = cmd_db.fetchone()[0]            
            
            if not badge_to_set in user_badges:
                sender.send(f"{RED + Colors.BOLD}You do not own this badge!{RESET + Colors.RESET}")
                return
            
            cmd_db.execute("UPDATE users SET badge = ? WHERE username = ?", (badge_to_set, user.username))
            cmd_db.commit()
            
            sender.send(f"{GREEN + Colors.BOLD}Your main badge has been updated to '{badge_to_set}'{RESET + Colors.RESET}")            
            
        else: 
            sender.send(f"{RED + Colors.BOLD}Please pass a valid argument!{RESET + Colors.RESET}")
    
    
    elif cmd == "add":
        if user_role[0] == "admin":
            if len(args) == 2:
                try:
                    badge_to_add = args[1]
                    
                except:
                    sender.send(f"{RED + Colors.BOLD}Please pass a valid argument!{RESET + Colors.RESET}")
                    return
                
                if badge_to_add not in badge_list:
                    sender.send(f"{RED + Colors.BOLD}Invalid badge!{RESET + Colors.RESET}")
                    return
                    
                cmd_db.execute("SELECT badges FROM users WHERE username = ?", (user.username,))
                
                user_badges = cmd_db.fetchone()[0]
                
                # Does the user already have this badge?
                if badge_to_add in user_badges:
                    sender.send(f"{RED + Colors.BOLD}This badge is already assigned to your profile!{RESET + Colors.RESET}")
                    return
                
                new_user_badges = user_badges + badge_to_add
                
                cmd_db.execute("UPDATE users SET badges = ? WHERE username = ?", (new_user_badges, user.username))
                cmd_db.commit()
               
                sender.send(f"{GREEN + Colors.BOLD}Added badge '{badge_to_add}' to your user profile{RESET + Colors.RESET}")
            
            elif len(args) == 3:
                try:
                    uname = args[1]
                    badge_to_add = args[2]
                    
                except:
                    sender.send(f"{RED + Colors.BOLD}Please pass a valid argument!{RESET + Colors.RESET}")
                    return
                
                if badge_to_add not in badge_list:
                    sender.send(f"{RED + Colors.BOLD}Invalid badge!{RESET + Colors.RESET}")
                    return
                    
                if not doesUserExist(uname):
                    sender.send(f"{RED + Colors.BOLD}Sorry, this user does not exist!{RESET + Colors.RESET}")
                    return
                
                else: 
                    cmd_db.execute("SELECT badges FROM users WHERE username = ?", (uname,))
                
                    user_badges = cmd_db.fetchone()[0]
                    
                    # Does the user already have this badge?
                    if badge_to_add in user_badges:
                        sender.send(f"{RED + Colors.BOLD}This badge is already assigned to {uname}'s profile!{RESET + Colors.RESET}")
                        return
                    
                    new_user_badges = user_badges + badge_to_add
                    
                    cmd_db.execute("UPDATE users SET badges = ? WHERE username = ?", (new_user_badges, uname))
                    cmd_db.commit()
                    
                    sender.send(f"{GREEN + Colors.BOLD}Added badge '{badge_to_add}' to {uname}'s profile{RESET + Colors.RESET}")
                    
            else:
                sender.send(f"{RED + Colors.BOLD}Invalid command usage.{RESET + Colors.RESET}")
                return
        else:
            sender.send(f"{RED}Sorry, you do not have permissons for that.{RESET}")
            return