from .. import register_command, PermissionLevel

import socket

from src.colors import *
from src.db import Database
from src.vars import role_colors
from src.functions import doesUserExist

from init import server_dir, blacklist


@register_command("bwords", arg_count=1, required_permissions=PermissionLevel.ADMIN)
def bwords_command(socket: socket.socket, username: str, args: list, send):
    cmd_db = Database(server_dir + "/users.db", check_same_thread=False)

    cmd = args[0]
    
    # /role set Command
    if cmd == "set":
        try:
            uname = args[1]
            value = args[2]
            
            if not doesUserExist(uname):
                socket.send(f"{RED + Colors.BOLD}Sorry, this user does not exist!{RESET + Colors.RESET}".encode("utf8"))
                return
        
            cmd_db.execute("UPDATE users SET enable_blacklisted_words = ? WHERE username = ?", (value, uname))
            cmd_db.commit()
        
            if value == "true":
                socket.send(f"{LIGHTGREEN_EX + Colors.BOLD}Enabled Blacklisted Words for {uname}{RESET + Colors.RESET}".encode("utf8"))
                return
            
            elif value == "false":
                socket.send(f"{LIGHTGREEN_EX + Colors.BOLD}Disabled Blacklisted Words for {uname}{RESET + Colors.RESET}".encode("utf8"))
                return
            
            else:
                socket.send(f"{RED + Colors.BOLD}Invalid value!{RESET + Colors.RESET}".encode("utf8"))
                return

        except:
            socket.send(f"{RED + Colors.BOLD}Invalid username and/or value!{RESET + Colors.RESET}".encode("utf8"))
            return

    elif cmd == "get":
        try:
            uname = args[1]
                
            cmd_db.execute("SELECT enable_blacklisted_words FROM users WHERE username = ?", (uname,))
            value = cmd_db.fetchone()[0]
            
            if value == "true":
                socket.send(f"{LIGHTGREEN_EX + Colors.BOLD}Blacklisted Words for {uname} are enabled{RESET + Colors.RESET}".encode("utf8"))
                return
            
            elif value == "false":
                socket.send(f"{LIGHTGREEN_EX + Colors.BOLD}Blacklisted Words for {uname} are disabled{RESET + Colors.RESET}".encode("utf8"))
                return
            
            else:
                socket.send(f"{RED + Colors.BOLD}Whoa! This should not happen...{RESET + Colors.RESET}".encode("utf8"))
                return
        except:
            socket.send(f"{RED + Colors.BOLD}Invalid username{RESET + Colors.RESET}".encode("utf8"))
            return

    elif cmd == "add":
        try:
            word = args[1]
        except:
            socket.send(f"{RED + Colors.BOLD}Cant add an empty word!{RESET + Colors.RESET}".encode("utf8"))
            return
        
        if word == "":
            socket.send(f"{RED + Colors.BOLD}Cant add an empty word!{RESET + Colors.RESET}".encode("utf8"))
            return
        
        with open("blacklist.txt", "a") as f:
            f.write("\n" + word)
            f.close()
        
        socket.send(f"{LIGHTGREEN_EX + Colors.BOLD}Added '{word}' to the blacklist{RESET + Colors.RESET}".encode("utf8"))
        return

    elif cmd == "reload":
        with open("blacklist.txt", "r") as f:
            for word in f:
                word = word.strip().lower()
                blacklist.add(word)
                
        socket.send(f"{GREEN + Colors.BOLD}Reloaded blacklisted words.{RESET + Colors.RESET}".encode("utf8"))
        return
            
    else:
        socket.send(f"{RED + Colors.BOLD}Invalid command usage.{RESET + Colors.RESET}".encode("utf8"))
        return