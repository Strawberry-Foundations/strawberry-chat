#!/usr/bin/env python3

import socket
import os
import sys
import threading

import colorama
from colorama import Fore

import datetime
import time

import platform
import json
import re

import yaml
from yaml import SafeLoader

import requests
import urllib3

from notifier import Notifier

if sys.platform == "linux":
    import readline
else:
    pass

# Colors
BLACK           = Fore.BLACK
RED             = Fore.RED
GREEN           = Fore.GREEN
YELLOW          = Fore.YELLOW
BLUE            = Fore.BLUE
MAGENTA         = Fore.MAGENTA
CYAN            = Fore.CYAN
WHITE           = Fore.WHITE
RESET           = Fore.RESET

LIGHTBLACK_EX   = Fore.LIGHTBLACK_EX
LIGHTRED_EX     = Fore.LIGHTRED_EX
LIGHTGREEN_EX   = Fore.LIGHTGREEN_EX
LIGHTYELLOW_EX  = Fore.LIGHTYELLOW_EX
LIGHTBLUE_EX    = Fore.LIGHTBLUE_EX
LIGHTMAGENTA_EX = Fore.LIGHTMAGENTA_EX
LIGHTCYAN_EX    = Fore.LIGHTCYAN_EX
LIGHTWHITE_EX   = Fore.LIGHTWHITE_EX

BOLD            = '\033[1m'
UNDERLINE       = '\033[4m'
CRESET          = '\033[0m'
GRAY            = "\033[90m"

MESSAGE_SEPARATOR = '\x1e'
# MESSAGE_SEPARATOR = ''

# Path of client.py
client_dir = os.path.dirname(os.path.realpath(__file__))

# Check if config exists & then open config if exists
if os.path.exists(client_dir + "/config.yml"):
    try:
        with open(client_dir + "/config.yml") as config:
            data = yaml.load(config, Loader=SafeLoader)
            
    except: 
        print(f"{RED}Error: Your configuration is invalid. Please check your config file.{RESET}")
        sys.exit(1)
        
else:
    print(f"{RED}Error: Your configuration is not available. Please check if there is a config.yml in the client.py folder.{RESET}")
    sys.exit(1)


# Variables
lang                    = data['language']
update_channel          = data['update_channel']
detect_same_sysmsg      = data['detect_same_system_messages']
message_format          = data['message_format']
enable_notifications    = data['enable_notifications']
enable_terminal_bell    = data['enable_terminal_bell']
experimental_debug_mode = data['experimental_debug_mode']
extreme_debug_mode      = data['extreme_debug_mode']
recv_allowed_bytes      = data['recv_allowed_bytes']

autoserver              = data['autoserver']['enabled']
autoserver_id           = data['autoserver']['server_id']

online_mode             = data['networking']['online_mode']
conf_keep_alive         = data['networking']['keep_alive']
latency_mode            = data['networking']['latency_mode']
latency_mode_time       = data['networking']['latency_mode_time']

ver                     = "2.6.1"
author                  = "Juliandev02"

config_ver              = 5
config_ver_yml          = data['config_ver']

langs                   = ["de_DE", "en_US"]
verified_list           = []

# todo: fork notifypy and make a better and newer version of it 
notification            = Notifier(default_notification_icon_legacy="./notification.ico")

api                     = "https://api.strawberryfoundations.xyz/v1/"

sys_argv            = False

# Client meta data
class ClientMeta:
    username = ""


# Open language strings
with open(client_dir + "/lang.yml", encoding="utf-8") as lang_strings:
    Str = yaml.load(lang_strings, Loader=SafeLoader)

# Check if language is available
if lang not in langs:
    print(f"{Fore.RED + BOLD}Error loading language: Selected language is not available.{Fore.RESET}")
    print(f"{Fore.YELLOW + BOLD}Falling back to en_US\n{Fore.RESET}")
    
    time.sleep(1)
    lang = "en_US"

if extreme_debug_mode:
    print(f"{Fore.YELLOW + BOLD}CLIENT DEBUG REPORT{Fore.RESET + CRESET}")
    print(f"Client Version: {ver}")
    print(f"Update Channel: {update_channel}")
    print(f"Detect same Sysmsg: {detect_same_sysmsg}")
    print(f"Message format: {message_format}")
    print(f"Enable Notifications: {enable_notifications}")
    print(f"Enable Terminal Bell: {enable_terminal_bell}")
    print(f"Experimental debug mode: {experimental_debug_mode}")
    print(f"Extreme debug mode: {extreme_debug_mode}")
    print(f"Autoserver: {autoserver}")
    print(f"Autoserver Id: {autoserver_id}")
    print(f"Keep alive: {conf_keep_alive}")
    print(f"Latency mode: {latency_mode}")
    print(f"Latency mode time: {latency_mode_time}")
    print(f"Language: {lang}")
    print(f"Online Mode: {online_mode}")
    print(f"System: {platform.platform()}")
    print(f"Python: {sys.version}")
    print("")


"""
--- Client-important functions ---
These functions are neccessary to run the client
"""
# Check verification of a server
def is_verified(address: str):
    try:
        if online_mode:
            if address in verified_list:
                return f"[{Str[lang]['Verified']}] "
            else:
                return ""
            
        else:
            return ""
        
    except Exception as e: 
        print(f"{RED}{e}{RESET}")

# Return current time
def current_time(): return datetime.datetime.now().strftime("%H:%M")

# Escape ansi from a string
def escape_ansi(string: str): return re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]').sub('', string)

# Convert raw input to json data
def conv_json_data(data): return json.loads(data)

# Delete last line to now show the written message
def delete_last_line():
    sys.stdout.write("\x1b[1A")
    sys.stdout.write("\x1b[2K")

# Fetch update data from the strawberry api server
def fetch_update_data(update_channel: str):
    response = requests.get(api + 'versions')
    data = response.json()
    update_data = data['stbchat']['client'][update_channel]
    
    return update_data

# Check for updates
def check_for_updates():
    online_ver = fetch_update_data(update_channel=update_channel)
    
    if not online_ver == f"v{ver}":
        print(f"{BOLD + GREEN}{Str[lang]['UpdateAvailable']}{RESET +RESET}")
        print(f"{BOLD + CYAN}strawberry-chat{GREEN}@{MAGENTA}{update_channel} {RESET}{online_ver}{RESET}")
        print(f"↳ {Str[lang]['UpgradingFrom']} {CYAN + BOLD}strawberry-chat{GREEN}@{MAGENTA}{update_channel} {RESET}{ver}{RESET}\n")
        
# Handle user badges
def badge_handler(badge):
    if not badge == "":
        return " [" + badge + "]"
    else:
        return ""

# Keep Alive handling
def keep_alive(sock):
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 60)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 10)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 5)
    
class MessageFormatter:
    def default(username: str = "", nickname: str = "", role_color: str = "", badge: str = "", message: str = "", message_type: str = "system_message"):
        time_fmt = f"[{current_time()}]"
        
        if message_type == "user_message":
            if nickname == username:
                fmt = f"{CRESET}{time_fmt} {role_color}{username}{badge}:{CRESET} {message}{CRESET}"
            else:
                fmt = f"{CRESET}{time_fmt} {role_color}{nickname} (@{username.lower()}){badge}:{CRESET} {message}{CRESET}"
                
        elif message_type == "system_message":
            fmt = f"{CRESET}{time_fmt} {message}{CRESET}"
            
        return fmt
    
    def gray_time(username: str = "", nickname: str = "", role_color: str = "", badge: str = "", message: str = "", message_type: str = "system_message"):
        time_fmt = f"{GRAY}{current_time()}{RESET}"
        
        if message_type == "user_message":
            if nickname == username:
                fmt = f"{CRESET}{time_fmt} {role_color}{username}{badge}:{CRESET} {message}{CRESET}"
            else:
                fmt = f"{CRESET}{time_fmt} {role_color}{nickname} (@{username.lower()}){badge}:{CRESET} {message}{CRESET}"
                
        elif message_type == "system_message":
            fmt = f"{CRESET}{time_fmt} {message}{CRESET}"
            
        return fmt


# Select server
def server_selector():
    print(f"{Fore.CYAN + BOLD + UNDERLINE}Strawberry Chat Client (v{ver}){CRESET}")
    print(f"{Fore.LIGHTGREEN_EX}{Str[lang]['Welcome']}{Fore.RESET}\n")
    
    if extreme_debug_mode: 
        print(f"{YELLOW + BOLD}{Str[lang]['ExtremeDebugModeActivated']}{CRESET}\n")
    
    print(f"{Fore.GREEN + BOLD + UNDERLINE}{Str[lang]['AvailableServers']}:{Fore.RESET + CRESET}")

    for i in range(len(data["server"])):
        print(f"{Fore.LIGHTBLUE_EX}[{i + 1}]{Fore.RESET} {BOLD}{data['server'][i]['name']}{CRESET} {Fore.LIGHTCYAN_EX}{is_verified(data['server'][i]['address'])}{Fore.RESET}{Fore.LIGHTYELLOW_EX}({data['server'][i]['type']})")

    print(f"{Fore.LIGHTBLUE_EX}[{len(data['server']) + 1}]{Fore.RESET} {BOLD}{Str[lang]['Custom']}{CRESET}\n")


    try:
        server_selection = int(input(f"{Fore.LIGHTCYAN_EX}{Str[lang]['SelChatServer']}{Fore.RESET}"))
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}{Str[lang]['Aborted']}{Fore.RESET}")
        sys.exit(1)
    
    except ValueError:
        print(f"{Fore.RED + BOLD}{Str[lang]['InvalidInput']}{Fore.RESET + CRESET}")
        sys.exit(1)

    server_count = len(data['server'])
    custom_server_sel = server_count + 1
    
    if server_selection == custom_server_sel:
        try:
            host = input(f"{Fore.LIGHTBLUE_EX + BOLD}{Str[lang]['Ipaddr']}{Fore.RESET + CRESET}")
            port = int(input(f"{Fore.LIGHTBLUE_EX + BOLD}{Str[lang]['Port']}{Fore.RESET + CRESET}"))
            enable_auto_login = False 
            
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}{Str[lang]['Aborted']}{Fore.RESET}")
            sys.exit(1)
        
        except ValueError:
            print(f"{Fore.RED + BOLD}{Str[lang]['InvalidInput']}{Fore.RESET + CRESET}")
            sys.exit(1)

    elif server_selection > custom_server_sel:
        print(f"{Fore.RED + BOLD}{Str[lang]['InvalidServerSelection']}{Fore.RESET + CRESET}")
        sys.exit(1)
        
    else:
        try: enable_auto_login = data["server"][(int(server_selection) - 1)]["autologin"]
        except KeyError: enable_auto_login = False 
            
        try:
            host = data["server"][(int(server_selection) - 1)]["address"]
            port = int(data["server"][(int(server_selection) - 1)]["port"])
            
        except KeyError:
            print(f"\n{Fore.YELLOW}{Str[lang]['Aborted']}{Fore.RESET}")
            sys.exit(1)
    
    return host, port, enable_auto_login, server_selection, custom_server_sel

# Try requesting our api server
if online_mode:
    try:
        print(f"{YELLOW}{Str[lang]['VerifyClient']}{RESET}")
        
        requests.get(api)
        delete_last_line()
        
        check_for_updates()
        
        print(f"{GREEN}{Str[lang]['VerifyClient']} ✓{RESET}")
    
    # If api is not available, print an error message
    except (socket.gaierror, urllib3.exceptions.NewConnectionError, urllib3.exceptions.MaxRetryError, requests.exceptions.ConnectionError): 
        print(f"{RED + UNDERLINE}{Str[lang]['ConnectionError']}{RESET + CRESET}")
        print(f"{YELLOW}{Str[lang]['ConnectionErrorDesc']}{RESET}")
        sys.exit(1)

# Verify your server's in your config
try:
    if online_mode == True:
        print(f"{YELLOW}{Str[lang]['VerifyServer']}{RESET}")
        
        for i in range(len(data["server"])):
            verified = requests.get(api + "server/verified?addr=" + data['server'][i]['address'])
            
            if verified.text == "True":
                verified_list.append(data['server'][i]['address'])
            else:
                pass  
            
        delete_last_line()
        
        print(f"{GREEN}{Str[lang]['VerifyServer']} ✓{RESET}")
        time.sleep(.1)
        
        delete_last_line()
        delete_last_line()
        
    else: pass
    
except Exception as e:
    print(f"{RED}{e}{RESET}")


# If --server is in the arguments, skip server selection input
if len(sys.argv) >= 2:
    if "--compatibility-mode" in sys.argv:
        sys_argv = False
        host, port, enable_autologin, server_selection, custom_server_sel = server_selector()
    
    elif sys.argv[1] == "--server":
        sys_argv = True
        server_selection = sys.argv[2]
        
        host = data["server"][(int(server_selection) - 1)]["address"]
        port = int(data["server"][(int(server_selection) - 1)]["port"])
        
        try: enable_autologin = data["server"][(int(server_selection) - 1)]["autologin"]     
        except KeyError: enable_autologin = False
        
        custom_server_sel = 0
 
    elif sys.argv[1] == "--gen-report":
        print(f"{Fore.YELLOW + BOLD}CLIENT REPORT{Fore.RESET + CRESET}")
        print(f"Client Version: {ver}")
        print(f"Update Channel: {update_channel}")
        print(f"Language: {lang}")
        print(f"Online Mode: {online_mode}")
        print(f"System: {platform.platform()}")
        print(f"Python: {sys.version}")
        sys.exit(0)

    else:
        print(f"{Fore.RED + BOLD}{Str[lang]['InvalidArgument']}{Fore.RESET + CRESET}")
        sys.exit(1)

# If autoserver is active, skip server selection input 
elif autoserver == True:
    server_id = data["autoserver"]["server_id"]
    
    server_selection = int(server_id + 1)
    custom_server_sel = 0
    
    host = data["server"][(int(server_id))]["address"]
    port = int(data["server"][(int(server_id))]["port"])
    
    try: enable_autologin = data["server"][(int(server_id))]["autologin"]
    except KeyError: enable_autologin = False

# If no arguments passed, start client without any special functions
else:
    host, port, enable_autologin, server_selection, custom_server_sel = server_selector()
    
# Sending thread
def send(sock):            
    if server_selection == custom_server_sel:
        print(f"{Fore.YELLOW + BOLD}{Str[lang]['Warning']}: {Str[lang]['AutologinNotAvailable']}{Fore.RESET + CRESET}\n")
        
    else:
        # Use autologin feature if enabled
        if enable_autologin:
            print(f"{Fore.GREEN + BOLD}{Str[lang]['AutologinActive']}{Fore.RESET + CRESET}\n")
            
            if latency_mode:
                time.sleep(latency_mode_time)
                
            server = data['server'][(int(server_selection) - 1)]
                
            sock.send(f"{server['credentials']['username']}".encode("utf8"))
            
            if latency_mode:
                time.sleep(latency_mode_time)
            else:
                time.sleep(0.2)
            
            sock.send(f"{server['credentials']['password']}".encode("utf8"))
        
        else:
            print(f"{Fore.GREEN + BOLD}{Str[lang]['AutologinNotActive']}{Fore.RESET + CRESET}\n")
    
    while thread_flag:
        try:
            message = input("")
            delete_last_line()
            sock.send(message.encode("utf8"))

        except:
            if thread_flag == False:
                break
            
            else:
                print(f"{Fore.RED + BOLD}{Str[lang]['ErrCouldNotSendMessage']}{Fore.RESET + CRESET}")
                break

# Receiving thread
def receive(sock):
    try:    compatibility_mode = data['server'][(int(server_selection) - 1)]['compatibility_mode']
    except: compatibility_mode = False
    
    if "--compatibility-mode" in sys.argv:
        compatibility_mode = True
    
    interrupt_counter = 0
    retry_limit = 4
    prev_message = None
    
    # Check if compatibility mode is not enabled
    if not compatibility_mode: 
        buffer = b''

        while thread_flag:
            # Comment this for debugging purposes
            try:
                message = sock.recv(int(recv_allowed_bytes)).decode('utf-8')
                
                try:
                    d_message = message.split(MESSAGE_SEPARATOR)
                    
                    if len(d_message) > 1:
                        if d_message[1] == "":
                            if extreme_debug_mode and experimental_debug_mode:
                                print(f"\n{GREEN + BOLD}[!] {YELLOW}Received JSON with MESSAGE_SEPARATOR character{CRESET}")
                            
                        else:
                            if extreme_debug_mode:
                                print(f"\n{RED + BOLD}[!] {YELLOW}Found malformed json{CRESET}")
                                print(f"↳ {YELLOW + BOLD}Received data: {d_message}{CRESET}")
                                print(f"↳ {YELLOW + BOLD}Index Length: {len(d_message)}{CRESET}")   
                                print(f"↳ {YELLOW + BOLD}Splitted (Index: 0): {d_message[0]}{CRESET}")   
                                print(f"↳ {YELLOW + BOLD}Splitted (Index: 1): {d_message[1]}{CRESET}\n")   
                    
                    message = d_message[0]
                    
                except Exception as e: 
                    if extreme_debug_mode:
                        print(f"{RED + BOLD}[!] {YELLOW}Splitting failed{CRESET}: {RED + BOLD}{e}{CRESET}")

                

                try:
                    message = conv_json_data(message)
                    
                except Exception as e:
                    if extreme_debug_mode:
                        print(f"{RED + BOLD}[!] {YELLOW}JSON Convert failed{CRESET}: {RED + BOLD}{e}{CRESET}")
                        
                    message = message
               
                
                # todo: stbmv2.1 (?)
                if message:
                    try:
                        try:
                            message_type = message["message_type"]
                            if extreme_debug_mode: print(f"{YELLOW + BOLD}Message Event:{CRESET + GRAY} {message_type}{CRESET}")
                            
                        except Exception as e:
                            print(f"{YELLOW + BOLD}{Str[lang]['CouldNotReadJson']}{CRESET}")
                            message_type = "unknown"
                            
                            if extreme_debug_mode:
                                print(f"↳ {RED + BOLD}{e}{CRESET}")
                                print(f"↳ {YELLOW + BOLD}Received data: {message}{CRESET}")
                                print(f"↳ {YELLOW + BOLD}Data type: {type(message)}{CRESET}")
                            
                            continue
                        
                        match message_type:
                            case "user_message":
                                username    = message["username"]
                                nickname    = message["nickname"]
                                badge       = badge_handler(message["badge"])
                                role_color  = message["role_color"]
                                message     = message["message"]["content"]
                                
                                match message_format:
                                    case "default": fmt = MessageFormatter.default(username=username, nickname=nickname, badge=badge, role_color=role_color, message=message, message_type=message_type)
                                    case "gray_time": fmt = MessageFormatter.gray_time(username=username, nickname=nickname, badge=badge, role_color=role_color, message=message, message_type=message_type)
                                
                                print(fmt)
                            
                            # todo: add user profile picture caching
                            case "stbchat_notification":
                                terminal_bell     = message["bell"]
                                
                                if terminal_bell and enable_terminal_bell:
                                    print("\a")
                                    delete_last_line()
                                
                                if enable_notifications:
                                    try:
                                        notify_title       = message["title"]
                                        notify_content     = message["content"]
                                        notify_username    = message["username"]
                                        notify_useravatar  = message["avatar_url"]
                                        
                                        notification.application_name = notify_title
                                        notification.title = notify_username
                                        notification.message = notify_content
                                        notification.icon = "./notification.png"
                                        
                                        notification.send()
                                        
                                    except: 
                                        print(f"{Fore.RED + BOLD}{Str[lang]['NotificationError']}{Fore.RESET + CRESET}")
                                    
                                else:
                                    pass
                            
                            case "stbchat_backend":
                                ClientMeta.username = message["user_meta"]["username"]
                                
                                if extreme_debug_mode:
                                    print(f"{YELLOW + BOLD}Received client meta data{CRESET}")
                                    print(f"↳ {YELLOW + BOLD}Username:{CRESET + GRAY} {ClientMeta.username}{CRESET}\n")
                                
                            case "system_message":
                                message = message["message"]["content"]
                                
                                match message_format:
                                    case "default": fmt = MessageFormatter.default(message=message, message_type=message_type)
                                    case "gray_time": fmt = MessageFormatter.gray_time(message=message, message_type=message_type)
                                    
                                print(fmt)
                                
                                if detect_same_sysmsg:
                                    _message = str(message)
                                    _message = _message[:28]
                                    
                                    if _message == prev_message:
                                        if escape_ansi(prev_message).startswith("You're currently at"):
                                            delete_last_line()
                                    
                                    prev_message = _message
                                    prev_message = prev_message[:30]
                                    
                            case _:
                                pass
                    
                    except Exception as e:
                        time.sleep(0.05)
                        message         = message["message"]["content"]
                        print(f"[{current_time()}] {message}")
                        
                        if experimental_debug_mode:
                            print(f"{Fore.RED + BOLD}{Str[lang]['ConnectionInterrupt']}{Fore.RESET + CRESET}")
                            print(e)
                            print("Occured by: message_type_checking")

                else:
                    break
                
            # Comment this for debugging purposes
            except Exception as e:
                interrupt_counter += 1 
                
                if experimental_debug_mode:
                    print(f"{Fore.RED + BOLD}{Str[lang]['ConnectionInterrupt']}{Fore.RESET + CRESET}")
                    print(e)
                    print("Occured by: message receiving")
                
                if interrupt_counter > retry_limit: 
                    print(f"{Fore.RED + BOLD}{Str[lang]['CheckCompatibilityMode']}{Fore.RESET + CRESET}")
                    retry_limit += 4
                    
                time.sleep(0.5)
                pass
            
    # Compatibility mode for connecting to old server versions (1.8.3 and below)
    else: 
        while thread_flag:
            try:
                message = sock.recv(2048).decode()
                
                if message:
                    print("[{}] {}".format(current_time(), message))
                else:
                    break
                
            except:
                print(f"{Fore.RED + BOLD}{Str[lang]['ErrNotReachable']}{Fore.RESET + CRESET}")
                break
                

def main():
    global thread_flag
    colorama.init()
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    if conf_keep_alive:
        keep_alive(client_socket)
    
    try: 
        print(f"{Fore.YELLOW + BOLD}{Str[lang]['TryConnection']}{Fore.RESET + CRESET}")
        client_socket.connect((host, port))
    
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}{Str[lang]['Aborted']}{Fore.RESET}")
        sys.exit(1)
            
    except: 
        print(f"{Fore.RED + BOLD}{Str[lang]['ErrNotReachable']}{Fore.RESET + CRESET}")
        sys.exit(1)
    
    if sys_argv == True:
        pass
    
    elif server_selection == custom_server_sel:
        print(f"{Fore.GREEN + BOLD}{Str[lang]['ConnectedToServer'] % host}{Fore.RESET + CRESET}")
        
    else:
        print(f"{Fore.GREEN + BOLD}{Str[lang]['ConnectedToServer'] % data['server'][(int(server_selection) - 1)]['name']}{Fore.RESET + CRESET}")
        
    _sending = threading.Thread(target=send, args=(client_socket,))
    _receiving = threading.Thread(target=receive, args=(client_socket,))

    _receiving.start()
    _sending.start()

    try:
        while _receiving.is_alive() and _sending.is_alive():
            continue
        
    except KeyboardInterrupt:
        print(f"\n{Str[lang]['Aborted']}")
        thread_flag = False
        sys.exit(1)
        
    thread_flag = False

    client_socket.close()
    print(f"\n{Fore.YELLOW}{Str[lang]['CloseApplication']}{Fore.RESET}")
    

thread_flag = True

if __name__ == "__main__":
    main()
    pass
