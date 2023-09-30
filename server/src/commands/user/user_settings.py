from .. import register_command

import socket

from src.colors import *
from src.db import Database
from src.vars import user_settings_help, admin_settings_help

from init import server_dir


@register_command("settings", arg_count=1)
def user_settings_command(socket: socket.socket, username: str, args: list):
    cmd_db = Database(server_dir + "/users.db", check_same_thread=False)
    try:
        match args[0]:
            case "help":
                socket.send(f"{user_settings_help}{RESET}".encode("utf8"))
            
            case "enable_dms":
                if args[1] in ["true", "false"]:
                    cmd_db.execute("UPDATE users SET enable_dms = ? WHERE username = ?", (args[1], username))
                    cmd_db.commit()
                    socket.send(f"{LIGHTGREEN_EX + Colors.BOLD}Updated enable_dms to {args[1]}{RESET + Colors.RESET}".encode("utf8"))
                    
                else:
                    socket.send(f"{Colors.RESET + RED}Please pass a valid argument!{RESET + Colors.RESET}".encode("utf8"))
                    
            case "discord_name":
                cmd_db.execute("UPDATE users SET discord_name = ? WHERE username = ?", (args[1], username))
                cmd_db.commit()
                socket.send(f"{LIGHTGREEN_EX + Colors.BOLD}Updated discord name to {args[1]}{RESET + Colors.RESET}".encode("utf8"))
                
            case "description":
                cmd_db.execute("UPDATE users SET description = ? WHERE username = ?", (args[1], username))
                cmd_db.commit()
                socket.send(f"{LIGHTGREEN_EX + Colors.BOLD}Updated description to {args[1]}{RESET + Colors.RESET}".encode("utf8"))
            
            case "badge":
                cmd_db.execute("SELECT badges FROM users WHERE username = ?", (username,))
                badge_to_set = args[1]
                user_badges = cmd_db.fetchone()[0]
                
                if badge_to_set in user_badges:
                    cmd_db.execute("UPDATE users SET badge = ? WHERE username = ?", (badge_to_set, username))
                    cmd_db.commit()
                    
                    socket.send(f"{GREEN + Colors.BOLD}The main badge of you has been updated to '{badge_to_set}'{RESET + Colors.RESET}".encode("utf8"))
                
                else:
                    socket.send(f"{RED + Colors.BOLD}You do not own this badge!{RESET + Colors.RESET}".encode("utf8"))
            
            case "role_color":
                color = args[1]
                colors = ["red", "green", "cyan", "blue", "yellow", "magenta",
                          "lightred", "lightgreen", "lightcyan", "lightblue", "lightyellow", "lightmagenta"
                          "boldred", "boldgreen", "boldcyan", "boldblue", "boldyellow", "boldmagenta"]
                
                if color in colors:
                    cmd_db.execute("UPDATE users SET role_color = ? WHERE username = ?", (color, username))
                    cmd_db.commit()
                    socket.send(f"{LIGHTGREEN_EX + Colors.BOLD}Your role color has been updated to {color}{RESET + Colors.RESET}".encode("utf8"))
                
                else:
                    socket.send(f"{Colors.RESET + RED}Invalid role color!{RESET + Colors.RESET}".encode("utf8"))
            
            case _:
                socket.send(f"{Colors.RESET + RED}Invalid subcommand!{RESET + Colors.RESET}".encode("utf8"))
                    
    except Exception as e: 
        socket.send(f"{RED}Not enough arguments!{RESET}".encode("utf8"))
        print(e)
            
            
@register_command("admin", arg_count=1)
def admin_settings_command(socket: socket.socket, username: str, args: list):
    cmd_db = Database(server_dir + "/users.db", check_same_thread=False)
    match args[0]:
        case "help":
            socket.send(f"{admin_settings_help}{RESET}".encode("utf8"))
        
        case _:
                socket.send(f"{Colors.RESET + RED}Invalid subcommand!{RESET + Colors.RESET}".encode("utf8"))