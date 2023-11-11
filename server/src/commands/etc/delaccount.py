from .. import register_command

import socket

from src.colors import *
from src.db import Database

from init import server_dir

@register_command("deleteaccount")
def delete_account_command(socket: socket.socket, username: str, args: list, send):
    cmd_db = Database(server_dir + "/users.db", check_same_thread=False)
    
    socket.send(f"{YELLOW + Colors.BOLD}Are you sure you want to delete your user account? This action is irreversible!!{RESET + Colors.RESET}".encode("utf8"))
    confirm_delete_1 = socket.recv(2048).decode("utf8")
    
    if confirm_delete_1.lower() == "yes":
        socket.send(f"{RED + Colors.BOLD}THIS IS YOUR VERY LAST WARNING! This action is irreversible!! ARE YOU SURE?{RESET + Colors.RESET}".encode("utf8"))
        confirm_delete_2 = socket.recv(2048).decode("utf8")
        
        if confirm_delete_2.lower() == "yes":
            socket.send(f"{YELLOW + Colors.BOLD}Enter your username to confirm the deletion of your account:{RESET + Colors.RESET}".encode("utf8"))
            confirm_username_delete = socket.recv(2048).decode("utf8")
            
            if confirm_username_delete == username:
                socket.send(f"{YELLOW + Colors.BOLD}Deleting your user account...{RESET + Colors.RESET}".encode("utf8"))
                
                try:
                    cmd_db.execute("DELETE FROM users WHERE username = ?", (username,))
                    cmd_db.commit()
                    socket.send(f"{GREEN + Colors.BOLD}Deleted{RESET + Colors.RESET}".encode("utf8"))
                    socket.close()
                    
                except Exception as e:
                    print(e)
                    
            else: 
                socket.send(f"{YELLOW + Colors.BOLD}Deletion of your account has been canceled...{RESET + Colors.RESET}".encode("utf8"))
        else:
            socket.send(f"{YELLOW + Colors.BOLD}Deletion of your account has been canceled...{RESET + Colors.RESET}".encode("utf8"))
    else:
        socket.send(f"{YELLOW + Colors.BOLD}Deletion of your account has been canceled...{RESET + Colors.RESET}".encode("utf8"))