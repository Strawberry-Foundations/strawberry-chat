#!/usr/bin/env python3

import socket
import threading

import os
import sys

import traceback
import errno

import sqlite3 as sql
import yaml
from yaml import SafeLoader

import atexit
import datetime
import time
import random
import requests
from colorama import Style

from init import *
from src.colors import *
from src.functions import *
from src.vars import *
from src.online import *
from src.commands import PermissionLevel, execute_command, list_commands

from src.commands.default import help, server_info, changelog, about, dm, exit_cmd
from src.commands.etc import test_command, news, delaccount
from src.commands.admin import broadcast_cmd, mute, ban, kick, debug, role, bwords
from src.commands.user import online, afklist, afk, unafk, msgcount, members, description, memberlist, discord, user_settings, user, nickname, badge


if "--enable-messages" in sys.argv: enable_messages = True
if "--debug-mode" in sys.argv: debug_mode = True
if "--test-mode" in sys.argv: test_mode = True
if "--regen-database" in sys.argv: input_regen_database()


# Check if database file exists
if os.path.exists(server_dir + "/users.db"):
    # Connect to database
    db = sql.connect(server_dir + "/users.db", check_same_thread=False)
    print(f"{GREEN + Colors.BOLD}>>> {RESET}Connected to database")
    
else:
    # Connect/Create database
    query_db = sql.connect(server_dir + "/users.db", check_same_thread=False)
    query_c = query_db.cursor()
    print(f"{GREEN + Colors.BOLD}>>> {RESET}Created database")
    
    query_c.execute(table_query)
    query_db.commit()
    
    query_c.close()
    query_db.close()
    
    print(f"{GREEN + Colors.BOLD}>>> {RESET}Created table")
    print(f"{YELLOW + Colors.BOLD}>>> {RESET}Restart your server to connect to your new database.")
    exit()

# Blacklisted word functions
def open_blacklist():
    with open(server_dir + "/blacklist.txt", "r") as f:
        for word in f:
            word = word.strip().lower()
            blacklist.add(word)

# Check if blacklist exists
if os.path.exists(server_dir + "/blacklist.txt"):
    open_blacklist()
    
else:
    create_empty_file("blacklist.txt")
    open_blacklist()

# Open news file
with open(server_dir + "/news.yml") as news_file:
    news_data = yaml.load(news_file, Loader=SafeLoader)
    
# News
news_text = f"""{GREEN +  Colors.UNDERLINE + Colors.BOLD}{chat_name} News - {short_ver}{RESET + Colors.RESET}{CYAN + Colors.BOLD}
{news_data['news'][base_ver]['text']}{RESET + Colors.RESET}"""


def connectionThread(sock):
    while True:
        try:
            client, address = sock.accept()

        except Exception as e:
            log.error("A connection error occured!")
            debug_logger(e, stbexceptions.connection_error)  
            
            break
        
        log.info(f"{address[0]} has connected")
        
        addresses[client] = address
        threading.Thread(target=clientThread, args=(client,)).start()


def clientThread(client):
    def send(message):
        json_builder = {
            "message_type": StbCom.SYS_MSG,
            "message": {
                "content": message
            }
        }
        
        client.send(send_json(json_builder).encode('utf8'))
        
    # Define db variable global
    global db
    
    address = addresses[client][0]
    
    try:
        user = clientLogin(client)
        
        user_logged_in[user] = True
        
        if user == "CltExit":
            del addresses[client]
            return
            
    except Exception as e:
        log.error(f"A login error with {address} occured!")
        debug_logger(e, stbexceptions.login_error)
        
        del addresses[client]
        return
    
    
    log.info(f"{user} ({address}) logged in")
    users[client] = user

    try:
        send(f"{CYAN + Colors.BOLD}Welcome back {user}! Nice to see you!{RESET + Colors.RESET}")
        onlineUsersLen = len([user for user in sorted(users.values())])
        
        if onlineUsersLen == 1:
            onlineUsersStr = f"is {onlineUsersLen} user"
        else:
            onlineUsersStr = f"are {onlineUsersLen} users"
            
        time.sleep(0.05)
        send(f"""{CYAN + Colors.BOLD}Currently there {onlineUsersStr} online. For help use /help{RESET + Colors.RESET}\n{news_text}""")
        

    except Exception as e:
        log.error(f"A Communication error with {address} ({user}) occurred.")
        debug_logger(e, stbexceptions.communication_error)
        
        del addresses[client]
        del users[client]
        client.close()
        return
    
    time.sleep(0.1)
    broadcast(f"{Colors.GRAY + Colors.BOLD}-->{Colors.RESET} {userRoleColor(user)}{user}{GREEN + Colors.BOLD} has joined the chat room!{RESET + Colors.RESET}")

    while True:
        try:
            try:
                if user_logged_in[user]:
                    message = client.recv(2048).decode("utf8")                    
                    
                    if len(message) == 0:
                        return
                else:
                    return

            except OSError: 
                return
            
            except Exception as e:
                log.warning(f"A message transmission error occurred.")
                debug_logger(e, stbexceptions.transmition_error, type=StbTypes.WARNING)
                return
            
            message_length = len(message)
            
            clcur = db.cursor()

            clcur.execute('SELECT role FROM users WHERE username = ?', (user,))    
            res = clcur.fetchone()
                    
            # Message length control system
            rnd = random.randint(0, 2)
            
            c = db.cursor()
            
            if res[0] == "bot":
                pass
            
            else:
                if message_length > max_message_length:
                    if rnd == 0:
                        send(f"{YELLOW + Colors.BOLD}Your message is too long.{RESET + Colors.RESET}")
                        
                    elif rnd == 1:
                        send(f"{YELLOW + Colors.BOLD}boah digga halbe bibel wer liest sich das durch{RESET + Colors.RESET}")
                        
                    elif rnd == 2:
                        send(f"{YELLOW + Colors.BOLD}junge niemand will sich hier die herr der ringe trilogie durchlesen{RESET + Colors.RESET}")

            # Blacklisted Word System
            clcur.execute('SELECT role, enable_blacklisted_words FROM users WHERE username = ?', (user,))    
            res = clcur.fetchone()
            
            if res[0] == "admin" or res[0] == "bot" or res[1] == "false":
                pass
            
            else:
                for word in message.split():
                    word = word.lower()
                    
                    if word in blacklist:
                        send(f"{YELLOW + Colors.BOLD}Please be friendlier in the chat. Rejoin when you feel ready!{RESET + Colors.RESET}")
                        client.close()
                        
                    else:
                        pass
        
            # Global Command Executor
            if message.startswith("/"):
                try:
                    message = message[1:]
                    args = message.split()
                    cmd = args[0]
                    args = args[1:]
                    
                except: 
                    send(f"{RED}Not enough arguments! Please pass an valid command!{RESET}")
                    continue
                
                try:
                    c.execute('SELECT role FROM users WHERE username = ?', (user,))

                except Exception as e:
                    log.error("An SQL error occured!")
                    debug_logger(e, stbexceptions.sql_error)
                    
                user_role = c.fetchone()[0]
                role = None
                
                match user_role:
                    case "member":
                        role = PermissionLevel.MEMBER
                    case "admin":
                        role = PermissionLevel.ADMIN
                    case "bot":
                        role = PermissionLevel.BOT
                    case _:
                        role = PermissionLevel.NONE
                        
                execute_command(cmd, client, user, role, args, send)
                continue
            

            # Message handling
            if isMuted(user):
                send(f"{RED + Colors.BOLD}Sorry, but you were muted by an administrator. Please contact him/her if you have done nothing wrong, or wait until you are unmuted.{RESET + Colors.RESET}")
            
            elif not isAccountEnabled(user):
                send(f"{RED + Colors.BOLD}Your account was disabled by an administrator.{RESET + Colors.RESET}")
                
            elif user in afks:
                send(f"{RED}Sorry, you are AFK.{RESET}")
                
            else:
                if not is_empty_or_whitespace(message):
                    if enable_messages:
                        log_msg = escape_ansi(message)
                                                        
                        log.info(f"{user} ({address}): {log_msg}")
                            
                    broadcast(message, user)
                    
                    try:
                        c.execute("SELECT msg_count FROM users WHERE username = ?", (user,))
                        msg_count = c.fetchone()
                        msg_count = msg_count[0] + 1
                        c.execute("UPDATE users SET msg_count = ? WHERE username = ?", (msg_count, user))
                        db.commit()
                        
                    except Exception as e:
                        log.error("An SQL error occured!")
                        debug_logger(e, stbexceptions.sql_error)
            c.close()            
                
        except Exception as e:
            log.error("A client-side error occurred.")
            
            debug_logger(e, stbexceptions.client_error)
            traceback.print_exc()
            log.info(f"{user} ({address}) has left")
            
            try:
                del addresses[client]
                del users[client]
                client.close()
                
            except Exception as e:
                log.warning("A socket-to-client exception occured")
                debug_logger(e, stbexceptions.stc_error, type=StbTypes.WARNING)
            
            broadcast(f"{Colors.GRAY + Colors.BOLD}<--{Colors.RESET} {userRoleColor(user)}{user}{YELLOW + Colors.BOLD} has left the chat room!{RESET + Colors.RESET}")
            break

def clientRegister(client, login_cur, sender):
    # Send a welcome message
    sender.send(f"{MAGENTA + Colors.BOLD + Colors.UNDERLINE}Welcome!{RESET + Colors.RESET}\n        {Colors.BOLD}Register, to chat with us!{Colors.RESET}")

    time.sleep(0.05)
    
    # Ask for a username that the user wants
    sender.send(f"{GREEN + Colors.BOLD}Username: {RESET + Colors.RESET}")
    
    # Receive username
    registered_username = client.recv(2048).decode("utf8")
    
    # If username is exit, exit the registration process 
    if registered_username.lower() == "exit":
        client.close()
        exit()
    
    # Check if the username is allowed
    for uname in registered_username.split():
        uname = uname.lower()
        
        # If username is in blacklisted words, return an error message and start from the beginning
        if uname in blacklist:
            sender.send(f"{YELLOW + Colors.BOLD}This username is not allowed{RESET + Colors.RESET}\n")    
            clientRegister(client, login_cur, sender)
            
        # If username is in this set of blacklisted words, return an error message and start from the beginning
        elif uname in ["exit", "register", "login"]:
            sender.send(f"{YELLOW + Colors.BOLD}This username is not allowed{RESET + Colors.RESET}\n")    
            clientRegister(client, login_cur, sender)
    
    # Check if the username is already in use
    try:
        login_cur.execute("SELECT username FROM users WHERE username = ? ", (registered_username,))
        
        usedUsernames = login_cur.fetchall()[0]
        usedUsernames = "".join(usedUsernames)
        
        if usedUsernames == usedUsernames:
            sender.send(f"{YELLOW + Colors.BOLD}This username is already in use!{RESET + Colors.RESET}\n")    
            clientRegister(client, login_cur, sender)
        
    except Exception as e:
        log.error("A registration exception occured")
        debug_logger(e, stbexceptions.reg_error)

    # Ask and receive password
    sender.send(f"{GREEN + Colors.BOLD}Password: {RESET + Colors.RESET}")
    registered_password = client.recv(2048).decode("utf8")
    
    # Confirm the new password
    sender.send(f"{GREEN + Colors.BOLD}Confirm Password: {RESET + Colors.RESET}")
    confirm_password = client.recv(2048).decode("utf8")
    
    # If passwords does not match, return an error message
    if registered_password != confirm_password:
        sender.send(f"{RED + Colors.BOLD}Passwords do not match{RESET + Colors.RESET}")
        clientRegister(client, login_cur, sender)
    
    # Ask and receive role color
    sender.send(f"{GREEN + Colors.BOLD}Role Color (Red, Green, Cyan, Blue, Yellow, Magenta): {RESET + Colors.RESET}")
    registered_role_color = client.recv(2048).decode("utf8")

    # Ask if everything is correct
    sender.send(f"{YELLOW + Colors.BOLD}Is everything correct? (You can change your username, role color and password at any time){RESET + Colors.RESET}")
    confirm_account_creation = client.recv(2048).decode("utf8")
    
    # If confirm_account_creation is yes, create the new account
    if confirm_account_creation.lower() == "yes":
        sender.send(f"{YELLOW + Colors.BOLD}Processing... {RESET + Colors.RESET}")
        
        try:
            sender.send(f"{GREEN + Colors.BOLD}Creating your User account... {RESET + Colors.RESET}")
        
            login_cur.execute("SELECT user_id FROM users")
        
            user_ids = login_cur.fetchall()
            user_ids = str(user_ids[-1])
            user_ids = user_ids[1:-2].replace(",", "")
            user_id = int(user_ids) + 1
            
            creation_date = time.time()
            
            registered_password = hash_password(registered_password)

            # logcur.execute('INSERT INTO users (username, password, role, role_color, enable_blacklisted_words, account_enabled, muted, user_id, msg_count, enable_dms, creation_date) VALUES (?, ?, "member", ?, "true", "true", "false", ?, ?, "true", ?)', (registered_username, registered_password, registered_role_color.lower(), user_ids, 0, creation_date))
            login_cur.execute('''
                           INSERT INTO users (
                               username,
                               password,
                               role,
                               role_color,
                               enable_blacklisted_words,
                               account_enabled,
                               muted,
                               user_id,
                               msg_count,
                               enable_dms,
                               creation_date)
                               VALUES (?, ?, "member", ?, "true", "true", "false", ?, ?, "true", ?)''',
                            (registered_username, registered_password, registered_role_color.lower(), user_id, 0, creation_date))
            db.commit()
            
            sender.send(f"{GREEN + Colors.BOLD}Created!{RESET + Colors.RESET}")
            client.close()
            
        except Exception as e:
            log.error("An SQL error occured!")
            debug_logger(e, stbexceptions.sql_error)
        
    else:
        sender.send(f"{RED + Colors.BOLD}Registration has been canceled. Start from the beginning...{RESET + Colors.RESET}")
        time.sleep(0.5)
        clientRegister(client, login_cur, sender)


def strawberryIdLogin(client):
    client.send(f"{GREEN + Colors.BOLD}Visit https://id.strawberryfoundations.xyz/v1/de?redirect=https://api.strawberryfoundations.xyz/stbchat&hl=de to login!{RESET + Colors.RESET}")
    


"""
--- CLIENT LOGIN ---
The client login function for logging into the chat.
This piece of code is well commented so that you understand what almost every line does.
"""
def clientLogin(client):
    sender      = ClientSender(client)
    logged_in   = False
    login_cur   = db.cursor()
    
    welcome_message_base = f"{Colors.BOLD}Welcome to Strawberry Chat!"
    welcome_message_ext  = f"{Colors.BOLD}New here? Type '{MAGENTA}Register{RESET}' to register! You want to leave? Type '{MAGENTA}Exit{RESET}' {Colors.RESET}"
    
    sender.send(welcome_message_base.strip("\n").rstrip())
    time.sleep(0.08)
    sender.send(welcome_message_ext.strip("\n").rstrip())
    
    while not logged_in:
        # Ask for the username
        time.sleep(0.05)
        sender.send(f"{GREEN + Colors.BOLD}Username: {RESET + Colors.RESET}")
        
        # Receive the ansi-escaped username and strip all new lines in case
        username = escape_ansi(client.recv(2048).decode("utf8")).strip().rstrip()
        
        # Check if username is "register", "exit" or "sid" 
        if username.lower() == "register": clientRegister(client, login_cur, sender)
        elif username.lower() == "exit": sender.close(del_address=True)
        elif username.lower() == "sid": strawberryIdLogin(client)
            
        time.sleep(0.05)
        
        # Ask for the password
        sender.send(f"{GREEN + Colors.BOLD}Password: {RESET + Colors.RESET}")
        
        # Receive the ansi-escaped password and strip all new lines in case
        password = escape_ansi(client.recv(2048).decode("utf8")).strip("\n").rstrip()
        
        # Select the password from the database and fetch it 
        login_cur.execute("SELECT password, account_enabled FROM users WHERE username = ?", (username,))
        result = login_cur.fetchone()

        # If the result is not none, fetch some things from the database [...].
        if result is not None:
            stored_password = result[0]
            account_enabled = result[1]
            
            # If account is not enabled, return error message and close connection between server and client
            if account_enabled == "false":
                sender.send(f"{RED + Colors.BOLD}Your account was disabled by an administrator.{RESET + Colors.RESET}")
                sender.close(del_address=True, call_exit=False)
                return "CltExit"
            
            if not enable_queue:
                if len(users) >= max_users:
                    sender.send(f"{YELLOW + Colors.BOLD}Sorry, Server is full!{RESET + Colors.RESET}")
                    sender.close(del_address=True, call_exit=True)
                
            # If the stored password from the database matches with the entered password, fetch the username and login the user
            if verify_password(stored_password, password):
                login_cur.execute('SELECT username FROM users WHERE username = ?', (username,))
                result = login_cur.fetchone()
                
                _username = result[0]
                
                if enable_queue:
                    if len(users) >= max_users:
                        
                        queue.add(_username)
                        log.info(f"{_username} ({addresses[client][0]}) is now in the queue")
                        
                        stopwatch = Stopwatch()
                        stopwatch.start()
                        
                        while True:
                            sender.send(f"{YELLOW + Colors.BOLD}You're currently at position {queue.position_user(_username)} in the queue.. Time past: {stopwatch.elapsed_time()}s Please wait until one slot is free...{RESET + Colors.RESET}")
                            time.sleep(1)
                            
                            if not len(users) >= max_users:
                                if queue.position_user(_username) == 1:
                                    if result is not None:
                                        log.info(f"{_username} ({addresses[client][0]}) left the queue")
                                        
                                        queue.remove()
                                        stopwatch.stop()
                                        stopwatch.reset()
                                        
                                        username = _username
                                        logged_in = True
                                        
                                        sender.send(f"{CYAN + Colors.BOLD}You've left the queue and are now logged in. Have fun!{RESET + Colors.RESET}")
                                        return username
                                    
                                else: pass
                            else: pass
                            
                # If username exists, login the user
                if result is not None:
                    username = result[0]
                    logged_in = True    
                    return username
            
            # If passwords does not match, return an error message and start from the beginning
            else: sender.send(f"{RED + Colors.BOLD}Wrong username or password.{RESET + Colors.RESET}\n")
        
        # If the password could not be fetched from the database, return an error message and start from the beginning
        else: sender.send(f"{RED + Colors.BOLD}User not found.\n{RESET + Colors.RESET}")


def broadcast(message, sent_by="", format: StbCom = StbCom.PLAIN):    
    c = db.cursor()
    
    try:
        if sent_by == "":
            for user in users:
                try:
                    json_builder = {
                        "message_type": StbCom.SYS_MSG,
                        "message": {
                            "content": message
                        }
                    }
                    
                    user.send(send_json(json_builder).encode("utf-8"))
                    
                except BrokenPipeError as e:
                    debug_logger(e, stbexceptions.broken_pipe_warning, type=StbTypes.WARNING)
                    log.warning("You should kick some invalid sessions.")

        else:
            for user in users:
                try: 
                    c.execute('SELECT badge FROM users WHERE username = ?', (sent_by,))
                    user_badge = c.fetchone()
               
                    if user_badge[0] is not None: badge = user_badge[0]    
                    else: badge = ""
                        
                except Exception as e:
                    log.error("Something went wrong while... doing something with the badges?: " + e)
                
                
                c.execute('SELECT role FROM users WHERE username = ?', (sent_by,))
                user_role = c.fetchone()
                
                if user_role[0] != "bot":
                    message = message.strip("\n")
                
                message = escape_ansi(message)
                message = repl_htpf(message)
                
                for u in users.values():
                    if f"@{u}" in message.split():
                        message = message.replace(f"@{u}", f"{BACKMAGENTA + Colors.BOLD}@{userNickname(u)}{BACKRESET + Colors.RESET}")
                
                
                if not is_empty_or_whitespace(message):
                    if message != "":
                        try: 
                            json_builder = {
                                "message_type": StbCom.USER_MSG,
                                "username": sent_by,
                                "nickname": userNickname(sent_by),
                                "badge": badge,
                                "role_color": userRoleColor(sent_by),
                                "avatar_url": userAvatarUrl(sent_by),
                                "message": {
                                    "content": message
                                }
                            }
                            
                            user.send(send_json(json_builder).encode('utf8'))
                            
                        except BrokenPipeError: pass
                    else: pass
                else: pass
                    
        c.close()
                
    except IOError as e:
        if e.errno == errno.EPIPE:
            log.critical(f"Broken Pipe Error. You may need to restart your server! Read more at https://developers.strawberryfoundations.xyz/")
            debug_logger(e, stbexceptions.broken_pipe_error)
            exit(1)
  
    except Exception as e:
        log.error(f"A broadcasting error occurred.")
        debug_logger(e, stbexceptions.communication_error)
        exit(1)



def cleanup(info_msg=True):
    if len(addresses) != 0:
        for sock in addresses.keys():
            sock.close()
        
    if info_msg:
        log.info(f"{YELLOW + Colors.BOLD}Runtime has stopped.{RESET + Colors.RESET}")
    
def server_commands(socket):
    while True:
        # command = input(f"{RESET + Colors.RESET}> ")
        command = input(f"")
        if command == "help":
            print(server_help_section)
            
        elif command == "about":
            print(f"""  {GREEN + Colors.UNDERLINE + Colors.BOLD}About {chat_name}{RESET + Colors.RESET}
  {BLUE + Colors.BOLD}Thank you for using {chat_name}!{RESET}
  {BLUE + Colors.BOLD}Version: {RESET}{short_ver} {codename} ({server_edition}) ({ext_ver})
  {BLUE + Colors.BOLD}Author: {RESET}{", ".join(authors)}{RESET + Colors.RESET}""")
            
        elif command == "exit":
            cleanup(info_msg=False)
            socket.close()
            exit(1)
        
        elif command.startswith("update"):
            args = command.replace("update", "").replace(" ", "")
            
            if online_mode == False:
                print(f"{YELLOW + Colors.BOLD}Updating strawberry-chat is not possible if online mode is disabled.{RESET + Colors.RESET}")
            else:
                check_for_updates(args)
                
                

def main():
    try:
        if test_mode: port = 49200
        else: port = config['server']['port']
        
        all_addresses = False
            
        atexit.register(cleanup)
        
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((ipaddr, port))
        server_socket.listen()
        
        if test_mode:
            print(f"{YELLOW + Colors.BOLD}>>> Enabled test mode{RESET + Colors.RESET}")
            print(f"{GREEN + Colors.BOLD}>>> {RESET}Server is running on {ipaddr}:{port}{RESET + Colors.RESET}")
            _connection_debug = threading.Thread(target=connectionThread, args=(server_socket,), daemon=True)
            _connection_debug.start()
            time.sleep(10)
        
        else:
            if enable_messages: print(f"{YELLOW + Colors.BOLD}>>> Enabled Flag {CYAN}'enable_messages'{RESET + Colors.RESET}")
            if debug_mode: print(f"{YELLOW + Colors.BOLD}>>> Enabled Flag {CYAN}'debug_mode'{RESET + Colors.RESET}")
            if online_mode == False: print(f"{RED + Colors.BOLD}>>> {YELLOW}WARNING:{RED} Online mode is disabled and your server might be in danger! Consider using the online mode!{RESET + Colors.RESET}")
            
            if ipaddr == "0.0.0.0": all_addresses = True
            
            if all_addresses: print(f"{GREEN + Colors.BOLD}>>> {RESET}Server is running on {Colors.ITALIC + MAGENTA}{ipaddr}:{port}{Colors.RESET} (All addresses)\n")
            else: print(f"{GREEN + Colors.BOLD}>>> {RESET}Server is running on {ipaddr}:{port}\n")
            
            _connection = threading.Thread(target=connectionThread, args=(server_socket,))
            _connection.start()
            
            try:
                _cmd = threading.Thread(target=server_commands, args=(server_socket,))
                _cmd.start()
                _cmd.join()
                
            except KeyboardInterrupt: pass

            cleanup()
            server_socket.close()
            log.info("Server stopped")
            
    except KeyboardInterrupt: exit()
    

if __name__ == "__main__":
    main()
    pass
