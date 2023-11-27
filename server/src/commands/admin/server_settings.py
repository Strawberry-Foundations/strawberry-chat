from .. import register_command, PermissionLevel

import socket

from src.colors import *
from src.db import Database
from src.vars import server_settings_help
from src.functions import hash_password, verify_password, escape_ansi

from init import server_dir, ipaddr, port, \
                 enable_messages, enable_queue, \
                 max_message_length, max_users, \
                 debug_mode, online_mode, update_channel, \
                 afks, queue, users, addresses, user_logged_in, blacklist


@register_command("serversettings", arg_count=1, required_permissions=PermissionLevel.ADMIN)
def user_settings_command(socket: socket.socket, username: str, args: list, send):
    cmd_db = Database(server_dir + "/users.db", check_same_thread=False)
    try:
        match args[0]:
            case "help":
                send(f"{server_settings_help}{RESET}")
            
            case "show":
                message = f"""{GREEN +  Colors.UNDERLINE + Colors.BOLD}Your Server Settings{RESET + Colors.RESET}
        {YELLOW}WARNING:{RESET} This could contain sensible information!
        
        {CYAN}IP-Address:{RESET} {ipaddr}
        {CYAN}Port:{RESET} {port}
        {CYAN}Enable Logging Messages:{RESET}{ enable_messages}
        {CYAN}Enable Queue:{RESET} {enable_queue}
        {CYAN}Max Message Length:{RESET} {max_message_length}
        {CYAN}Max Users:{RESET} {max_users}
        {CYAN}Debug Mode:{RESET} {debug_mode}
        {CYAN}Online Mode:{RESET} {online_mode}
        {CYAN}Update Channel:{RESET} {update_channel}
        """
                send(message)
                try:
                    if args[1] == "debug":
                        message = f"""{GREEN +  Colors.UNDERLINE + Colors.BOLD}Your Server Settings (Debug){RESET + Colors.RESET}
            {YELLOW}WARNING:{RESET} This could contain sensible information!
            
            {CYAN}IP-Address:{RESET} {ipaddr}
            {CYAN}Port:{RESET} {port}
            {CYAN}Enable Logging Messages:{RESET} {enable_messages}
            {CYAN}Enable Queue:{RESET} {enable_queue}
            {CYAN}Max Message Length:{RESET} {max_message_length}
            {CYAN}Max Users:{RESET} {max_users}
            {CYAN}Debug Mode:{RESET} {debug_mode}
            {CYAN}Online Mode:{RESET} {online_mode}
            {CYAN}Update Channel:{RESET} {update_channel}
            
            {YELLOW}Afks:{RESET} {afks}
            {YELLOW}Queue:{RESET} {queue.queue}
            {YELLOW}Users:{RESET} {users}
            {YELLOW}Addresses:{RESET} {addresses}
            {YELLOW}Logged in:{RESET} {user_logged_in}
            """
            
                        send(message)
                        
                except: pass
            
            case _:
                send(f"{Colors.RESET + RED}Invalid subcommand!{RESET + Colors.RESET}")
                    
    except Exception as e: 
        send(f"{RED}Not enough arguments!{RESET}")
        print(e)