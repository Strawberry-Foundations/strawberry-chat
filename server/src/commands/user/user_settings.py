from .. import register_command

import socket

from src.colors import *
from src.db import Database
from src.vars import user_settings_help, admin_settings_help

from init import server_dir

@register_command("settings", arg_count=1)
def user_settings_command(socket: socket.socket, username: str, args: list):
    cmd_db = Database(server_dir + "/users.db", check_same_thread=False)
    
    match args[0]:
        case "help":
            socket.send(f"{user_settings_help}{RESET}".encode("utf8"))
            
@register_command("admin", arg_count=1)
def user_settings_command(socket: socket.socket, username: str, args: list):
    cmd_db = Database(server_dir + "/users.db", check_same_thread=False)
    
    match args[0]:
        case "help":
            socket.send(f"{admin_settings_help}{RESET}".encode("utf8"))