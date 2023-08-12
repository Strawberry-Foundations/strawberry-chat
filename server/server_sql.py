#!/usr/bin/env python3

import logging
import atexit
from colorama import Fore, Style
import socket
import threading
import json
import os
import sys
import datetime
import sqlite3 as sql
import time
import errno
import random

# Init logger
class LogFormatter(logging.Formatter):
    format = "[%(asctime)s]  [%(levelname)s] %(message)s"

    FORMATS = {
        logging.DEBUG: Fore.LIGHTWHITE_EX + format + Style.RESET_ALL,
        logging.INFO: Fore.BLUE + format + Style.RESET_ALL,
        logging.WARNING: Fore.YELLOW + format + Style.RESET_ALL,
        logging.ERROR: Fore.LIGHTRED_EX + format + Style.RESET_ALL,
        logging.CRITICAL: Fore.RED + format + Style.RESET_ALL
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


log = logging.getLogger("LOG")
log.setLevel(logging.INFO)
log_fh = logging.FileHandler('log.txt')
log_fmt = logging.Formatter("%(asctime)s [%(levelname)s]  %(message)s")
log_fh.setFormatter(log_fmt)
log_ch = logging.StreamHandler()
log_ch.setFormatter(LogFormatter())
log.addHandler(log_ch)
log.addHandler(log_fh)

# Path of server.py
server_dir = os.path.dirname(os.path.realpath(__file__))

# Connect to the database
db = sql.connect(server_dir + "/users.db", check_same_thread=False)
c = db.cursor()

with open(server_dir + "/config.json", "r") as f:
    config = json.load(f)

# Configuration
ipaddr = config["adress"]
port = config["port"]
enable_messages = config["enable_messages"]
max_message_length = config["max_message_length"]
debug_mode = config["debug_mode"]

# Version-specified Variables 
short_ver = "1.7.0_b3"
ver = short_ver + "-vc_sql"
chat_name = "Strawberry Chat"
codename = "Vanilla Cake"
server_edition = "SQL Server"

# Afk list
afks = list([])

# Blacklised words set
blacklist = set()
with open(server_dir + "/blacklist.txt", "r") as f:
    for word in f:
        word = word.strip().lower()
        blacklist.add(word)

class Time:
    def currentTime():
        time = datetime.datetime.now()
        formattedTime = time.strftime("%H:%M:%S")
        return formattedTime

    def currentDate():
        date = datetime.date.today()
        formattedDate = date.strftime("%Y-%m-%d")
        return formattedDate

class Colors:
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'
    GRAY = "\033[90m"
    
if "--enable-messages" in sys.argv:
    enable_messages = True

# General Functions
def userNickname(uname):
    c = db.cursor()
    c.execute('SELECT nickname FROM users WHERE username = ?', (uname,))
    unick = c.fetchone()
    
    if unick[0] is not None: 
        unick = unick[0]
        return unick

def hasNickname(uname):
    c = db.cursor()
    c.execute('SELECT nickname FROM users WHERE username = ?', (uname,))
    unick = c.fetchone()
    
    if unick[0] is not None: 
        return True
    
    else: 
        return False

def userRoleColor(uname):
    c = db.cursor()
    c.execute('SELECT role_color FROM users WHERE username = ?', (uname,))
    color = c.fetchone()
    
    if color[0] is not None: 
        match color[0]:
            case "red": 
                return Fore.RED + Colors.BOLD
            
            case "green": 
                return Fore.GREEN + Colors.BOLD
                
            case "cyan": 
                return Fore.CYAN + Colors.BOLD
            
            case "blue": 
                return Fore.BLUE

            case "yellow": 
                return Fore.YELLOW
                
            case "magenta": 
                return Fore.MAGENTA
            
            case "lightred":
                return Fore.LIGHTRED_EX
            
            case "lightgreen":
                return Fore.LIGHTGREEN_EX
            
            case "lightcyan":
                return Fore.LIGHTCYAN_EX
            
            case "lightblue":
                return Fore.LIGHTBLUE_EX

            case "lightyellow":
                return Fore.LIGHTYELLOW_EX

            case "lightmagenta":
                return Fore.LIGHTMAGENTA_EX
            
            case "boldred":
                return Colors.BOLD + Fore.RED

            case "boldgreen":
                return Colors.BOLD + Fore.GREEN
            
            case "boldcyan":
                return Colors.BOLD + Fore.CYAN
            
            case "boldblue":
                return Colors.BOLD + Fore.BLUE
            
            case "boldyellow":
                return Colors.BOLD + Fore.YELLOW
            
            case "boldmagenta":
                return Colors.BOLD + Fore.MAGENTA
            
            case _:
                return Fore.RESET
    else: 
        return Fore.RESET

def isMuted(uname):
    c = db.cursor()
    c.execute('SELECT muted FROM users WHERE username = ?', (uname,))
    mutedStatus = c.fetchone()
    
    if mutedStatus[0] == "true":
        return True
    else: 
        return False

def isAccountEnabled(uname):
    c = db.cursor()
    c.execute('SELECT accountEnabled FROM users WHERE username = ?', (uname,))
    accountEnabledStatus = c.fetchone()
    
    if accountEnabledStatus[0] == "true":
        return True
    else: 
        return False
    
def debugLogger(errorMessage, errorCode):
    if debug_mode:
        log.error(f"ErrCode {errorCode}: {errorMessage}")
    else:
        None
        
def sqlError(errorMessage):
    log.error(f"e096: An SQL Error occured: {errorMessage}")
    

log.info(f"Server started ({ver})")

# News
news = f"""{Fore.GREEN +  Colors.UNDERLINE + Colors.BOLD}{chat_name} News - v1.7.0 Beta{Fore.RESET + Colors.RESET}{Fore.CYAN + Colors.BOLD}
        - COMMUNITY: New custom client by matteodev8: superchrgd ⚡ (Currently in development)
        - NEW: Bots are here!
               You can now create and program your own bots - so
               you can create your own commands, independent of the server! 
        - NEW: User Profiles are here! You can now link your discord, write something 
               about yourself in your description or take a look at your fantastic badges!
        - NEW: You can now create an account from the login page!
        - NEW: Fancy User Chat Badges and exclusive badges for your user profile!
        - NEW: Blacklisted Words
        - NEW: Character Limit with some special easter eggs :)
        - NEW: User Nicknames and command to change nickname
        - NEW: Member Command
        - NEW: User info command
        - NEW: New welcome message with chat color support
        - ADMIN: Broadcast Command, Mute Command, Role set/get/color Command, Bwords set/get/add/reload Command and Ban Command
        - FIX: Fixed many many bugs{Fore.RESET + Colors.RESET}"""



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
        client.send(f"{Fore.CYAN + Colors.BOLD}Welcome back {user}! Nice to see you!{Fore.RESET + Colors.RESET}".encode("utf8"))
        onlineUsersLen = len([user for user in sorted(users.values())])
        
        if onlineUsersLen == 1:
            onlineUsersStr = f"is {onlineUsersLen} user"
        else:
            onlineUsersStr = f"are {onlineUsersLen} users"
            
        time.sleep(0.05)
        client.send(f"""{Fore.CYAN + Colors.BOLD}Currently there {onlineUsersStr} online. For help use /help{Fore.RESET + Colors.RESET}\n{news}""".encode("utf8"))
        

    except Exception as e:
        log.error(f"A Communication error with {address} ({user}) occurred.")
        debugLogger(e, "003")
        
        del addresses[client]
        del users[client]
        client.close()
        return
    
    time.sleep(0.1)
    broadcast(f"{Colors.GRAY + Colors.BOLD}-->{Colors.RESET} {userRoleColor(user)}{user}{Fore.GREEN + Colors.BOLD} has joined the chat room!{Fore.RESET + Colors.RESET}")

    while True:
        try:
            message = client.recv(2048).decode("utf8")
            message_length = len(message)
        
            # Message length control system
            rnd = random.randint(0, 3)    
            if message_length > max_message_length:
                if rnd == 0:
                    client.send(f"{Fore.YELLOW + Colors.BOLD}Your message is too long.{Fore.RESET + Colors.RESET}".encode("utf8"))
                    
                elif rnd == 1:
                    client.send(f"{Fore.YELLOW + Colors.BOLD}boah digga halbe bibel wer liest sich das durch{Fore.RESET + Colors.RESET}".encode("utf8"))
                    
                elif rnd == 2:
                    client.send(f"{Fore.YELLOW + Colors.BOLD}junge niemand will sich hier die herr der ringe trilogie durchlesen{Fore.RESET + Colors.RESET}".encode("utf8"))
                    
                elif rnd == 3:
                    client.send(f"{Fore.YELLOW + Colors.BOLD}ne digga das liest sich doch keiner durch grundgesetz einfach. mach dich ab{Fore.RESET + Colors.RESET}".encode("utf8"))
                    client.close()
                continue

            # Blacklisted Word System
            c.execute('SELECT role FROM users WHERE username = ?', (user,))    
            res = c.fetchone()
            
            c.execute('SELECT enableBlacklistedWords FROM users WHERE username = ?', (user,))
            res2 = c.fetchone()
            
            if res[0] == "admin" or res2[0] == "false":
                pass
            
            else:
                for word in message.split():
                    word = word.lower()
                    
                    if word in blacklist:
                        client.send(f"{Fore.YELLOW + Colors.BOLD}Please be friendlier in the chat. Rejoin when you feel ready!{Fore.RESET + Colors.RESET}".encode("utf8"))
                        client.close()
                        
                    else:
                        pass
            
            # Define db variable global
            global db
                    
            # /broadcast Command            
            if message.startswith("/broadcast "):
                try: 
                    c.execute('SELECT role FROM users WHERE username = ?', (user,))
                    
                except Exception as e:
                    sqlError(e)
                    
                res = c.fetchone()
                
                if res[0] == "admin":
                    text = message.replace("/broadcast ", "")
                    
                    if text == "/broadcast ":
                        client.send("Wrong usage".encode("utf8"))
                        continue
                    
                    broadcast(f"{text}")
                    continue
                    
                else:
                    client.send(f"{Fore.RED}Sorry, you do not have permissons for that.{Fore.RESET}".encode("utf8"))
                    continue
            
    
            # /nick Command
            elif message.startswith("/nick ") or message.startswith("/nickname "):  
                if message.startswith("/nick "):
                    nick = message.replace("/nick ", "")
                    
                elif message.startswith("/nickname ") :
                    nick = message.replace("/nickname ", "")
                    
                if nick.lower() == "remove":
                    c.execute("UPDATE users SET nickname = NULL WHERE username = ?", (user,))
                    db.commit()
                    
                    client.send(f"{Fore.LIGHTGREEN_EX + Colors.BOLD}Removed nickname{Fore.RESET + Colors.RESET}".encode("utf8"))
                    continue
                    
                c.execute("UPDATE users SET nickname = ? WHERE username = ?", (nick, user))
                db.commit()
                
                client.send(f"{Fore.LIGHTGREEN_EX + Colors.BOLD}Changed nickname to {Fore.RESET + userRoleColor(user)}{nick}{Fore.RESET + Colors.RESET}".encode("utf8"))
                continue
            
            
            # /member Command
            elif message.startswith("/member ") or message.startswith("/user ") or message.startswith("/userinfo "):  
                if message.startswith("/member "):
                    uname = message.replace("/member ", "")
                    
                elif message.startswith("/user "):
                    uname = message.replace("/user ", "")
                    
                elif message.startswith("/userinfo "):
                    uname = message.replace("/userinfo ", "")
                    
                if uname.startswith("me"):
                    uname = user
                
                try:
                    c.execute("SELECT username, nickname, badge, role, role_color, description, badges, discord_name FROM users WHERE username = ?", (uname,))
                    
                except:
                    client.send(f"{Fore.RED + Colors.BOLD}User not found.{Fore.RESET + Colors.RESET}".encode("utf8"))
                    continue
                
                for row in c:
                    if row[1] is not None:
                        nickname = row[1]
                    else:
                        nickname = "Not set"
                    
                    if row[3] == "admin":
                        role = "Administrator"
                    else:
                        role = "Member"
                        
                    if row[2] is not None:
                        badge = row[2]
                    else:
                        badge = "Not set"
                        
                    if row[5] is not None:
                        description = row[5]
                    else:
                        description = "Not set"
                        
                    if row[7] is not None:
                        discord = Fore.MAGENTA + "@" + row[7]
                    else:
                        discord = "Not set"
                        
                    crown_badge = "- 👑 The legendary founder and owner!"
                    cool_badge = "- 😎 One of the coolest here!"
                    flame_badge = "- 🔥 The hottest user!"
                    lightning_badge = "- ⚡ Founder and owner of the Superchrgd Client!"
                    bot_badge = "- 🤖 Just some bot"
                    macher_badge = "- 💪 In germany we say: \"Macher\""
                    kindness_badge = "- 👍 The badge of kindness!"
                    troll_badge = "- 🤡 Someone wo trolls.. watch out"
                    evil_badge = "- 😈 The opposite of the kindness's badge - The evil badge"
                    supporter_badge = "- 🤝 Active supporter and helper"
                    newbie_badge = "- 👋 Say hi! I'm new!"
                    og_badge = "- 😌 A real OG, who is one of the first members!"
                    all_badges = ""

                    if row[6] is None:
                        all_badges = " Hmm... This user doesn't have any badges yet"
                        
                    else:
                        if "👑" in row[6]:
                            all_badges = all_badges + "\n        " + crown_badge  
                        if "😎" in row[6]:
                            all_badges = all_badges + "\n        " + cool_badge
                        if "🔥" in row[6]:
                            all_badges = all_badges + "\n        " + flame_badge
                        if "⚡" in row[6]:
                            all_badges = all_badges + "\n        " + lightning_badge
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
                        
                        
                    client.send(
                        f"""{Fore.CYAN + Colors.BOLD + Colors.UNDERLINE}User information about {row[0]}{Fore.RESET + Colors.RESET}
        {Fore.GREEN + Colors.BOLD}Username:{Fore.RESET + userRoleColor(row[0])} {row[0]}{Fore.RESET + Colors.RESET}
        {Fore.GREEN + Colors.BOLD}Nickname:{Fore.RESET + Colors.BOLD} {nickname}{Fore.RESET + Colors.RESET}
        {Fore.GREEN + Colors.BOLD}Description:{Fore.RESET + Colors.BOLD} {description}{Fore.RESET + Colors.RESET}
        {Fore.GREEN + Colors.BOLD}Main Badge:{Fore.RESET + Colors.BOLD} {badge}{Fore.RESET + Colors.RESET}
        {Fore.GREEN + Colors.BOLD}Badges: {row[6]}{Fore.RESET + Colors.BOLD}{Fore.RESET + Colors.RESET}{Colors.BOLD}{all_badges}{Colors.RESET}
        {Fore.GREEN + Colors.BOLD}Role:{Fore.RESET + Colors.BOLD} {role}{Fore.RESET + Colors.RESET}
        {Fore.GREEN + Colors.BOLD}Role Color:{Fore.RESET + Colors.BOLD} {userRoleColor(row[0])}{row[4]}{Fore.RESET + Colors.RESET}
        {Fore.GREEN + Colors.BOLD}Discord:{Fore.RESET + Colors.BOLD} {discord}{Fore.RESET + Colors.RESET}"""
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
                    
                    c.execute("UPDATE users SET muted = 'true' WHERE username = ?", (uname,))
                    db.commit()
                    
                    client.send(f"{Fore.LIGHTGREEN_EX + Colors.BOLD}Muted {uname}{Fore.RESET + Colors.RESET}".encode("utf8"))
                    continue
                    
                else:
                    client.send(f"{Fore.RED}Sorry, you do not have permissons for that.{Fore.RESET}".encode("utf8"))
                    
                    
            # /unmute Command
            elif message.startswith("/unmute "):
                try: 
                    c.execute('SELECT role FROM users WHERE username = ?', (user,))
                    
                except Exception as e:
                    sqlError(e)
                    
                res = c.fetchone()
                
                if res[0] == "admin":
                    uname = message.replace("/unmute ", "")
                    
                    c.execute("UPDATE users SET muted = 'false' WHERE username = ?", (uname,))
                    db.commit()
                    
                    client.send(f"{Fore.LIGHTGREEN_EX + Colors.BOLD}Unmuted {uname}{Fore.RESET + Colors.RESET}".encode("utf8"))
                    continue
                    
                else:
                    client.send(f"{Fore.RED}Sorry, you do not have permissons for that.{Fore.RESET}".encode("utf8"))
            
            
            # /discord Command
            elif message.startswith("/discord "):
                discord_name = message.replace("/discord ", "")

                if discord_name.lower() == "remove":
                    c.execute("UPDATE users SET discord_name = NULL WHERE username = ?", (user,))
                    db.commit()
                    
                    client.send(f"{Fore.LIGHTGREEN_EX + Colors.BOLD}Removed Discord Link{Fore.RESET + Colors.RESET}".encode("utf8"))
                    continue
                
                c.execute("UPDATE users SET discord_name = ? WHERE username = ?", (discord_name, user))
                db.commit()
                
                client.send(f"{Fore.LIGHTGREEN_EX + Colors.BOLD}Changed Discord Link to {Fore.MAGENTA}{discord_name}{Fore.RESET + Colors.RESET}".encode("utf8"))
                continue

            
            # /description Command
            elif message.startswith("/description "):
                desc = message.replace("/description ", "")

                if desc.lower() == "remove" or desc.lower() == "reset":
                    c.execute("UPDATE users SET description = NULL WHERE username = ?", (user,))
                    db.commit()
                    
                    client.send(f"{Fore.LIGHTGREEN_EX + Colors.BOLD}Removed Description{Fore.RESET + Colors.RESET}".encode("utf8"))
                    continue
                
                elif desc.lower() == "" or desc.lower() == " ":
                    c.execute("SELECT description FROM users WHERE username = ?", (user,))
                    desc = c.fetchone()[0]
                    
                    client.send(f"{Fore.LIGHTGREEN_EX + Colors.BOLD}Your current description: {Fore.RESET}{desc}{Colors.RESET}".encode("utf8"))
                    continue
                
                c.execute("UPDATE users SET description = ? WHERE username = ?", (desc, user))
                db.commit()
                
                client.send(f"{Fore.LIGHTGREEN_EX + Colors.BOLD}Changed Description to {Fore.CYAN}{desc}{Fore.RESET + Colors.RESET}".encode("utf8"))
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
                    
                    c.execute("UPDATE users SET accountEnabled = 'false' WHERE username = ?", (uname,))
                    db.commit()
                    
                    client.send(f"{Fore.LIGHTGREEN_EX + Colors.BOLD}Banned {uname}{Fore.RESET + Colors.RESET}".encode("utf8"))
                    continue
                    
                else:
                    client.send(f"{Fore.RED}Sorry, you do not have permissons for that.{Fore.RESET}".encode("utf8"))
            
            
            # /unban Command
            elif message.startswith("/unban "):
                try: 
                    c.execute('SELECT role FROM users WHERE username = ?', (user,))
                    
                except Exception as e:
                    sqlError(e)
                    
                res = c.fetchone()
                
                if res[0] == "admin":
                    uname = message.replace("/unban ", "")
                    
                    c.execute("UPDATE users SET accountEnabled = 'true' WHERE username = ?", (uname,))
                    db.commit()
                    
                    client.send(f"{Fore.LIGHTGREEN_EX + Colors.BOLD}Unbanned {uname}{Fore.RESET + Colors.RESET}".encode("utf8"))
                    continue
                    
                else:
                    client.send(f"{Fore.RED}Sorry, you do not have permissons for that.{Fore.RESET}".encode("utf8"))
            
            
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
                            
                            client.send(f"{Fore.LIGHTGREEN_EX + Colors.BOLD}Role of {uname} was set to {role}{Fore.RESET + Colors.RESET}".encode("utf8"))
                            continue
                        
                        except:
                            client.send(f"{Fore.RED + Colors.BOLD}Invalid username and/or role!{Fore.RESET + Colors.RESET}".encode("utf8"))
                            continue
                    
                    # /role get Command
                    elif cmd == "get":
                        try:
                            uname = args[1]
                      
                            c.execute("SELECT role FROM users WHERE username = ?", (uname,))
                            role = c.fetchone()[0]
                            
                            client.send(f"{Fore.LIGHTGREEN_EX + Colors.BOLD}Role of {uname}: {Fore.MAGENTA}{role}{Fore.RESET + Colors.RESET}".encode("utf8"))
                            continue
                        
                        except:
                            client.send(f"{Fore.RED + Colors.BOLD}Invalid username!{Fore.RESET + Colors.RESET}".encode("utf8"))
                            continue
                    
                    # /role color Command
                    elif cmd == "color":
                        try:
                            uname = args[1]
                            color = args[2]
                        
                            c.execute("UPDATE users SET role_color = ? WHERE username = ?", (color, uname))
                            db.commit()
                            
                            client.send(f"{Fore.LIGHTGREEN_EX + Colors.BOLD}Role Color of {uname} was set to {color}{Fore.RESET + Colors.RESET}".encode("utf8"))
                            continue
                    
                        except:
                            client.send(f"{Fore.RED + Colors.BOLD}Invalid username and/or color!{Fore.RESET + Colors.RESET}".encode("utf8"))
                            continue
                        
                    else:
                        client.send(f"{Fore.RED + Colors.BOLD}Invalid command usage.{Fore.RESET + Colors.RESET}".encode("utf8"))
                        continue
                    
                else:
                    client.send(f"{Fore.RED}Sorry, you do not have permissons for that.{Fore.RESET}".encode("utf8"))
            
            
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
                         
                            c.execute("UPDATE users SET enableBlacklistedWords = ? WHERE username = ?", (value, uname))
                            db.commit()
                        
                            if value == "true":
                                client.send(f"{Fore.LIGHTGREEN_EX + Colors.BOLD}Enabled Blacklisted Words for {uname}{Fore.RESET + Colors.RESET}".encode("utf8"))
                                continue
                            
                            elif value == "false":
                                client.send(f"{Fore.LIGHTGREEN_EX + Colors.BOLD}Disabled Blacklisted Words for {uname}{Fore.RESET + Colors.RESET}".encode("utf8"))
                                continue
                            
                            else:
                                client.send(f"{Fore.RED + Colors.BOLD}Invalid value!{Fore.RESET + Colors.RESET}".encode("utf8"))
                                continue
                    
                        except:
                            client.send(f"{Fore.RED + Colors.BOLD}Invalid username and/or value!{Fore.RESET + Colors.RESET}".encode("utf8"))
                            continue
                        
                    # /bwords get
                    elif cmd == "get":
                        try:
                            uname = args[1]
                                
                            c.execute("SELECT enableBlacklistedWords FROM users WHERE username = ?", (uname,))
                            value = c.fetchone()[0]
                            
                            if value == "true":
                                client.send(f"{Fore.LIGHTGREEN_EX + Colors.BOLD}Blacklisted Words for {uname} are enabled{Fore.RESET + Colors.RESET}".encode("utf8"))
                                continue
                            
                            elif value == "false":
                                client.send(f"{Fore.LIGHTGREEN_EX + Colors.BOLD}Blacklisted Words for {uname} are disabled{Fore.RESET + Colors.RESET}".encode("utf8"))
                                continue
                            
                            else:
                                client.send(f"{Fore.RED + Colors.BOLD}Whoa! This should not happen...{Fore.RESET + Colors.RESET}".encode("utf8"))
                                continue
                        except:
                            client.send(f"{Fore.RED + Colors.BOLD}Invalid username{Fore.RESET + Colors.RESET}".encode("utf8"))
                            continue
                           
                    # /bwords add 
                    elif cmd == "add":
                        try:
                            word = args[1]
                        except:
                            client.send(f"{Fore.RED + Colors.BOLD}Cant add an empty word!{Fore.RESET + Colors.RESET}".encode("utf8"))
                            continue
                        
                        if word == "":
                            client.send(f"{Fore.RED + Colors.BOLD}Cant add an empty word!{Fore.RESET + Colors.RESET}".encode("utf8"))
                            continue
                        
                        with open("blacklist.txt", "a") as f:
                            f.write("\n" + word)
                            f.close()
                        
                        client.send(f"{Fore.LIGHTGREEN_EX + Colors.BOLD}Added '{word}' to the blacklist{Fore.RESET + Colors.RESET}".encode("utf8"))
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
                            
                        else:
                            client.send(f"{Fore.RED}Sorry, you do not have permissons for that.{Fore.RESET}".encode("utf8"))
                            
                            
                    
                    else:
                        client.send(f"{Fore.RED + Colors.BOLD}Invalid command usage.{Fore.RESET + Colors.RESET}".encode("utf8"))
                        continue
                        
                    
                else:
                    client.send(f"{Fore.RED}Sorry, you do not have permissons for that.{Fore.RESET}".encode("utf8"))
                                
            
            # Match-Case-Pattern Commands
            match message:
                # Quit / Exit Command
                case "/quit" | "/exit":
                    client.send(f"{Fore.YELLOW + Colors.BOLD}You left the chat!{Fore.RESET + Colors.RESET}".encode("utf8"))
                    del addresses[client]
                    del users[client]
                    client.close()
                    
                    log.info(f"[<] {address} ({user}) has left.")
                    broadcast(f"{Fore.YELLOW + Colors.BOLD}<- {userRoleColor(user)}{user}{Fore.YELLOW + Colors.BOLD} has left the chat.{Fore.RESET + Colors.RESET}")
                    break


                # Help Command
                case "/help":
                    broadcast(f"\033[90m--> {Colors.RESET + Colors.BOLD}{userRoleColor(user)}{user}{Fore.RESET} uses /help{Fore.RESET + Colors.RESET}")
                    client.send(
                        f"""{Fore.GREEN +  Colors.UNDERLINE + Colors.BOLD}Default commands{Fore.RESET + Colors.RESET}
        {Fore.BLUE + Colors.BOLD}/help: {Fore.RESET}Help Command
        {Fore.BLUE + Colors.BOLD}/about: {Fore.RESET}About {chat_name}
        {Fore.BLUE + Colors.BOLD}/news: {Fore.RESET}Newsletter{Fore.RESET + Colors.RESET}
        {Fore.BLUE + Colors.BOLD}/exit, /quit: {Fore.RESET}Leave chat
        {Fore.BLUE + Colors.BOLD}/clientinfo: {Fore.RESET}Get some information about you{Fore.RESET + Colors.RESET}
        {Fore.BLUE + Colors.BOLD}/shrug: {Fore.RESET}¯\_(ツ)_/¯
        {Fore.BLUE + Colors.BOLD}/tableflip: {Fore.RESET}(╯°□°)╯︵ ┻━┻
        {Fore.BLUE + Colors.BOLD}/unflip: {Fore.RESET}┬─┬ノ( º _ ºノ){Fore.RESET + Colors.RESET}
        """.encode("utf-8"))
                    
                    time.sleep(0.1)
                    client.send(
                        f"""{Fore.CYAN + Colors.UNDERLINE + Colors.BOLD}Profile & User Commands{Fore.RESET + Colors.RESET}
        {Fore.BLUE + Colors.BOLD}/online: {Fore.RESET}Shows online users
        {Fore.BLUE + Colors.BOLD}/members, /users: {Fore.RESET}Shows registered users
        {Fore.BLUE + Colors.BOLD}/userinfo, /user, /member <user>/me: {Fore.RESET}Shows information about the specified user
        {Fore.BLUE + Colors.BOLD}/nick <nickname/remove>: {Fore.RESET}Changes nickname to <nickname> or removes it
        {Fore.BLUE + Colors.BOLD}/description <desc>: {Fore.RESET}Set your user description{Fore.RESET + Colors.RESET}
        {Fore.BLUE + Colors.BOLD}/discord <discord_uname>: {Fore.RESET}Set your discord username{Fore.RESET + Colors.RESET}
        {Fore.BLUE + Colors.BOLD}/afk: {Fore.RESET}Toggle afk status
        {Fore.BLUE + Colors.BOLD}/unafk: {Fore.RESET}Untoggle afk status
        {Fore.BLUE + Colors.BOLD}/afks, /afklist: {Fore.RESET}Shows afk users
        """.encode("utf-8"))
                    
                    time.sleep(0.1)
                    client.send(
                        f"""{Fore.MAGENTA +  Colors.UNDERLINE + Colors.BOLD}Admin commands{Fore.RESET + Colors.RESET}
        {Fore.BLUE + Colors.BOLD}/ban <user>: {Fore.RESET}Bans the specificed user{Fore.RESET + Colors.RESET}
        {Fore.BLUE + Colors.BOLD}/unban <user>: {Fore.RESET}Unbans the specificed user{Fore.RESET + Colors.RESET}        
        {Fore.BLUE + Colors.BOLD}/mute <user>: {Fore.RESET}Mutes the specificed user{Fore.RESET + Colors.RESET}
        {Fore.BLUE + Colors.BOLD}/unmute <user>: {Fore.RESET}Unmutes the specificed user{Fore.RESET + Colors.RESET}
        {Fore.BLUE + Colors.BOLD}/broadcast <message>: {Fore.RESET}Broadcast a message{Fore.RESET + Colors.RESET}
        {Fore.BLUE + Colors.BOLD}/role get/set <user> (<role>) [<color>]: {Fore.RESET}Gets or sets the role of a user{Fore.RESET + Colors.RESET}
        {Fore.BLUE + Colors.BOLD}/role color <user> <color>: {Fore.RESET}Gets or sets the role of a user{Fore.RESET + Colors.RESET}
        {Fore.BLUE + Colors.BOLD}/bwords set/get <user> (<true/false>): {Fore.RESET}Enable or disable whether a user should be affected by the bad words{Fore.RESET + Colors.RESET}
        {Fore.BLUE + Colors.BOLD}/bwords reload: {Fore.RESET}Reloads all blacklisted words{Fore.RESET + Colors.RESET}
        {Fore.BLUE + Colors.BOLD}/bwords add <word>: {Fore.RESET}Adds a blacklisted word{Fore.RESET + Colors.RESET}
        {Fore.BLUE + Colors.BOLD}/debug: {Fore.RESET}View debug informations{Fore.RESET + Colors.RESET}
        {Fore.BLUE + Colors.BOLD}/kickall: {Fore.RESET}Kick all users (Currently not working){Fore.RESET + Colors.RESET}
        """.encode("utf8"))
                    
                    
                # Online Command
                case "/online":
                    onlineUsers = ', '.join([user for user in sorted(users.values())])
                    onlineUsersLen2 = len([user for user in sorted(users.values())])
                    client.send(f"""{Fore.GREEN +  Colors.UNDERLINE + Colors.BOLD}Users who are currently online ({onlineUsersLen2}){Fore.RESET + Colors.RESET}
        {Colors.BOLD}->{Colors.RESET} {Fore.CYAN}{onlineUsers}{Fore.RESET + Colors.RESET}""".encode("utf8"))
                
                
                # Afk Command
                case "/afk":
                    if user in afks:
                        client.send(f"{Fore.YELLOW + Colors.BOLD}You are already AFK!{Fore.RESET + Colors.RESET}".encode("utf8"))
                        
                    else:
                        broadcast(f"{user} is now AFK 🌙..")
                        afks.append(user)
                
                
                # Unafk Comamnd
                case "/unafk":
                    if user not in afks:
                        client.send(f"{Fore.YELLOW + Colors.BOLD}You are not AFK!{Fore.RESET + Colors.RESET}".encode("utf8"))
                    
                    else:
                        broadcast(f"{user} is no longer AFK 🌻!")
                        afks.remove(user)
                    
                    
                # Whois Afk Command
                case "/afks" | "/afklist":
                    afkUsers = ', '.join([afks for afks in sorted(afks)])
                    afkUsersLen = len([afks for afks in sorted(afks)])
                    client.send(f"""{Fore.GREEN +  Colors.UNDERLINE + Colors.BOLD}Users who are currently Afk ({afkUsersLen}){Fore.RESET + Colors.RESET}
        {Colors.BOLD}->{Colors.RESET} {Fore.CYAN}{afkUsers}{Fore.RESET}""".encode("utf8"))
                
                
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
                        client.send(f"{Fore.RED}Sorry, you do not have permissons for that.{Fore.RESET}".encode("utf8"))
                                
                                                
                # Kickall Command
                case "/kickall":
                    try: 
                        c.execute('SELECT role FROM users WHERE username = ?', (user,))
                        
                    except Exception as e:
                        sqlError(e)
                        
                    res = c.fetchone()
                    
                    if res[0] == "admin":
                        cleanup()
                        
                    else:
                        client.send(f"{Fore.RED}Sorry, you do not have permissons for that.{Fore.RESET}".encode("utf8"))
                
                
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
                        f"""{Fore.GREEN +  Colors.UNDERLINE + Colors.BOLD}About {chat_name}{Fore.RESET + Colors.RESET}
        {Fore.BLUE + Colors.BOLD}Thank you for using {chat_name}!{Fore.RESET}
        {Fore.BLUE + Colors.BOLD}Version: {Fore.RESET}{short_ver} {codename} ({server_edition})
        {Fore.BLUE + Colors.BOLD}Author: {Fore.RESET}Juliandev02{Fore.RESET + Colors.RESET}"""
        .encode("utf8"))
                    
                    
                # News Command
                case "/news":
                    client.send(news.encode("utf8"))
                
                
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

                    client.send(f"""{Fore.CYAN +  Colors.UNDERLINE + Colors.BOLD}Members on this server ({membersLen}){Fore.RESET + Colors.RESET}
        {Colors.BOLD}->{Colors.RESET} {Fore.CYAN}{members}{Fore.RESET}""".encode("utf8"))
                
                
                # Show Description Command
                case "/description" | "/desc":
                    c.execute("SELECT description FROM users WHERE username = ?", (user,))
                    desc = c.fetchone()[0]
                    client.send(f"{Fore.LIGHTGREEN_EX + Colors.BOLD}Your current description: {Fore.RESET}{desc}{Colors.RESET}".encode("utf8"))
                
                
                # Delete Account Command
                case "/deleteaccount":
                    client.send(f"{Fore.YELLOW + Colors.BOLD}Are you sure you want to delete your user account? This action is irreversible!!{Fore.RESET + Colors.RESET}".encode("utf8"))
                    confirmDelete1 = client.recv(2048).decode("utf8")
                    
                    if confirmDelete1.lower() == "yes":
                        client.send(f"{Fore.YELLOW + Colors.BOLD}THIS IS YOUR VERY LAST WARNING! This action is irreversible!! ARE YOU SURE?{Fore.RESET + Colors.RESET}".encode("utf8"))
                        confirmDelete2 = client.recv(2048).decode("utf8")
                        
                        if confirmDelete2.lower() == "yes":
                            client.send(f"{Fore.YELLOW + Colors.BOLD}Enter your username to confirm the deletion of your account:{Fore.RESET + Colors.RESET}".encode("utf8"))
                            confirmUsernameDelete = client.recv(2048).decode("utf8")
                            
                            if confirmUsernameDelete.lower() == user:
                                client.send(f"{Fore.YELLOW + Colors.BOLD}Deleting your user account...{Fore.RESET + Colors.RESET}".encode("utf8"))
                                
                                try:
                                    cursor = db.cursor()
                                    cursor.execute("DELETE FROM users WHERE username = ?", (user,))
                                    db.commit()
                                    client.send(f"{Fore.YELLOW + Colors.BOLD}Deleted{Fore.RESET + Colors.RESET}".encode("utf8"))
                                    client.close()
                                    sys.exit(1)
                                    
                                except Exception as e:
                                    log.error(e)
                                    
                            else: 
                                client.send(f"{Fore.YELLOW + Colors.BOLD}Deletion of your account has been canceled...{Fore.RESET + Colors.RESET}".encode("utf8"))
                        else:
                            client.send(f"{Fore.YELLOW + Colors.BOLD}Deletion of your account has been canceled...{Fore.RESET + Colors.RESET}".encode("utf8"))
                    else:
                        client.send(f"{Fore.YELLOW + Colors.BOLD}Deletion of your account has been canceled...{Fore.RESET + Colors.RESET}".encode("utf8"))

            
                case "/":
                    client.send(f"{Fore.GREEN + Colors.BOLD}Need help? Take a look at our help command! /help{Fore.RESET + Colors.RESET}".encode("utf8"))
                
                
                case _:
                    
                    if user in afks:
                        client.send(f"{Fore.RED}Sorry, you are AFK.{Fore.RESET}".encode("utf8"))
                        
                    elif isMuted(user) == True:
                        client.send(f"{Fore.RED + Colors.BOLD}Sorry, but you were muted by an administrator. Please contact him/her if you have done nothing wrong, or wait until you are unmuted.{Fore.RESET + Colors.RESET}".encode("utf8"))
                    
                    elif isAccountEnabled(user) == False:
                        client.send(f"{Fore.RED + Colors.BOLD}Your account was disabled by an administrator.{Fore.RESET + Colors.RESET}".encode("utf8"))
                        
                    else:
                        if enable_messages == True:
                            log.info(f"[{Time.currentDate()} {Time.currentTime()}] {address} ({user}): {message}")
                                
                        broadcast(message, user)
                
            
                
        except Exception as e:
            log.error("A client-side error occurred.")
            
            debugLogger(e, "004")
            log.info(f"[<] {user} ({address}) has left")
            
            del addresses[client]
            del users[client]
            client.close()
            
            broadcast(f"{Fore.YELLOW + Colors.BOLD}<- {userRoleColor(user)}{user}{Fore.YELLOW + Colors.BOLD} has left the chat.{Fore.RESET + Colors.RESET}")
            break


def clientLogin(client):
    def register():
        global db
        global c
        
        client.send(f"{Fore.MAGENTA + Colors.BOLD + Colors.UNDERLINE}Welcome!{Fore.RESET + Colors.RESET}\n        {Colors.BOLD}Register, to chat with us!{Colors.RESET}".encode("utf8"))
    
        time.sleep(0.05)
        client.send(f"{Fore.GREEN + Colors.BOLD}Username: {Fore.RESET + Colors.RESET}".encode("utf8"))
        registeredUsername = client.recv(2048).decode("utf8")
        
        if registeredUsername.lower() == "exit":
            client.close()
            sys.exit()
        
        for uname in registeredUsername.split():
            uname = uname.lower()
            
            if uname in blacklist:
                client.send(f"{Fore.YELLOW + Colors.BOLD}This username is not allowed{Fore.RESET + Colors.RESET}".encode("utf8"))    
                client.close()
                sys.exit()
        try:
            c.execute("SELECT username FROM users WHERE username = ? ", (registeredUsername,))
            
            usedUsernames = c.fetchall()[0]
            usedUsernames = "".join(usedUsernames)
            
            
            if usedUsernames == usedUsernames:
                client.send(f"{Fore.YELLOW + Colors.BOLD}This username is already in use!{Fore.RESET + Colors.RESET}".encode("utf8"))    
                register()
            
        except:
            pass
            

            
        client.send(f"{Fore.GREEN + Colors.BOLD}Password: {Fore.RESET + Colors.RESET}".encode("utf8"))
        registeredPassword = client.recv(2048).decode("utf8")
        
        client.send(f"{Fore.GREEN + Colors.BOLD}Confirm Password: {Fore.RESET + Colors.RESET}".encode("utf8"))
        confirmPassword = client.recv(2048).decode("utf8")
        
        if registeredPassword != confirmPassword:
            client.send(f"{Fore.RED + Colors.BOLD}Passwords do not match{Fore.RESET + Colors.RESET}".encode("utf8"))
            register()
        
        client.send(f"{Fore.GREEN + Colors.BOLD}Role Color (Red, Green, Cyan, Blue, Yellow, Magenta): {Fore.RESET + Colors.RESET}".encode("utf8"))
        registeredRoleColor = client.recv(2048).decode("utf8")

        client.send(f"{Fore.YELLOW + Colors.BOLD}Are you sure? Changing the username is currently not possible and requires a lot of time.{Fore.RESET + Colors.RESET}".encode("utf8"))
        confirmUsername = client.recv(2048).decode("utf8")
        
        if confirmUsername == "yes":
            client.send(f"{Fore.YELLOW + Colors.BOLD}Processing... {Fore.RESET + Colors.RESET}".encode("utf8"))
            
            try:
                db = sql.connect(server_dir + "/users.db", check_same_thread=False)
                c = db.cursor()
                
                client.send(f"{Fore.GREEN + Colors.BOLD}Creating your User account... {Fore.RESET + Colors.RESET}".encode("utf8"))
                
                c.execute('INSERT INTO users (username, password, badge, role, role_color, enableBlacklistedWords, accountEnabled, muted) VALUES (?, ?, "None", "member", ?, "true", "true", "false")', (registeredUsername, registeredPassword, registeredRoleColor.lower()))
                db.commit()
                db.close()
                
                client.send(f"{Fore.GREEN + Colors.BOLD}Created!{Fore.RESET + Colors.RESET}".encode("utf8"))
                client.close()
                sys.exit(1)
                
            except Exception as e:
                sqlError(e)
            
        else:
            client.send(f"{Fore.RED + Colors.BOLD}Registration has been canceled. Start from the beginning...{Fore.RESET + Colors.RESET}".encode("utf8"))
            time.sleep(0.5)
            register()
            
        
    client.send(f"{Colors.BOLD}Welcome to Strawberry Chat!{Colors.RESET}".encode("utf8"))
    client.send(f"{Colors.BOLD}New here? Type '{Fore.MAGENTA}Register{Fore.RESET}' to register! You want to leave? Type '{Fore.MAGENTA}Exit{Fore.RESET}' {Colors.RESET}".encode("utf8"))
    client.send(f"".encode("utf8"))
    
    time.sleep(0.1)
    client.send(f"{Fore.GREEN + Colors.BOLD}Username: {Fore.RESET + Colors.RESET}".encode("utf8"))
    username = client.recv(2048).decode("utf8")
    
    if username.lower() == "register":
        register()
        
    elif username.lower() == "exit":
        client.close()
        sys.exit()
        
    time.sleep(0.01)
    
    client.send(f"{Fore.GREEN + Colors.BOLD}Password: {Fore.RESET + Colors.RESET}".encode("utf8"))
    password = client.recv(2048).decode("utf8")

    try: 
        c.execute('SELECT * FROM users WHERE username = ? AND password = ? AND accountEnabled = ?', (username, password, "true"))
        
    except Exception as e:
        log.error(f"A login-error occurred")
        debugLogger(e, "002")
        
    res = c.fetchall()
    
    if res:
        c.execute('SELECT username FROM users WHERE username = ? AND password = ?', (username, password))
        result = c.fetchone()
        
        if result is not None:
            nickname = result[0]      
            return nickname
    

    else:   
        alreadyTaken = True
        while alreadyTaken:
            try:
                enabled = c.execute('SELECT accountEnabled FROM users WHERE username = ? AND password = ?', (username, password))
                enabled = str(enabled.fetchone()[0])
                
            except TypeError:
                pass

            if enabled == "false":
                client.send(f"{Fore.RED + Colors.BOLD}Your account was disabled by an administrator.{Fore.RESET + Colors.RESET}".encode("utf8"))
                client.recv(2048).decode("utf8")
                client.close()
            
            client.send(f"{Fore.RED + Colors.BOLD}Wrong username or password.{Fore.RESET + Colors.RESET}".encode("utf8"))
            client.send(f"{Fore.GREEN + Colors.BOLD}Username: {Fore.RESET + Colors.RESET}".encode("utf8"))
            username = client.recv(2048).decode("utf8")
            time.sleep(0.01)
            
            if username.lower() == "register":
                register()
                
            elif username.lower() == "exit":
                client.close()
                sys.exit()
            
            client.send(f"{Fore.GREEN + Colors.BOLD}Password: {Fore.RESET + Colors.RESET}".encode("utf8"))
            password = client.recv(2048).decode("utf8")
            time.sleep(0.01)
            
            try: 
                c.execute('SELECT * FROM users WHERE username = ? AND password = ? AND accountEnabled = ?', (username, password, "true"))
                
            except Exception as e:
                log.error(f"An error occurred.")
                debugLogger(e, "100")
                
            res = c.fetchall()
            
            if res:
                c.execute('SELECT username FROM users WHERE username = ? AND password = ?', (username, password))
                result = c.fetchone()
                
                if result is not None:
                    nickname = result[0]
                    alreadyTaken = False
                    return nickname
                
            else: alreadyTaken = True


 
def broadcast(message, sentBy=""):
    def userRoleColor(uname):
        db = sql.connect('./users.db', check_same_thread=False)
        c = db.cursor()
        c.execute('SELECT role_color FROM users WHERE username = ?', (uname,))
        color = c.fetchone()
        db.close()
        
        if color[0] is not None: 
            match color[0]:
                case "red": 
                    return Fore.RED
                
                case "green": 
                    return Fore.GREEN
                    
                case "cyan": 
                    return Fore.CYAN
                
                case "blue": 
                    return Fore.BLUE

                case "yellow": 
                    return Fore.YELLOW
                 
                case "magenta": 
                    return Fore.MAGENTA
                
                case "lightred":
                    return Fore.LIGHTRED_EX
                
                case "lightgreen":
                    return Fore.LIGHTGREEN_EX
                
                case "lightcyan":
                    return Fore.LIGHTCYAN_EX
                
                case "lightblue":
                    return Fore.LIGHTBLUE_EX

                case "lightyellow":
                    return Fore.LIGHTYELLOW_EX

                case "lightmagenta":
                    return Fore.LIGHTMAGENTA_EX
                
                case "boldred":
                    return Colors.BOLD + Fore.RED

                case "boldgreen":
                    return Colors.BOLD + Fore.GREEN
                
                case "boldcyan":
                    return Colors.BOLD + Fore.CYAN
                
                case "boldblue":
                    return Colors.BOLD + Fore.BLUE
                
                case "boldyellow":
                    return Colors.BOLD + Fore.YELLOW
                
                case "boldmagenta":
                    return Colors.BOLD + Fore.MAGENTA
                
                case _:
                    return Fore.RESET
        else: 
            return Fore.RESET
        
                
        
    try:
        if sentBy == "":
            for user in users:
                user.send(message.encode("utf8"))

        else:
            for user in users:
                try: 
                    c.execute('SELECT badge FROM users WHERE username = ?', (sentBy,))
                    res = c.fetchone()
               
                    if res[0] != "None":
                        badge = " [" + res[0] + "]"
                    else:
                        badge = ""
                        
                except Exception as e:
                    log.error("Something went wrong while... doing something with the badges?: " + e)
                
                if hasNickname(sentBy) == True:
                    user.send(f"{userRoleColor(sentBy)}{userNickname(sentBy)} (@{sentBy.lower()}){badge}{Fore.RESET + Colors.RESET}: {message}".encode("utf8"))
                    
                else: 
                    user.send(f"{userRoleColor(sentBy)}{sentBy}{badge}{Fore.RESET + Colors.RESET}: {message}".encode("utf8"))
                
    except IOError as e:
        if e.errno == errno.EPIPE:
            log.critical(f"Broken Pipe Error. You may need to restart your server!! DO NOT EXIT THE CHAT CLIENT WITH ^C!!!")
            exit(1)
  
    except Exception as e:
        log.error(f"A broadcasting error occurred. Maybe this can help you: {e}")
        exit(1)



def cleanup():
    if len(addresses) != 0:
        for sock in addresses.keys():
            sock.close()
    log.info(f"Runtime has stopped.")


def main():
    try:
        atexit.register(cleanup)

        socketFamily = socket.AF_INET
        socketType = socket.SOCK_STREAM
        serverSocket = socket.socket(socketFamily, socketType)
        serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serverSocket.bind((ipaddr, port))
        serverSocket.listen()
        print(f"{Fore.GREEN + Colors.BOLD}* -- Server started -- *{Fore.RESET + Colors.RESET}")
        print(f"{Fore.CYAN + Colors.BOLD}{chat_name} v{short_ver} {codename} ({server_edition}){Fore.RESET + Colors.RESET}")
        
        if enable_messages == True:
            log.info(f"Enabled Flag {Fore.CYAN}'enable-messages'{Fore.RESET}")
        
        if debug_mode:
            log.info("Enabled debug mode for debugging")
            
        print(f"{Fore.YELLOW + Colors.BOLD}>>> {Fore.RESET}Server is running on {ipaddr}:{port}")

        connThread = threading.Thread(target=connectionThread, args=(serverSocket,))
        connThread.start()
        connThread.join()

        cleanup()
        serverSocket.close()
        log.info("Server stopped")
        print("Server has shut down.")
        
    except KeyboardInterrupt: 
        exit()
    

users = {}
addresses = {}

if __name__ == "__main__":
    main()
    db.close()
    pass
