#!/usr/bin/env python3

import socket
import threading

import os
import sys

import logging
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
from src.db import * 
from src.online import *
from src.commands import PermissionLevel, execute_command, list_commands

from src.commands.default import help, server_info, news, changelog, about
from src.commands.etc import test_command
from src.commands.admin import broadcast

# Startup title
print(f"{CYAN + Colors.BOLD}* -- {chat_name} v{short_ver} {codename} ({server_edition}) -- *{RESET + Colors.RESET}")


# Init logger
class LogFormatter(logging.Formatter):
    format = f"[{datetime.datetime.now().strftime('%H:%M')}] [%(levelname)s]{RESET + Colors.RESET + Colors.BOLD} %(message)s"

    FORMATS = {
        logging.DEBUG:    WHITE  + Style.DIM    + format,
        logging.INFO:     BLUE   + format,
        logging.WARNING:  YELLOW + format,
        logging.ERROR:    RED    + Style.BRIGHT + format,
        logging.CRITICAL: RED    + format
    }

    def format(self, record):
        log_fmt = Style.RESET_ALL + self.FORMATS.get(record.levelno) + Style.RESET_ALL
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


log = logging.getLogger("LOG")

if os.environ.get("LOG_LEVEL") is not None:
    log.setLevel(os.environ.get("LOG_LEVEL").upper())
    
else:
    log.setLevel("INFO")
    
log_fh  = logging.FileHandler(server_dir + '/log.txt')
log_fmt = logging.Formatter(f"(%(asctime)s) [%(levelname)s]  %(message)s")
log_fh.setFormatter(log_fmt)

log_ch = logging.StreamHandler()
log_ch.setFormatter(LogFormatter())

log.addHandler(log_ch)
log.addHandler(log_fh)

# Check if database file exists
if os.path.exists(server_dir + "/users.db"):
    # Connect to database
    db = sql.connect(server_dir + "/users.db", check_same_thread=False)
    # db = Database(server_dir + "/users.db", check_same_thread=False)
    print(f"{GREEN + Colors.BOLD}>>> {RESET}Connected to database")
    
else:
    # Connect/Create database
    # db = sql.connect(server_dir + "/users.db", check_same_thread=False)
    db = Database(server_dir + "/users.db", check_same_thread=False)
    print(f"{GREEN + Colors.BOLD}>>> {RESET}Created database")
    
    db.execute(table_query)
    db.commit()
    
    print(f"{GREEN + Colors.BOLD}>>> {RESET}Created table")


# Open Configuration
with open(server_dir + "/config.yml") as config_data:
        config = yaml.load(config_data, Loader=SafeLoader)

# Configuration
ipaddr                  = config['server']['address']
port                    = config['server']['port']

enable_messages         = config['flags']['enable_messages']
max_message_length      = config['flags']['max_message_length']
debug_mode              = config['flags']['debug_mode']
online_mode             = config['flags']['online_mode']

# Check if online mode is enabled + receive the global ip
if online_mode:
    print(f"{YELLOW + Colors.BOLD}>>> Connecting to the Strawberry API ...{RESET + Colors.RESET}")
    global_ip           = get_global_ip()
    print(f"{GREEN + Colors.BOLD}>>> Connected{RESET + Colors.RESET}")
    
else:
    pass

# Lists & Sets
afks = list([])
blacklist = set()

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


if "--enable-messages" in sys.argv:
    enable_messages = True

if "--debug-mode" in sys.argv:
    debug_mode = True
    
if "--regen-database" in sys.argv:
    ays_input = input(f"{YELLOW + Colors.BOLD}>>> {RESET}WARNING: This will delete your database! Are you sure?: ")
    
    if ays_input.lower() == "yes":
        db.close()
        regen_database()
        
        print(f"{GREEN + Colors.BOLD}>>> {RESET}Created table")
        
    else:
        print(f"{Colors.GRAY + Colors.BOLD}>>> {RESET + Colors.RESET + Colors.BOLD}Cancelled database regeneration process")

if "--test-mode" in sys.argv:
    test_mode = True
    
else:
    test_mode = False


# General Functions

# Get user's nickname
def userNickname(uname):
    c = db.cursor()
    c.execute('SELECT nickname FROM users WHERE username = ?', (uname,))
    unick = c.fetchone()
    c.close()
    
    if unick[0] is not None: 
        unick = unick[0]
        return unick
    
    else:
        return uname

# Check if user has a nickname
def hasNickname(uname):
    c = db.cursor()
    c.execute('SELECT nickname FROM users WHERE username = ?', (uname,))
    unick = c.fetchone()
    c.close()
    
    if unick[0] is not None: 
        return True
    
    else: 
        return False

# Get user role color from the user
def userRoleColor(uname):
    c = db.cursor()
    c.execute('SELECT role_color FROM users WHERE username = ?', (uname,))
    color = c.fetchone()
    c.close()
    
    if color[0] is not None: 
        match color[0]:
            case "red": 
                return RED + Colors.BOLD
            
            case "green": 
                return GREEN + Colors.BOLD
                
            case "cyan": 
                return CYAN + Colors.BOLD
            
            case "blue": 
                return BLUE

            case "yellow": 
                return YELLOW
                
            case "magenta": 
                return MAGENTA
            
            case "lightred":
                return LIGHTRED_EX
            
            case "lightgreen":
                return LIGHTGREEN_EX
            
            case "lightcyan":
                return LIGHTCYAN_EX
            
            case "lightblue":
                return LIGHTBLUE_EX

            case "lightyellow":
                return LIGHTYELLOW_EX

            case "lightmagenta":
                return LIGHTMAGENTA_EX
            
            case "boldred":
                return Colors.BOLD + RED

            case "boldgreen":
                return Colors.BOLD + GREEN
            
            case "boldcyan":
                return Colors.BOLD + CYAN
            
            case "boldblue":
                return Colors.BOLD + BLUE
            
            case "boldyellow":
                return Colors.BOLD + YELLOW
            
            case "boldmagenta":
                return Colors.BOLD + MAGENTA
            
            case _:
                return RESET
    else: 
        return RESET

# Check if user is muted
def isMuted(uname):
    c = db.cursor()
    c.execute('SELECT muted FROM users WHERE username = ?', (uname,))
    mutedStatus = c.fetchone()
    c.close()
    
    if mutedStatus[0] == "true":
        return True
    else: 
        return False

# Check if user's account is enabled
def isAccountEnabled(uname):
    c = db.cursor()
    c.execute('SELECT account_enabled FROM users WHERE username = ?', (uname,))
    accountEnabledStatus = c.fetchone()
    c.close()
    
    if accountEnabledStatus[0] == "true":
        return True
    else: 
        return False

# Print debug error codes
def debugLogger(errorMessage, errorCode, type="error"):
    if debug_mode:
        if type == "error":
            log.error(f"ErrCode {errorCode}: {errorMessage}")
        elif type == "warning":
            log.warning(f"ErrCode {errorCode}: {errorMessage}")
    else:
        None

# SQL error message logger
def sqlError(errorMessage):
    log.error(f"e096: An SQL Error occured: {errorMessage}")

# Check if a user exists
def doesUserExist(uname):
    c = db.cursor()
    uname = uname.lower()
    c.execute('SELECT username FROM users WHERE LOWER(username) = ?', (uname,))
    
    try:
        userExists = c.fetchone()[0]
        
    except:
        return False
    
    if userExists.lower() == uname:
        return True
    
    c.close()

# Print a proper user name information for memberlist command
def memberListNickname(uname):
    c = db.cursor()
    c.execute("SELECT nickname FROM users WHERE username = ?", (uname,))
    nickname = c.fetchone()
    c.close()
    
    if hasNickname(uname):
        return f"{nickname[0]} (@{uname.lower()})"
    
    else:
        return uname


with open(server_dir + "/news.yml") as news_file:
    news_data = yaml.load(news_file, Loader=SafeLoader)
    
# News
news = f"""{GREEN +  Colors.UNDERLINE + Colors.BOLD}{chat_name} News - {short_ver}{RESET + Colors.RESET}{CYAN + Colors.BOLD}
{news_data['news'][base_ver]['text']}{RESET + Colors.RESET}"""



def connectionThread(sock):
    while True:
        try:
            client, address = sock.accept()

        except Exception as e:
            log.error("A connection error occured!")
            debugLogger(e, "001")
            
            break
        
        log.info(f"{address[0]} has connected")
        
        addresses[client] = address
        threading.Thread(target=clientThread, args=(client,)).start()


def clientThread(client):
    # Define db variable global
    global db
    
    address = addresses[client][0]
    
    try:
        user = clientLogin(client)
            
    except Exception as e:
        log.error(f"A login error with {address} occured!")
        debugLogger(e, "002")
        
        del addresses[client]
        return
    
    
    log.info(f"{user} ({address}) logged in")
    users[client] = user

    try:
        client.send(f"{CYAN + Colors.BOLD}Welcome back {user}! Nice to see you!{RESET + Colors.RESET}".encode("utf8"))
        onlineUsersLen = len([user for user in sorted(users.values())])
        
        if onlineUsersLen == 1:
            onlineUsersStr = f"is {onlineUsersLen} user"
        else:
            onlineUsersStr = f"are {onlineUsersLen} users"
            
        time.sleep(0.05)
        client.send(f"""{CYAN + Colors.BOLD}Currently there {onlineUsersStr} online. For help use /help{RESET + Colors.RESET}\n{news}""".encode("utf8"))
        

    except Exception as e:
        log.error(f"A Communication error with {address} ({user}) occurred.")
        debugLogger(e, "003")
        
        del addresses[client]
        del users[client]
        client.close()
        return
    
    time.sleep(0.1)
    broadcast(f"{Colors.GRAY + Colors.BOLD}-->{Colors.RESET} {userRoleColor(user)}{user}{GREEN + Colors.BOLD} has joined the chat room!{RESET + Colors.RESET}")

    while True:
        try:            
            message = client.recv(2048).decode("utf8")
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
                        client.send(f"{YELLOW + Colors.BOLD}Your message is too long.{RESET + Colors.RESET}".encode("utf8"))
                        
                    elif rnd == 1:
                        client.send(f"{YELLOW + Colors.BOLD}boah digga halbe bibel wer liest sich das durch{RESET + Colors.RESET}".encode("utf8"))
                        
                    elif rnd == 2:
                        client.send(f"{YELLOW + Colors.BOLD}junge niemand will sich hier die herr der ringe trilogie durchlesen{RESET + Colors.RESET}".encode("utf8"))

            # Blacklisted Word System
            clcur.execute('SELECT role, enable_blacklisted_words FROM users WHERE username = ?', (user,))    
            res = clcur.fetchone()
            
            if res[0] == "admin" or res[0] == "bot" or res[1] == "false":
                pass
            
            else:
                for word in message.split():
                    word = word.lower()
                    
                    if word in blacklist:
                        client.send(f"{YELLOW + Colors.BOLD}Please be friendlier in the chat. Rejoin when you feel ready!{RESET + Colors.RESET}".encode("utf8"))
                        client.close()
                        
                    else:
                        pass

              
            if message == "/exit":
                client.send(f"{YELLOW + Colors.BOLD}You left the chat!{RESET + Colors.RESET}".encode("utf8"))
                del addresses[client]
                del users[client]
                client.close()
                
                log.info(f"{user} ({address}) has left.")
                broadcast(f"{Colors.GRAY + Colors.BOLD}<--{Colors.RESET} {userRoleColor(user)}{user}{YELLOW + Colors.BOLD} has left the chat room!{RESET + Colors.RESET}")
                break
            
            # Global Command Executor
            elif message.startswith("/"):
                message = message[1:]
                args = message.split()
                cmd = args[0]
                args = args[1:]
                
                try:
                    c.execute('SELECT role FROM users WHERE username = ?', (user,))

                except Exception as e:
                    sqlError(e)
                    
                user_role = c.fetchone()[0]
                role = None
                
                match user_role:
                    case "member":
                        role = PermissionLevel.MEMBER
                    case "admin":
                        role = PermissionLevel.ADMIN
                        
                execute_command(cmd, client, user, role, args)
                continue
            

            if message.startswith("/broadcast ") or message.startswith("/rawsay "):
                try: 
                    c.execute('SELECT role FROM users WHERE username = ?', (user,))
                    
                except Exception as e:
                    sqlError(e)
                    
                res = c.fetchone()
                
                if res[0] == "admin":
                    text = message.replace("/broadcast ", "")
                    
                    if message.startswith("/broadcast "):
                        text = message.replace("/broadcast ", "")
                        
                    elif message.startswith("/rawsay "):
                        text = message.replace("/rawsay ", "")
                    
                    if message == "/broadcast " or message == "/rawsay ":
                        client.send(f"{RED + Colors.BOLD}Wrong usage{RESET + Colors.RESET}".encode("utf8"))
                        continue
                    
                    text = repl_htpf(text)
                            
                    broadcast(f"{text}{RESET + Colors.RESET}")
                    continue
                    
                else:
                    client.send(f"{RED}Sorry, you do not have permissons for that.{RESET}".encode("utf8"))
                    continue
            
    
            # /nick Command
            elif message.startswith("/nick ") or message.startswith("/nickname "):
                if message.startswith("/nick "):
                    arg = message.replace("/nick ", "")
                    
                elif message.startswith("/nickname ") :
                    arg = message.replace("/nickname ", "")
                    
            
                args = arg.split(" ")
                cmd = args[0]
                
                # /nick set                        
                try: 
                    c.execute('SELECT role FROM users WHERE username = ?', (user,))
                    
                except Exception as e:
                    sqlError(e)
                    
                res = c.fetchone()
                
                if cmd == "set":       
                    if res[0] == "admin":              
                        if len(args) == 3:
                            try:
                                nick = args[2]
                                uname = args[1]
                                
                            except:
                                client.send(f"{RED + Colors.BOLD}Please pass a valid argument!{RESET + Colors.RESET}".encode("utf8"))
                                continue
                                
                        
                            c.execute("UPDATE users SET nickname = ? WHERE username = ?", (nick, uname))
                            db.commit()
                            
                            client.send(f"{GREEN + Colors.BOLD}The nickname of {uname} has been updated to '{nick}'{RESET + Colors.RESET}".encode("utf8"))
                            continue
                        
                        else:
                            client.send(f"{RED + Colors.BOLD}Please pass a valid argument!{RESET + Colors.RESET}".encode("utf8"))
                            continue                     
                
                    else:
                        client.send(f"{RED}Sorry, you do not have permissons for that.{RESET}".encode("utf8"))
                        continue
                    
                else:
                    nick = cmd
                    
                    if nick.lower() == "remove":
                        c.execute("UPDATE users SET nickname = NULL WHERE username = ?", (user,))
                        db.commit()
                        
                        client.send(f"{LIGHTGREEN_EX + Colors.BOLD}Removed nickname{RESET + Colors.RESET}".encode("utf8"))
                        continue
                    c.execute("UPDATE users SET nickname = ? WHERE username = ?", (nick, user))
                    db.commit()
                    
                    client.send(f"{LIGHTGREEN_EX + Colors.BOLD}Changed nickname to {RESET + userRoleColor(user)}{nick}{RESET + Colors.RESET}".encode("utf8"))
                    continue
            
            # /member Command
            elif message.startswith("/member ") or message.startswith("/user ") or message == "/user": 
                if message.startswith("/member "):
                    uname = message.replace("/member ", "")
                    
                elif message.startswith("/user "):
                    uname = message.replace("/user ", "")
                
                elif message == "/user":
                    uname = user
                    
                if uname.startswith("me"):
                    uname = user
                
                if uname == "":
                    uname = user
                    
                if doesUserExist(uname) == False:
                    client.send(f"{RED + Colors.BOLD}Sorry, this user does not exist!{RESET + Colors.RESET}".encode("utf8"))
                    continue
                
                def isOnline(uname):
                    if uname in users.values():
                        if uname in afks:
                            return "🌙"
                        
                        else:
                            return "🟢"
                    
                    else:
                        return f"{Colors.GRAY}〇{RESET}"
                
                try:
                    c.execute("SELECT username, nickname, badge, role, role_color, description, badges, discord_name, user_id, strawberry_id, creation_date FROM users WHERE LOWER(username) = ?", (uname.lower(),))
                    
                except:
                    client.send(f"{RED + Colors.BOLD}Sorry, this user does not exist!{RESET + Colors.RESET}".encode("utf8"))
                    continue
                
                for row in c:
                    role = row[3]
                    role_color = row[4]
                    
                    # Nickname
                    if row[1] is not None:
                        nickname = row[1]
                    else:
                        nickname = "Not set"
                        
                    # Badge
                    if row[2] is not None:
                        badge = row[2]
                    else:
                        badge = "Not set"
                    
                    # Description
                    if row[5] is not None:
                        description = row[5]
                    else:
                        description = "Not set"
                    
                    # Discord Username
                    if row[7] is not None:
                        discord = MAGENTA + "@" + row[7]
                    else:
                        discord = "Not set"
                        
                    # Strawberry ID/Network
                    if row[9] is not None:
                        strawberry_id_name = MAGENTA + "@" + row[9]
                    else:
                        strawberry_id_name = "Not set"
                        
                    role = role.capitalize()
                    role_color = role_color.capitalize()
                        
                    crown_badge         = "- 👑 The legendary founder and owner!"
                    cool_badge          = "- 😎 One of the coolest here!"
                    flame_badge         = "- 🔥 The hottest user!"
                    berryjuice_badge    = "- 🫐 Founder and owner of the Berryjuice Client!"
                    bot_badge           = "- 🤖 Just some bot"
                    macher_badge        = "- 💪 In germany we say: \"Macher\""
                    kindness_badge      = "- 👍 The badge of kindness!"
                    troll_badge         = "- 🤡 Someone wo trolls.. watch out"
                    evil_badge          = "- 😈 The opposite of the kindness's badge - The evil badge"
                    supporter_badge     = "- 🤝 Active supporter and helper"
                    newbie_badge        = "- 👋 Say hi! I'm new!"
                    og_badge            = "- 😌 A real OG, who is one of the first members!"
                    strawberry_badge    = "- 🍓 Strawberry ID & Network user!"
                    stbchat_plus_user   = "- 💫 Strawberry Chat+ user"
                    all_badges          = ""

                    badges = row[6]
                    
                    if row[6] is None:
                        badges = ""
                        all_badges = "This user doesn't have any badges yet"
                        
                    else:
                        if "👑" in row[6]:
                            all_badges = all_badges + "\n        " + crown_badge  
                        if "😎" in row[6]:
                            all_badges = all_badges + "\n        " + cool_badge
                        if "🔥" in row[6]:
                            all_badges = all_badges + "\n        " + flame_badge
                        if "🫐" in row[6]:
                            all_badges = all_badges + "\n        " + berryjuice_badge
                        if "🤖" in row[6]:
                            all_badges = all_badges + "\n        " + bot_badge
                        if "💪" in row[6]:
                            all_badges = all_badges + "\n        " + macher_badge
                        if "👍" in row[6]:
                            all_badges = all_badges + "\n        " + kindness_badge
                        if "🤡" in row[6]:
                            all_badges = all_badges + "\n        " + troll_badge
                        if "😈" in row[6]:
                            all_badges = all_badges + "\n        " + evil_badge
                        if "🤝" in row[6]:
                            all_badges = all_badges + "\n        " + supporter_badge
                        if "👋" in row[6]:
                            all_badges = all_badges + "\n        " + newbie_badge
                        if "😌" in row[6]:
                            all_badges = all_badges + "\n        " + og_badge
                        if "🍓" in row[6] or row[9] is not None:
                            all_badges = all_badges + "\n        " + strawberry_badge
                        if "💫" in row[6]:
                            all_badges = all_badges + "\n        " + stbchat_plus_user
                        
                        
                    client.send(
                        f"""{CYAN + Colors.BOLD + Colors.UNDERLINE}User profile of {row[0]}{RESET + Colors.RESET} {isOnline(row[0])}
        {GREEN + Colors.BOLD}Username:{RESET + userRoleColor(row[0])} @{row[0].lower()}{RESET + Colors.RESET}
        {GREEN + Colors.BOLD}User-ID:{RESET + LIGHTBLUE_EX} {row[8]}{RESET + Colors.RESET}
        {GREEN + Colors.BOLD}Nickname:{RESET + Colors.BOLD} {nickname}{RESET + Colors.RESET}
        {GREEN + Colors.BOLD}Description:{RESET + Colors.BOLD} {description}{RESET + Colors.RESET}
        {GREEN + Colors.BOLD}Member since:{RESET + Colors.BOLD} {datetime.datetime.fromtimestamp(row[10]).strftime("%a, %d. %h %Y")}{RESET + Colors.RESET}
        {GREEN + Colors.BOLD}Main Badge:{RESET + Colors.BOLD} {badge}{RESET + Colors.RESET}
        {GREEN + Colors.BOLD}Badges: {badges}{RESET + Colors.BOLD}{RESET + Colors.RESET}{Colors.BOLD}{all_badges}{Colors.RESET}
        {GREEN + Colors.BOLD}Role:{RESET + Colors.BOLD} {role}{RESET + Colors.RESET}
        {GREEN + Colors.BOLD}Role Color:{RESET + Colors.BOLD} {userRoleColor(row[0])}{role_color}{RESET + Colors.RESET}
        {GREEN + Colors.BOLD}Strawberry Network:{RESET + Colors.BOLD} {strawberry_id_name}{RESET + Colors.RESET}
        {GREEN + Colors.BOLD}Discord:{RESET + Colors.BOLD} {discord}{RESET + Colors.RESET}"""
                        .encode("utf8"))
                continue
                
                
            # /mute Command
            elif message.startswith("/mute "):
                try: 
                    c.execute('SELECT role FROM users WHERE username = ?', (user,))
                    
                except Exception as e:
                    sqlError(e)
                    
                res = c.fetchone()
                
                if res[0] == "admin":
                    uname = message.replace("/mute ", "")
                    
                    if doesUserExist(uname) == False:
                        client.send(f"{RED + Colors.BOLD}Sorry, this user does not exist!{RESET + Colors.RESET}".encode("utf8"))
                        continue
                    
                    c.execute("UPDATE users SET muted = 'true' WHERE username = ?", (uname,))
                    db.commit()
                    
                    client.send(f"{LIGHTGREEN_EX + Colors.BOLD}Muted {uname}{RESET + Colors.RESET}".encode("utf8"))
                    continue
                    
                else:
                    client.send(f"{RED}Sorry, you do not have permissons for that.{RESET}".encode("utf8"))
                    
                    
            # /unmute Command
            elif message.startswith("/unmute "):
                try: 
                    c.execute('SELECT role FROM users WHERE username = ?', (user,))
                    
                except Exception as e:
                    sqlError(e)
                    
                res = c.fetchone()
                
                if res[0] == "admin":
                    uname = message.replace("/unmute ", "")
                    
                    if doesUserExist(uname) == False:
                        client.send(f"{RED + Colors.BOLD}Sorry, this user does not exist!{RESET + Colors.RESET}".encode("utf8"))
                        continue
                    
                    c.execute("UPDATE users SET muted = 'false' WHERE username = ?", (uname,))
                    db.commit()
                    
                    client.send(f"{LIGHTGREEN_EX + Colors.BOLD}Unmuted {uname}{RESET + Colors.RESET}".encode("utf8"))
                    continue
                    
                else:
                    client.send(f"{RED}Sorry, you do not have permissons for that.{RESET}".encode("utf8"))
            
            
            # /discord Command
            elif message.startswith("/discord "):
                discord_name = message.replace("/discord ", "")

                if discord_name.lower() == "remove":
                    c.execute("UPDATE users SET discord_name = NULL WHERE username = ?", (user,))
                    db.commit()
                    
                    client.send(f"{LIGHTGREEN_EX + Colors.BOLD}Removed Discord Link{RESET + Colors.RESET}".encode("utf8"))
                    continue
                
                c.execute("UPDATE users SET discord_name = ? WHERE username = ?", (discord_name, user))
                db.commit()
                
                client.send(f"{LIGHTGREEN_EX + Colors.BOLD}Changed Discord Link to {MAGENTA}{discord_name}{RESET + Colors.RESET}".encode("utf8"))
                continue

            
            # /description Command
            elif message.startswith("/description "):
                desc = message.replace("/description ", "")

                if desc.lower() == "remove" or desc.lower() == "reset":
                    c.execute("UPDATE users SET description = NULL WHERE username = ?", (user,))
                    db.commit()
                    
                    client.send(f"{LIGHTGREEN_EX + Colors.BOLD}Removed Description{RESET + Colors.RESET}".encode("utf8"))
                    continue
                
                elif desc.lower() == "" or desc.lower() == " ":
                    c.execute("SELECT description FROM users WHERE username = ?", (user,))
                    desc = c.fetchone()[0]
                    
                    client.send(f"{LIGHTGREEN_EX + Colors.BOLD}Your current description: {RESET}{desc}{Colors.RESET}".encode("utf8"))
                    continue
                
                c.execute("UPDATE users SET description = ? WHERE username = ?", (desc, user))
                db.commit()
                
                client.send(f"{LIGHTGREEN_EX + Colors.BOLD}Changed Description to {CYAN}{desc}{RESET + Colors.RESET}".encode("utf8"))
                continue

        
            # /ban Command
            elif message.startswith("/ban "):
                try: 
                    c.execute('SELECT role FROM users WHERE username = ?', (user,))
                    
                except Exception as e:
                    sqlError(e)
                    
                res = c.fetchone()
                
                if res[0] == "admin":
                    uname = message.replace("/ban ", "")
                    
                    if doesUserExist(uname) == False:
                        client.send(f"{RED + Colors.BOLD}Sorry, this user does not exist!{RESET + Colors.RESET}".encode("utf8"))
                        continue
                    
                    c.execute("UPDATE users SET account_enabled = 'false' WHERE username = ?", (uname,))
                    db.commit()
                    
                    client.send(f"{LIGHTGREEN_EX + Colors.BOLD}Banned {uname}{RESET + Colors.RESET}".encode("utf8"))
                    continue
                    
                else:
                    client.send(f"{RED}Sorry, you do not have permissons for that.{RESET}".encode("utf8"))
            
            
            # /unban Command
            elif message.startswith("/unban "):
                try: 
                    c.execute('SELECT role FROM users WHERE username = ?', (user,))
                    
                except Exception as e:
                    sqlError(e)
                    
                res = c.fetchone()
                
                if res[0] == "admin":
                    uname = message.replace("/unban ", "")
                    
                    if doesUserExist(uname) == False:
                        client.send(f"{RED + Colors.BOLD}Sorry, this user does not exist!{RESET + Colors.RESET}".encode("utf8"))
                        continue
                    
                    c.execute("UPDATE users SET account_enabled = 'true' WHERE username = ?", (uname,))
                    db.commit()
                    
                    client.send(f"{LIGHTGREEN_EX + Colors.BOLD}Unbanned {uname}{RESET + Colors.RESET}".encode("utf8"))
                    continue
                    
                else:
                    client.send(f"{RED}Sorry, you do not have permissons for that.{RESET}".encode("utf8"))
            
            
            # /role Command
            elif message.startswith("/role "):
                try: 
                    c.execute('SELECT role FROM users WHERE username = ?', (user,))
                    
                except Exception as e: 
                    sqlError(e)
                    
                res = c.fetchone()
                
                if res[0] == "admin":
                    arg = message.replace("/role ", "")
                    args = arg.split(" ")

                    cmd = args[0]
                    
                    # /role set Command
                    if cmd == "set":
                        try:
                            uname = args[1]
                            role = args[2]
                        
                            c.execute("UPDATE users SET role = ? WHERE username = ?", (role, uname))
                            db.commit()
                            
                            client.send(f"{LIGHTGREEN_EX + Colors.BOLD}Role of {uname} was set to {role}{RESET + Colors.RESET}".encode("utf8"))
                            continue
                        
                        except:
                            client.send(f"{RED + Colors.BOLD}Invalid username and/or role!{RESET + Colors.RESET}".encode("utf8"))
                            continue
                    
                    # /role get Command
                    elif cmd == "get":
                        try:
                            uname = args[1]
                      
                            c.execute("SELECT role FROM users WHERE username = ?", (uname,))
                            role = c.fetchone()[0]
                            
                            client.send(f"{LIGHTGREEN_EX + Colors.BOLD}Role of {uname}: {MAGENTA}{role}{RESET + Colors.RESET}".encode("utf8"))
                            continue
                        
                        except:
                            client.send(f"{RED + Colors.BOLD}Invalid username!{RESET + Colors.RESET}".encode("utf8"))
                            continue
                    
                    # /role color Command
                    elif cmd == "color":
                        try:
                            uname = args[1]
                            color = args[2]
                        
                            c.execute("UPDATE users SET role_color = ? WHERE username = ?", (color, uname))
                            db.commit()
                            
                            client.send(f"{LIGHTGREEN_EX + Colors.BOLD}Role Color of {uname} was set to {color}{RESET + Colors.RESET}".encode("utf8"))
                            continue
                    
                        except:
                            client.send(f"{RED + Colors.BOLD}Invalid username and/or color!{RESET + Colors.RESET}".encode("utf8"))
                            continue
                        
                    else:
                        client.send(f"{RED + Colors.BOLD}Invalid command usage.{RESET + Colors.RESET}".encode("utf8"))
                        continue
                    
                else:
                    client.send(f"{RED}Sorry, you do not have permissons for that.{RESET}".encode("utf8"))
            
            
            # /bwords Command
            elif message.startswith("/bwords "):
                try: 
                    c.execute('SELECT role FROM users WHERE username = ?', (user,))
                    
                except Exception as e:
                    sqlError(e)
                    
                res = c.fetchone()
                
                if res[0] == "admin":
                    arg = message.replace("/bwords ", "")
                    args = arg.split(" ")

                    cmd = args[0]
                    
                    # /bwords set
                    if cmd == "set":
                        try:
                            uname = args[1]
                            value = args[2]
                            
                            if doesUserExist(uname) == False:
                                client.send(f"{RED + Colors.BOLD}Sorry, this user does not exist!{RESET + Colors.RESET}".encode("utf8"))
                                continue
                         
                            c.execute("UPDATE users SET enable_blacklisted_words = ? WHERE username = ?", (value, uname))
                            db.commit()
                        
                            if value == "true":
                                client.send(f"{LIGHTGREEN_EX + Colors.BOLD}Enabled Blacklisted Words for {uname}{RESET + Colors.RESET}".encode("utf8"))
                                continue
                            
                            elif value == "false":
                                client.send(f"{LIGHTGREEN_EX + Colors.BOLD}Disabled Blacklisted Words for {uname}{RESET + Colors.RESET}".encode("utf8"))
                                continue
                            
                            else:
                                client.send(f"{RED + Colors.BOLD}Invalid value!{RESET + Colors.RESET}".encode("utf8"))
                                continue
                    
                        except:
                            client.send(f"{RED + Colors.BOLD}Invalid username and/or value!{RESET + Colors.RESET}".encode("utf8"))
                            continue
                        
                    # /bwords get
                    elif cmd == "get":
                        try:
                            uname = args[1]
                                
                            c.execute("SELECT enable_blacklisted_words FROM users WHERE username = ?", (uname,))
                            value = c.fetchone()[0]
                            
                            if value == "true":
                                client.send(f"{LIGHTGREEN_EX + Colors.BOLD}Blacklisted Words for {uname} are enabled{RESET + Colors.RESET}".encode("utf8"))
                                continue
                            
                            elif value == "false":
                                client.send(f"{LIGHTGREEN_EX + Colors.BOLD}Blacklisted Words for {uname} are disabled{RESET + Colors.RESET}".encode("utf8"))
                                continue
                            
                            else:
                                client.send(f"{RED + Colors.BOLD}Whoa! This should not happen...{RESET + Colors.RESET}".encode("utf8"))
                                continue
                        except:
                            client.send(f"{RED + Colors.BOLD}Invalid username{RESET + Colors.RESET}".encode("utf8"))
                            continue
                           
                    # /bwords add 
                    elif cmd == "add":
                        try:
                            word = args[1]
                        except:
                            client.send(f"{RED + Colors.BOLD}Cant add an empty word!{RESET + Colors.RESET}".encode("utf8"))
                            continue
                        
                        if word == "":
                            client.send(f"{RED + Colors.BOLD}Cant add an empty word!{RESET + Colors.RESET}".encode("utf8"))
                            continue
                        
                        with open("blacklist.txt", "a") as f:
                            f.write("\n" + word)
                            f.close()
                        
                        client.send(f"{LIGHTGREEN_EX + Colors.BOLD}Added '{word}' to the blacklist{RESET + Colors.RESET}".encode("utf8"))
                        continue
                    
                    # /bwords reload
                    elif cmd == "reload":
                        try: 
                            c.execute('SELECT role FROM users WHERE username = ?', (user,))
                            
                        except Exception as e:
                            sqlError(e)
                            
                        res = c.fetchone()
                        
                        if res[0] == "admin":
                            with open("blacklist.txt", "r") as f:
                                for word in f:
                                    word = word.strip().lower()
                                    blacklist.add(word)
                                    
                            client.send(f"{GREEN + Colors.BOLD}Reloaded blacklisted words.{RESET + Colors.RESET}".encode("utf8"))
                            continue
                            
                        else:
                            client.send(f"{RED}Sorry, you do not have permissons for that.{RESET}".encode("utf8"))
                            
                    else:
                        client.send(f"{RED + Colors.BOLD}Invalid command usage.{RESET + Colors.RESET}".encode("utf8"))
                        continue
                    
                else:
                    client.send(f"{RED}Sorry, you do not have permissons for that.{RESET}".encode("utf8"))
            
            
            # /badge Command
            elif message.startswith("/badge "):
                try: 
                    c.execute('SELECT role FROM users WHERE username = ?', (user,))
                    
                except Exception as e:
                    sqlError(e)
                    
                res = c.fetchone()
                
                if res[0] == "admin":
                    arg = message.replace("/badge ", "")
                    args = arg.split(" ")

                    cmd = args[0]
                    
                    
                    # /badge add
                    if cmd == "add":
                        # If no username is provided
                        if len(args) == 2:
                            try:
                                badge_to_add = args[1]
                                
                            except:
                                client.send(f"{RED + Colors.BOLD}Please pass a valid argument!{RESET + Colors.RESET}".encode("utf8"))
                                continue
                                
                            c.execute("SELECT badges FROM users WHERE username = ?", (user,))
                            
                            user_badges = c.fetchone()[0]
                            
                            # Does the user already have this badge?
                            if badge_to_add in user_badges:
                                client.send(f"{RED + Colors.BOLD}This badge is already assigned to your profile!{RESET + Colors.RESET}".encode("utf8"))
                                continue
                            
                            new_user_badges = user_badges + badge_to_add
                            
                            c.execute("UPDATE users SET badges = ? WHERE username = ?", (new_user_badges, user))
                            db.commit()
                            
                            client.send(f"{GREEN + Colors.BOLD}Added badge '{badge_to_add}' to your user profile{RESET + Colors.RESET}".encode("utf8"))
                            continue
                        
                        # If username is provided
                        elif len(args) == 3:
                            try:
                                badge_to_add = args[1]
                                uname = args[2]
                                
                            except:
                                client.send(f"{RED + Colors.BOLD}Please pass a valid argument!{RESET + Colors.RESET}".encode("utf8"))
                                continue
                                
                            if doesUserExist(uname) == False:
                                client.send(f"{RED + Colors.BOLD}Sorry, this user does not exist!{RESET + Colors.RESET}".encode("utf8"))
                                continue
                            
                            else: 
                                c.execute("SELECT badges FROM users WHERE username = ?", (uname,))
                            
                                user_badges = c.fetchone()[0]
                                
                                # Does the user already have this badge?
                                if badge_to_add in user_badges:
                                    client.send(f"{RED + Colors.BOLD}This badge is already assigned to {uname}'s profile!{RESET + Colors.RESET}".encode("utf8"))
                                    continue
                                
                                new_user_badges = user_badges + badge_to_add
                                
                                c.execute("UPDATE users SET badges = ? WHERE username = ?", (new_user_badges, uname))
                                db.commit()
                                
                                client.send(f"{GREEN + Colors.BOLD}Added badge '{badge_to_add}' to {uname}'s profile{RESET + Colors.RESET}".encode("utf8"))
                                continue
                            
                        elif len(args) < 2 or len(args) > 3:
                            client.send(f"{RED + Colors.BOLD}Invalid command usage.{RESET + Colors.RESET}".encode("utf8"))
                            continue
                                            
                else:
                    client.send(f"{RED}Sorry, you do not have permissons for that.{RESET}".encode("utf8"))
                    continue

                # /badge set
                if cmd == "set":
                    # If no username is provided
                    if len(args) == 2:
                        try:
                            badge_to_set = args[1]
                            
                        except:
                            client.send(f"{RED + Colors.BOLD}Please pass a valid argument!{RESET + Colors.RESET}".encode("utf8"))
                            continue
                            
                        c.execute("SELECT badges FROM users WHERE username = ?", (user,))
                        
                        user_badges = c.fetchone()[0]
                        
                        # Does the user have this badge?
                        if badge_to_set in user_badges:
                        
                            c.execute("UPDATE users SET badge = ? WHERE username = ?", (badge_to_set, user))
                            db.commit()
                            
                            client.send(f"{GREEN + Colors.BOLD}The main badge of you has been updated to '{badge_to_set}'{RESET + Colors.RESET}".encode("utf8"))
                            continue
                        
                        else:
                            client.send(f"{RED + Colors.BOLD}You do not own this badge!{RESET + Colors.RESET}".encode("utf8"))
                            continue
                        
                    # If username is provided
                    elif len(args) == 3:
                        if res[0] == "admin":
                            try:
                                badge_to_set = args[1]
                                uname = args[2]
                                
                                if uname == "":
                                    client.send(f"{RED + Colors.BOLD}Please provide a valid username! If you try to change your own main badge, please do not add a space after the badge!{RESET + Colors.RESET}".encode("utf8"))
                                    continue
                                
                            except:
                                client.send(f"{RED + Colors.BOLD}Please pass a valid argument!{RESET + Colors.RESET}".encode("utf8"))
                                continue
                                
                            if doesUserExist(uname) == False:
                                client.send(f"{RED + Colors.BOLD}Sorry, this user does not exist!{RESET + Colors.RESET}".encode("utf8"))
                                continue
                            
                            else: 
                                c.execute("SELECT badges FROM users WHERE username = ?", (uname,))
                            
                                user_badges = c.fetchone()[0]
                                
                                # Does the user have this badge?
                                if badge_to_set in user_badges:
                                        
                                    c.execute("UPDATE users SET badge = ? WHERE username = ?", (badge_to_set, uname))
                                    db.commit()
                                    
                                    client.send(f"{GREEN + Colors.BOLD}The main badge of {uname} has been updated to '{badge_to_set}'{RESET + Colors.RESET}".encode("utf8"))
                                    continue
                                
                                else:
                                    client.send(f"{RED + Colors.BOLD}This user does not own this badge!{RESET + Colors.RESET}".encode("utf8"))
                                    continue
                        else:
                            client.send(f"{RED}Sorry, you do not have permissons for that.{RESET}".encode("utf8"))
                            continue
                        
                    elif len(args) < 2 or len(args) > 3:
                        client.send(f"{RED + Colors.BOLD}Invalid command usage.{RESET + Colors.RESET}".encode("utf8"))
                        continue
            
            
            elif message.startswith("/dm "):                
                arg = message.replace("/dm ", "")
                args = arg.split(" ")

                uname   = args[0]
                msg     = ' '.join(args[1:])
                msg     = escape_ansi(msg)
                msg     = msg.strip("\n")
                
                search_val = uname
                found_keys = []
                
                for key, value in users.items():
                    if value == search_val:
                        global to_sent
                        to_sent = key
                        found_keys.append(key)
                    
                try:
                    c.execute("SELECT enable_dms FROM users WHERE username = ?", (uname,))
                    has_dm_enabled = c.fetchone()[0]
                    
                except:
                    client.send(f"{RED + Colors.BOLD}User not found{RESET + Colors.RESET}".encode("utf8"))
                    continue
                        
                if uname == user:
                    client.send(f"{YELLOW}You shouldn't send messages to yourself...{RESET}".encode("utf8"))
                    continue
                
                elif uname in afks:
                    client.send(f"{YELLOW}This user is currently afk...{RESET}".encode("utf8"))
                    continue
                
                elif has_dm_enabled == "false":
                    client.send(f"{YELLOW}This user has deactivated his/her DM's{RESET}".encode("utf8"))
                    continue
                
                else:
                    if found_keys:
                        client.send(f"{userRoleColor(user)}You{RESET} {Colors.GRAY}-->{Colors.RESET} {userRoleColor(uname)}{uname}{RESET + Colors.RESET}: {msg}".encode("utf8"))
                        to_sent.send(f"{Colors.RESET + userRoleColor(user)}{user} {Colors.GRAY}-->{RESET + Colors.RESET}{userRoleColor(uname)} You{Colors.RESET + RESET}: {msg}".encode("utf8"))
                        
                    else:
                        client.send(f"{RED + Colors.BOLD}User is offline.{RESET + Colors.RESET}".encode("utf8"))
                        
                    continue
                
            
            elif message.startswith("/kick "):
                try: 
                    c.execute('SELECT role FROM users WHERE username = ?', (user,))
                    
                except Exception as e:
                    sqlError(e)
                    
                res = c.fetchone()
                
                if res[0] == "admin":
                    arg = message.replace("/kick ", "")
                    args = arg.split(" ")

                    uname   = args[0]
                    reason  = ' '.join(args[1:])
                    
                    if reason == "":
                        reason = "No reason provided"
                    
                    search_val = uname
                    found_keys = []
                    
                    for key, value in users.items():
                        if value == search_val:
                            global to_kick
                            to_kick = key
                            found_keys.append(key)
                            
                    if uname == user:
                        client.send(f"{YELLOW}You shouldn't kick yourself...{RESET}".encode("utf8"))
                        continue
                    
                    else:
                        if found_keys:
                            client.send(f"{YELLOW + Colors.BOLD}Kicked {uname} for following reason: {reason}{RESET + Colors.RESET}".encode("utf8"))
                            to_kick.send(f"{YELLOW + Colors.BOLD}You have been kicked out of the chat for the following reason: {reason}{RESET + Colors.RESET}".encode("utf8"))
                            
                            try:
                                del addresses[to_kick]
                                del users[to_kick]
                                to_kick.close()
                                
                            except Exception as e: 
                                log.warning("A socket-to-client exception occured")
                                debugLogger(e, "005", type="warning")
                            
                        else:
                            client.send(f"{RED + Colors.BOLD}User not found or user is offline.{RESET + Colors.RESET}".encode("utf8"))
                            
                        continue
                
                else:
                    client.send(f"{RED}Sorry, you do not have permissons for that.{RESET}".encode("utf8"))
                    continue
                    "".encode
            
            elif message.startswith("/news "):
                arg = message.replace("/news ", "")
                args = arg.split(" ")

                cmd = args[0]
                
                # Open News YML file
                with open(server_dir + "/news.yml") as news_file:
                    news_data = yaml.load(news_file, Loader=SafeLoader)
                        
                if cmd == "list":
                    version_list = ", ".join(news_data['versions'])
                    client.send(f"{CYAN + Colors.BOLD}{chat_name} Versions:{RESET + Colors.RESET} {GREEN}{version_list}{RESET}".encode("utf8"))
                    continue
                    
                elif cmd == "show":
                    try:
                        i_ver = args[1] 
                        client.send(f"{GREEN + Colors.BOLD + Colors.UNDERLINE}{chat_name} News - v{i_ver}{RESET + Colors.RESET + CYAN + Colors.BOLD}\n{news_data['news'][i_ver]['text']}{RESET + Colors.RESET}".encode("utf8"))
                        
                    except:
                        client.send(f"{RED + Colors.BOLD}This version of {chat_name} does not exist.{RESET + Colors.RESET}".encode("utf8"))
                        
                    continue
                
                else:
                    client.send(f"{RED + Colors.BOLD}Invalid command usage.{RESET + Colors.RESET}".encode("utf8"))
                    
                    continue
                    
                                


            # Match-Case-Pattern Commands
            match message:
                # Quit / Exit Command
                case "/quit" | "/exit":
                    client.send(f"{YELLOW + Colors.BOLD}You left the chat!{RESET + Colors.RESET}".encode("utf8"))
                    del addresses[client]
                    del users[client]
                    client.close()
                    
                    log.info(f"{user} ({address}) has left.")
                    broadcast(f"{Colors.GRAY + Colors.BOLD}<--{Colors.RESET} {userRoleColor(user)}{user}{YELLOW + Colors.BOLD} has left the chat room!{RESET + Colors.RESET}")
                    break

                # Online Command
                case "/online":
                    onlineUsers = ', '.join([user for user in sorted(users.values())])
                    onlineUsersLen2 = len([user for user in sorted(users.values())])
                    client.send(f"""{GREEN +  Colors.UNDERLINE + Colors.BOLD}Users who are currently online ({onlineUsersLen2}){RESET + Colors.RESET}
        {Colors.BOLD}->{Colors.RESET} {CYAN}{onlineUsers}{RESET + Colors.RESET}""".encode("utf8"))
                
                
                # Afk Command
                case "/afk":
                    if user in afks:
                        client.send(f"{YELLOW + Colors.BOLD}You are already AFK!{RESET + Colors.RESET}".encode("utf8"))
                        
                    else:
                        broadcast(f"{user} is now AFK 🌙..")
                        afks.append(user)
                
                
                # Unafk Comamnd
                case "/unafk":
                    if user not in afks:
                        client.send(f"{YELLOW + Colors.BOLD}You are not AFK!{RESET + Colors.RESET}".encode("utf8"))
                    
                    else:
                        broadcast(f"{user} is no longer AFK 🌻!")
                        afks.remove(user)
                    
                    
                # Whois Afk Command
                case "/afks" | "/afklist":
                    afkUsers = ', '.join([afks for afks in sorted(afks)])
                    afkUsersLen = len([afks for afks in sorted(afks)])
                    client.send(f"""{GREEN +  Colors.UNDERLINE + Colors.BOLD}Users who are currently Afk ({afkUsersLen}){RESET + Colors.RESET}
        {Colors.BOLD}->{Colors.RESET} {CYAN}{afkUsers}{RESET}""".encode("utf8"))
                
                
                # Debug Command
                case "/debug":
                    try: 
                        c.execute('SELECT role FROM users WHERE username = ?', (user,))
                        
                    except Exception as e:
                        sqlError(e)
                        
                    res = c.fetchone()
                    
                    if res[0] == "admin":
                        client.send(f"""Client Object: {client}
        IP Object: {addresses[client]}
        User Object: {users[client]}
        Addresses: {addresses}
        Users: {users}""".encode("utf8"))
                        
                    else:
                        client.send(f"{RED}Sorry, you do not have permissons for that.{RESET}".encode("utf8"))
                
                # Shrug Command
                case "/shrug":
                    broadcast("¯\_(ツ)_/¯", user)
                
                
                # Tableflip Command
                case "/tableflip":
                    broadcast("(╯°□°)╯︵ ┻━┻", user)
                
                
                # Unflip Command
                case "/unflip":
                    broadcast("┬─┬ノ( º _ ºノ)", user)
                
                
                # About Command
                case "/about":
                    client.send(
                        f"""{GREEN +  Colors.UNDERLINE + Colors.BOLD}About {chat_name}{RESET + Colors.RESET}
        {BLUE + Colors.BOLD}Thank you for using {chat_name}!{RESET}
        {BLUE + Colors.BOLD}Version: {RESET}{short_ver} {codename} ({server_edition})
        {BLUE + Colors.BOLD}Author: {RESET}{", ".join(authors)}{RESET + Colors.RESET}"""
        .encode("utf8"))
                    
                # Clientinfo Command
                case "/clientinfo":
                    client.send(f"{addresses[client]}".encode("utf8"))
                    time.sleep(0.1)
                    client.send(f"{users[client]}".encode("utf8"))
                    time.sleep(0.1)
                    client.send(f"{client}".encode("utf8"))
                    
                
                # Member Command
                case "/members" | "/users":
                    c.execute("SELECT username FROM users")
                    raw_members = c.fetchall()
                    membersLen = len([raw_members for raw_members in sorted(raw_members)])
                    members = ", ".join([result[0] for result in raw_members])

                    client.send(f"""{CYAN +  Colors.UNDERLINE + Colors.BOLD}Members on this server ({membersLen}){RESET + Colors.RESET}
        {Colors.BOLD}->{Colors.RESET} {CYAN}{members}{RESET}""".encode("utf8"))
                    
                
                case "/memberlist" | "/userlist":
                    def isOnline(uname):
                        if uname in users.values():
                            if uname in afks:
                                return "🌙"
                            
                            else:
                                return "🟢"
                        
                        else:
                            return f"{Colors.GRAY}〇{RESET}"
            
                    
                    c.execute("SELECT username FROM users")
                    raw_members = c.fetchall()
                    membersLen  = len([raw_members for raw_members in sorted(raw_members)])
                    
                    c.execute("SELECT username, badge FROM users WHERE role = 'admin'")
                    raw_admins  = c.fetchall()
                    admins_len  = len([raw_admins for raw_admins in sorted(raw_admins)])
                    admins      = "\n           ".join([f"{isOnline(result[0])}{LIGHTRED_EX} {memberListNickname(result[0])} [{result[1]}]" for result in raw_admins])
                    
                    c.execute("SELECT username, badge FROM users WHERE role = 'bot'")
                    raw_bots    = c.fetchall()
                    bots_len    = len([raw_bots for raw_bots in sorted(raw_bots)])
                    bots      = "\n           ".join([f"{isOnline(result[0])}{LIGHTMAGENTA_EX} {memberListNickname(result[0])} [{result[1]}]" for result in raw_bots])
                    
                    
                    c.execute("SELECT username, badge FROM users WHERE role = 'member'")
                    raw_members = c.fetchall()
                    members_len = len([raw_members for raw_members in sorted(raw_members)])
                    members      = "\n           ".join([f"{isOnline(result[0])}{LIGHTYELLOW_EX} {memberListNickname(result[0])} [{result[1]}]" for result in raw_members])
                    
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
                    
                    client.send(f"""{CYAN +  Colors.UNDERLINE + Colors.BOLD}{verified_txt}{config['server']['name'].upper()} ({membersLen} Members, {onlineUsersLen2} Online){RESET + Colors.RESET}
        {Colors.BOLD}->{Colors.RESET} {RED}Administrators ({admins_len}){RESET}
           {LIGHTRED_EX}{admins}{RESET}
           
        {Colors.BOLD}->{Colors.RESET} {MAGENTA}Bots ({bots_len}){RESET}
           {LIGHTMAGENTA_EX}{bots}{RESET}
           
        {Colors.BOLD}->{Colors.RESET} {YELLOW}Members ({members_len}){RESET}
           {LIGHTYELLOW_EX}{members}{RESET}
        """
        
        .encode("utf8"))
                
                
                # Show Description Command
                case "/description" | "/desc":
                    c.execute("SELECT description FROM users WHERE username = ?", (user,))
                    desc = c.fetchone()[0]
                    client.send(f"{LIGHTGREEN_EX + Colors.BOLD}Your current description: {RESET}{desc}{Colors.RESET}".encode("utf8"))                
                
                # Delete Account Command
                case "/deleteaccount":
                    client.send(f"{YELLOW + Colors.BOLD}Are you sure you want to delete your user account? This action is irreversible!!{RESET + Colors.RESET}".encode("utf8"))
                    confirmDelete1 = client.recv(2048).decode("utf8")
                    
                    if confirmDelete1.lower() == "yes":
                        client.send(f"{RED + Colors.BOLD}THIS IS YOUR VERY LAST WARNING! This action is irreversible!! ARE YOU SURE?{RESET + Colors.RESET}".encode("utf8"))
                        confirmDelete2 = client.recv(2048).decode("utf8")
                        
                        if confirmDelete2.lower() == "yes":
                            client.send(f"{YELLOW + Colors.BOLD}Enter your username to confirm the deletion of your account:{RESET + Colors.RESET}".encode("utf8"))
                            confirmUsernameDelete = client.recv(2048).decode("utf8")
                            
                            if confirmUsernameDelete == user:
                                client.send(f"{YELLOW + Colors.BOLD}Deleting your user account...{RESET + Colors.RESET}".encode("utf8"))
                                
                                try:
                                    c.execute("DELETE FROM users WHERE username = ?", (user,))
                                    db.commit()
                                    client.send(f"{GREEN + Colors.BOLD}Deleted{RESET + Colors.RESET}".encode("utf8"))
                                    client.close()
                                    
                                except Exception as e:
                                    log.error(e)
                                    
                            else: 
                                client.send(f"{YELLOW + Colors.BOLD}Deletion of your account has been canceled...{RESET + Colors.RESET}".encode("utf8"))
                        else:
                            client.send(f"{YELLOW + Colors.BOLD}Deletion of your account has been canceled...{RESET + Colors.RESET}".encode("utf8"))
                    else:
                        client.send(f"{YELLOW + Colors.BOLD}Deletion of your account has been canceled...{RESET + Colors.RESET}".encode("utf8"))
   
                
                case "/msgcount":
                    c.execute("SELECT msg_count FROM users WHERE username = ?", (user,))
                    msg_count = c.fetchone()
                    client.send(f"{GREEN + Colors.BOLD}Your message count:{RESET + Colors.RESET} {msg_count[0]}".encode("utf8"))
                case "/":
                    client.send(f"{GREEN + Colors.BOLD}Need help? Take a look at our help command! /help{RESET + Colors.RESET}".encode("utf8"))
                    
                
                case _:
                    
                    if user in afks:
                        client.send(f"{RED}Sorry, you are AFK.{RESET}".encode("utf8"))
                        
                    elif isMuted(user) == True:
                        client.send(f"{RED + Colors.BOLD}Sorry, but you were muted by an administrator. Please contact him/her if you have done nothing wrong, or wait until you are unmuted.{RESET + Colors.RESET}".encode("utf8"))
                    
                    elif isAccountEnabled(user) == False:
                        client.send(f"{RED + Colors.BOLD}Your account was disabled by an administrator.{RESET + Colors.RESET}".encode("utf8"))
                        
                    else:
                        if enable_messages == True:
                            log_msg = escape_ansi(message)
                            log_msg = message.strip("\n")
                            
                            log.info(f"{user} ({address}): {log_msg}")
                                
                        broadcast(message, user)
                        try:
                            c.execute("SELECT msg_count FROM users WHERE username = ?", (user,))
                            msg_count = c.fetchone()
                            msg_count = msg_count[0] + 1
                            c.execute("UPDATE users SET msg_count = ? WHERE username = ?", (msg_count, user))
                            db.commit()
                            
                        except Exception as e:
                            sqlError(e)
            c.close()            
                
        except Exception as e:
            log.error("A client-side error occurred.")
            
            debugLogger(e, "004")
            traceback.print_exc()
            log.info(f"{user} ({address}) has left")
            
            try:
                del addresses[client]
                del users[client]
                client.close()
                
            except Exception as e:
                log.warning("A socket-to-client exception occured")
                debugLogger(e, "005", type="warning")
            
            broadcast(f"{Colors.GRAY + Colors.BOLD}<--{Colors.RESET} {userRoleColor(user)}{user}{YELLOW + Colors.BOLD} has left the chat room!{RESET + Colors.RESET}")
            break


def clientLogin(client):
    global db
    global logcur
    logcur = db.cursor()
    
    def register():
        global db
        global logcur
        client.send(f"{MAGENTA + Colors.BOLD + Colors.UNDERLINE}Welcome!{RESET + Colors.RESET}\n        {Colors.BOLD}Register, to chat with us!{Colors.RESET}".encode("utf8"))
    
        time.sleep(0.05)
        client.send(f"{GREEN + Colors.BOLD}Username: {RESET + Colors.RESET}".encode("utf8"))
        registeredUsername = client.recv(2048).decode("utf8")
        
        if registeredUsername.lower() == "exit":
            client.close()
            sys.exit()
        
        for uname in registeredUsername.split():
            uname = uname.lower()
            
            if uname in blacklist:
                client.send(f"{YELLOW + Colors.BOLD}This username is not allowed{RESET + Colors.RESET}".encode("utf8"))    
                client.close()
                sys.exit()
        try:
            logcur.execute("SELECT username FROM users WHERE username = ? ", (registeredUsername,))
            
            usedUsernames = logcur.fetchall()[0]
            usedUsernames = "".join(usedUsernames)
            
            
            if usedUsernames == usedUsernames:
                client.send(f"{YELLOW + Colors.BOLD}This username is already in use!{RESET + Colors.RESET}".encode("utf8"))    
                register()
            
        except:
            pass
    
        client.send(f"{GREEN + Colors.BOLD}Password: {RESET + Colors.RESET}".encode("utf8"))
        registeredPassword = client.recv(2048).decode("utf8")
        
        client.send(f"{GREEN + Colors.BOLD}Confirm Password: {RESET + Colors.RESET}".encode("utf8"))
        confirmPassword = client.recv(2048).decode("utf8")
        
        if registeredPassword != confirmPassword:
            client.send(f"{RED + Colors.BOLD}Passwords do not match{RESET + Colors.RESET}".encode("utf8"))
            register()
        
        client.send(f"{GREEN + Colors.BOLD}Role Color (Red, Green, Cyan, Blue, Yellow, Magenta): {RESET + Colors.RESET}".encode("utf8"))
        registeredRoleColor = client.recv(2048).decode("utf8")

        client.send(f"{YELLOW + Colors.BOLD}Are you sure? Changing the username is currently not possible and requires a lot of time.{RESET + Colors.RESET}".encode("utf8"))
        confirmUsername = client.recv(2048).decode("utf8")
        
        if confirmUsername == "yes":
            client.send(f"{YELLOW + Colors.BOLD}Processing... {RESET + Colors.RESET}".encode("utf8"))
            
            try:
                client.send(f"{GREEN + Colors.BOLD}Creating your User account... {RESET + Colors.RESET}".encode("utf8"))
            
                logcur.execute("SELECT user_id FROM users")
            
                user_ids = logcur.fetchall()
                user_ids = str(user_ids[-1])
                user_ids = user_ids[1:-2].replace(",", "")
                user_ids = int(user_ids) + 1
                
                creation_date = time.time()
                
                logcur.execute('INSERT INTO users (username, password, role, role_color, enable_blacklisted_words, account_enabled, muted, user_id, msg_count, enable_dms, creation_date) VALUES (?, ?, "member", ?, "true", "true", "false", ?, ?, "true", ?)', (registeredUsername, registeredPassword, registeredRoleColor.lower(), user_ids, 0, creation_date))
                db.commit()
                
                client.send(f"{GREEN + Colors.BOLD}Created!{RESET + Colors.RESET}".encode("utf8"))
                client.close()
                
            except Exception as e:
                sqlError(e)
            
        else:
            client.send(f"{RED + Colors.BOLD}Registration has been canceled. Start from the beginning...{RESET + Colors.RESET}".encode("utf8"))
            time.sleep(0.5)
            register()
            
        
    client.send(f"{Colors.BOLD}Welcome to Strawberry Chat!{Colors.RESET}".encode("utf8"))
    client.send(f"{Colors.BOLD}New here? Type '{MAGENTA}Register{RESET}' to register! You want to leave? Type '{MAGENTA}Exit{RESET}' {Colors.RESET}".encode("utf8"))
    # client.send(f"".encode("utf8"))
    
    time.sleep(0.1)
    client.send(f"{GREEN + Colors.BOLD}Username: {RESET + Colors.RESET}".encode("utf8"))
    username = escape_ansi(client.recv(2048).decode("utf8"))
    username = username.strip("\n")
    
    if username.lower() == "register":
        register()
        
    elif username.lower() == "exit":
        client.close()
        sys.exit()
        
    time.sleep(0.01)
    
    client.send(f"{GREEN + Colors.BOLD}Password: {RESET + Colors.RESET}".encode("utf8"))
    password = escape_ansi(client.recv(2048).decode("utf8"))
    password = password.strip("\n")

    try: 
        logcur.execute('SELECT * FROM users WHERE username = ? AND password = ? AND account_enabled = ?', (username, password, "true"))
        
    except Exception as e:
        log.error(f"A login-error occurred")
        debugLogger(e, "002")
        
    res = logcur.fetchall()
    
    if res:
        logcur.execute('SELECT username FROM users WHERE username = ? AND password = ?', (username, password))
        result = logcur.fetchone()
        
        if result is not None:
            nickname = result[0]      
            return nickname
    

    else:   
        alreadyTaken = True
        while alreadyTaken:
            try:
                enabled = logcur.execute('SELECT account_enabled FROM users WHERE username = ? AND password = ?', (username, password))
                enabled = str(enabled.fetchone()[0])
                
            except TypeError:
                pass

            if enabled == "false":
                client.send(f"{RED + Colors.BOLD}Your account was disabled by an administrator.{RESET + Colors.RESET}".encode("utf8"))
                client.recv(2048).decode("utf8")
                client.close()
            
            client.send(f"{RED + Colors.BOLD}Wrong username or password.{RESET + Colors.RESET}".encode("utf8"))
            client.send(f"{GREEN + Colors.BOLD}Username: {RESET + Colors.RESET}".encode("utf8"))
            username = client.recv(2048).decode("utf8")
            time.sleep(0.01)
            
            if username.lower() == "register":
                register()
                
            elif username.lower() == "exit":
                client.close()
                sys.exit()
            
            client.send(f"{GREEN + Colors.BOLD}Password: {RESET + Colors.RESET}".encode("utf8"))
            password = client.recv(2048).decode("utf8")
            time.sleep(0.01)
            
            try: 
                logcur.execute('SELECT * FROM users WHERE username = ? AND password = ? AND account_enabled = ?', (username, password, "true"))
                
            except Exception as e:
                log.error(f"An error occurred.")
                debugLogger(e, "100")
                
            res = logcur.fetchall()
            
            if res:
                logcur.execute('SELECT username FROM users WHERE username = ? AND password = ?', (username, password))
                result = logcur.fetchone()
                
                if result is not None:
                    nickname = result[0]
                    alreadyTaken = False
                    return nickname
                
            else: alreadyTaken = True
            

 
def broadcast(message, sentBy=""):
    c = db.cursor()
    try:
        if sentBy == "":
            for user in users:
                user.send(message.encode("utf8"))

        else:
            for user in users:
                try: 
                    c.execute('SELECT badge FROM users WHERE username = ?', (sentBy,))
                    res = c.fetchone()
               
                    if res[0] is not None:
                        badge = " [" + res[0] + "]"
                        
                    else:
                        badge = ""
                        
                except Exception as e:
                    log.error("Something went wrong while... doing something with the badges?: " + e)
                
                
                c.execute('SELECT role FROM users WHERE username = ?', (sentBy,))
                res = c.fetchone()
                if res[0] != "bot":
                    
                    message = message.strip("\n")
                
                message = escape_ansi(message)
                message = repl_htpf(message)
                
                for u in users.values():
                    if f"@{u}" in message.split():
                        message = message.replace(f"@{u}", f"{BACKMAGENTA + Colors.BOLD}@{userNickname(u)}{BACKRESET + Colors.RESET}")
                
                if hasNickname(sentBy) == True:
                    if message != "":
                        user.send(f"{userRoleColor(sentBy)}{userNickname(sentBy)} (@{sentBy.lower()}){badge}{RESET + Colors.RESET}: {message}{RESET + Colors.RESET}".encode("utf8"))
                    else:
                        pass
                    
                else: 
                    if message != "":
                        user.send(f"{userRoleColor(sentBy)}{sentBy}{badge}{RESET + Colors.RESET}: {message}{RESET + Colors.RESET}".encode("utf8"))
                    else:
                        pass
                    
        c.close()
                
    except IOError as e:
        if e.errno == errno.EPIPE:
            log.critical(f"Broken Pipe Error. You may need to restart your server!! DO NOT EXIT THE CHAT CLIENT WITH ^C!!!")
            debugLogger(e, "122")
            exit(1)
  
    except Exception as e:
        log.error(f"A broadcasting error occurred.")
        debugLogger(e, "003")
        exit(1)



def cleanup():
    if len(addresses) != 0:
        for sock in addresses.keys():
            sock.close()
    print(f"{YELLOW + Colors.BOLD}Runtime has stopped.{RESET + Colors.RESET}")


def main():
    try:
        if test_mode:
            port = 49200
        else:
            port = config['server']['port']
            
        atexit.register(cleanup)
        
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serverSocket.bind((ipaddr, port))
        serverSocket.listen()
        
        if test_mode:
            print(f"{YELLOW + Colors.BOLD}>>> Enabled test mode{RESET + Colors.RESET}")
            print(f"{GREEN + Colors.BOLD}>>> {RESET}Server is running on {ipaddr}:{port}")
            mainThread = threading.Thread(target=connectionThread, args=(serverSocket,), daemon=True)
            mainThread.start()
            time.sleep(10)
        
        else:
            if enable_messages:
                print(f"{YELLOW + Colors.BOLD}>>> Enabled Flag {CYAN}'enable_messages'{RESET + Colors.RESET}")
            
            if debug_mode:
                print(f"{YELLOW + Colors.BOLD}>>> Enabled Flag {CYAN}'debug_mode'{RESET + Colors.RESET}")

            if online_mode == False:
                print(f"{RED + Colors.BOLD}>>> {YELLOW}WARNING:{RED} Online mode is disabled and your server might be in danger! Consider using the online mode!{RESET + Colors.RESET}")
            
            print(f"{GREEN + Colors.BOLD}>>> {RESET}Server is running on {ipaddr}:{port}")

            connThread = threading.Thread(target=connectionThread, args=(serverSocket,))
            connThread.start()
            connThread.join()

            cleanup()
            serverSocket.close()
            log.info("Server stopped")
            print("Server has shut down.")
            
    except KeyboardInterrupt: 
        exit()
    

# users = {}
addresses = {}

if __name__ == "__main__":
    main()
    # db.close()
    pass
