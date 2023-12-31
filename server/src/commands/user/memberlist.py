from .. import register_command

import socket
import requests

from src.colors import *
from src.db import Database

from init import User, ClientSender, server_dir, users, config, online_mode, global_ip, max_users
from src.vars import api
from src.functions import memberListNickname, memberListBadge, isOnline, check_user_status

import yaml
from yaml import SafeLoader


@register_command("memberlist")
@register_command("userlist")
def memberlist_command(socket: socket.socket, user: User, args: list, sender: ClientSender):
    badge = {}
    
    cmd_db = Database(server_dir + "/users.db", check_same_thread=False)
                
    cmd_db.execute("SELECT username FROM users")
    raw_members = cmd_db.fetchall()
    membersLen  = len([raw_members for raw_members in sorted(raw_members)])
    
    cmd_db.execute("SELECT username, badge FROM users WHERE role = 'admin'")
    raw_admins  = cmd_db.fetchall()
    admins_len  = len([raw_admins for raw_admins in sorted(raw_admins)])
    admins      = "\n           ".join([f"{check_user_status(type='name', user=result[0])}{LIGHTRED_EX} {memberListNickname(result[0])} {memberListBadge(result[0])}" for result in raw_admins])
    
    cmd_db.execute("SELECT username, badge FROM users WHERE role = 'bot'")
    raw_bots    = cmd_db.fetchall()
    bots_len    = len([raw_bots for raw_bots in sorted(raw_bots)])
    bots        = "\n           ".join([f"{check_user_status(type='name', user=result[0])}{LIGHTMAGENTA_EX} {memberListNickname(result[0])} {memberListBadge(result[0])}" for result in raw_bots])
    
    
    cmd_db.execute("SELECT username, badge FROM users WHERE role = 'member'")
    raw_members = cmd_db.fetchall()
    members_len = len([raw_members for raw_members in sorted(raw_members)])
    members     = "\n           ".join([f"{check_user_status(type='name', user=result[0])}{LIGHTYELLOW_EX} {memberListNickname(result[0])} {memberListBadge(result[0])}" for result in raw_members])
    
    try:
        if online_mode == True:
            verified = requests.get(api + "server/verified?addr=" + global_ip)
        
            if verified.text == "True":
                verified_txt = f"{GREEN}[VERIFIED]{CYAN} "
            else:
                verified_txt = ""
            
        else:
            verified_txt = ""
        
    except Exception as e: 
        print(e)
    
    onlineUsersLen2 = len([user for user in sorted(users.values())])
    
    _online_users = f"{onlineUsersLen2}/{max_users}"
    if max_users == -1: _online_users = f"{onlineUsersLen2}"
                
    sender.send(f"""{CYAN +  Colors.UNDERLINE + Colors.BOLD}{verified_txt}{config['server']['name'].upper()} ({membersLen} Members, {_online_users} Online){RESET + Colors.RESET}
        {Colors.BOLD}->{Colors.RESET} {RED}Administrators ({admins_len}){RESET}
           {LIGHTRED_EX}{admins}{RESET}
        
        {Colors.BOLD}->{Colors.RESET} {MAGENTA}Bots ({bots_len}){RESET}
           {LIGHTMAGENTA_EX}{bots}{RESET}
    
        {Colors.BOLD}->{Colors.RESET} {YELLOW}Members ({members_len}){RESET}
           {LIGHTYELLOW_EX}{members}{RESET}
    """
    
    )