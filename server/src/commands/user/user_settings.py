from .. import register_command

import socket

from src.colors import *
from src.db import Database
from src.vars import user_settings_help, admin_settings_help
from src.functions import hash_password, verify_password, escape_ansi

from init import User, ClientSender, server_dir, users, addresses


@register_command("settings", arg_count=1)
def user_settings_command(socket: socket.socket, user: User, args: list, sender: ClientSender):
    cmd_db = Database(server_dir + "/users.db", check_same_thread=False)
    try:
        match args[0]:
            case "help":
                sender.send(f"{user_settings_help}{RESET}")
            
            case "enable_dms":
                if args[1] in ["true", "false"]:
                    cmd_db.execute("UPDATE users SET enable_dms = ? WHERE username = ?", (args[1], user.username))
                    cmd_db.commit()
                    sender.send(f"{LIGHTGREEN_EX + Colors.BOLD}Updated enable_dms to {args[1]}{RESET + Colors.RESET}")
                    
                else:
                    sender.send(f"{Colors.RESET + RED}Please pass a valid argument!{RESET + Colors.RESET}")
                    
            case "discord_name":
                cmd_db.execute("UPDATE users SET discord_name = ? WHERE username = ?", (args[1], user.username))
                cmd_db.commit()
                sender.send(f"{LIGHTGREEN_EX + Colors.BOLD}Updated discord name to {args[1]}{RESET + Colors.RESET}")
            
            case "role_color":
                color = args[1]
                colors = ["red", "green", "cyan", "blue", "yellow", "magenta",
                          "lightred", "lightgreen", "lightcyan", "lightblue", "lightyellow", "lightmagenta"
                          "boldred", "boldgreen", "boldcyan", "boldblue", "boldyellow", "boldmagenta"]
                
                if color in colors:
                    cmd_db.execute("UPDATE users SET role_color = ? WHERE username = ?", (color, user.username))
                    cmd_db.commit()
                    sender.send(f"{LIGHTGREEN_EX + Colors.BOLD}Your role color has been updated to {color}{RESET + Colors.RESET}")
                
                else:
                    sender.send(f"{Colors.RESET + RED}Invalid role color!{RESET + Colors.RESET}")                
            
            case "badge":
                cmd_db.execute("SELECT badges FROM users WHERE username = ?", (user.username,))
                badge_to_set = args[1]
                user_badges = cmd_db.fetchone()[0]
                
                if badge_to_set in user_badges:
                    cmd_db.execute("UPDATE users SET badge = ? WHERE username = ?", (badge_to_set, user.username))
                    cmd_db.commit()
                    
                    sender.send(f"{GREEN + Colors.BOLD}The main badge of you has been updated to '{badge_to_set}'{RESET + Colors.RESET}")
                
                else:
                    sender.send(f"{RED + Colors.BOLD}You do not own this badge!{RESET + Colors.RESET}")
                    
            case "description":
                cmd_db.execute("UPDATE users SET description = ? WHERE username = ?", (args[1], user.username))
                cmd_db.commit()
                sender.send(f"{LIGHTGREEN_EX + Colors.BOLD}Updated description to {args[1]}{RESET + Colors.RESET}")
                
            case "account":
                if args[1] == "username":
                    new_username = args[2]
                    
                    if new_username == user.username:
                        sender.send(f"{Colors.RESET + YELLOW}You shouldn't update your username to your current. Nothing changed.{RESET + Colors.RESET}")
                        return
                        
                    else:                        
                        sender.send(f"{YELLOW + Colors.BOLD}Are you sure to change your username to {new_username}?{RESET + Colors.RESET}")
                        confirmUsername = socket.recv(2048).decode("utf8")
                    
                    if confirmUsername == "yes":
                        sender.send(f"{YELLOW + Colors.BOLD}Processing... {RESET + Colors.RESET}")
                        
                        cmd_db.execute("UPDATE users SET username = ? WHERE username = ?", (new_username, user.username))
                        cmd_db.commit()
                        sender.send(f"{LIGHTGREEN_EX + Colors.BOLD}Your username has been updated to {new_username}. You may need to relogin in strawberry chat.{RESET + Colors.RESET}")
                        
                        del addresses[socket]
                        del users[socket]
                        socket.close()
                        return
                        
                    else:
                        sender.send(f"{Colors.RESET + RED}Cancelled!{RESET + Colors.RESET}")
                
                elif args[1] == "password":
                    sender.send(f"{GREEN + Colors.BOLD}New Password: {RESET + Colors.RESET}")
                    new_password = escape_ansi(socket.recv(2048).decode("utf8"))
                    new_password = new_password.strip("\n")
                    
                    cmd_db.execute("SELECT password FROM users WHERE username = ?", (user.username,))
                    result = cmd_db.fetchone()
                    stored_password = result[0]
                    
                    if verify_password(stored_password, new_password):
                        sender.send(f"{Colors.RESET + YELLOW}You shouldn't update your password to your current. Nothing changed.{RESET + Colors.RESET}")
                        return
                        
                    else:                   
                        sender.send(f"{GREEN + Colors.BOLD}Confirm Password: {RESET + Colors.RESET}")
                        confirm_password = socket.recv(2048).decode("utf8")
                    
                    if new_password != confirm_password:
                        sender.send(f"{RED + Colors.BOLD}Passwords do not match{RESET + Colors.RESET}")
                        return
                    
                    else:
                        new_password = hash_password(new_password)
                        sender.send(f"{YELLOW + Colors.BOLD}Processing... {RESET + Colors.RESET}")
                                                
                        cmd_db.execute("UPDATE users SET password = ? WHERE username = ?", (new_password, user.username))
                        cmd_db.commit()
                        sender.send(f"{LIGHTGREEN_EX + Colors.BOLD}Your password has been updated.{RESET + Colors.RESET}")
                                        
                else:
                    sender.send(f"{Colors.RESET + RED}Please pass a valid argument!{RESET + Colors.RESET}")
            
            case _:
                sender.send(f"{Colors.RESET + RED}Invalid subcommand!{RESET + Colors.RESET}")
                    
    except Exception as e: 
        sender.send(f"{RED}Not enough arguments!{RESET}")
        print(e)
        
            
@register_command("admin", arg_count=1)
def admin_settings_command(socket: socket.socket, user: User, args: list, sender: ClientSender):
    cmd_db = Database(server_dir + "/users.db", check_same_thread=False)
    match args[0]:
        case "help":
            sender.send(f"{admin_settings_help}{RESET}")
        
        case _:
                sender.send(f"{Colors.RESET + RED}Invalid subcommand!{RESET + Colors.RESET}")