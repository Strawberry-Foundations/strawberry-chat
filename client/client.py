#!/usr/bin/env python3

import os
import socket
import sys
import colorama
from colorama import Fore
import datetime
import threading
import yaml
from yaml import SafeLoader
import time
import requests
import urllib3
import json
import re
import platform
from notifypy import Notify

if sys.platform == "linux":
    import readline
else: pass

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

# Path of client.py
client_dir = os.path.dirname(os.path.realpath(__file__))

# Check if config exists
if os.path.exists(client_dir + "/config.yml"):
    # Open Configuration
    try:
        with open(client_dir + "/config.yml") as config:
                data = yaml.load(config, Loader=SafeLoader)
    except: 
        print(f"{RED}Error: Your configuration is invalid. Please check your config file. {RESET}")
        sys.exit(1)
else:
    print(f"{RED}Error: Your configuration is not available. Please check if there is a config.yml in the client.py folder. {RESET}")
    sys.exit(1)


# Variables
lang                    = data['language']

autoserver              = data['autoserver']['enabled']
autoserver_id           = data['autoserver']['server_id']
det_same_sysmsg         = data['detect_same_system_messages']

enable_notifications    = data['enable_notifications']

online_mode             = data['networking']['online_mode']
conf_keep_alive         = data['networking']['keep_alive']
latency_mode            = data['networking']['latency_mode']
latency_mode_time       = data['networking']['latency_mode_time']

update_channel          = data['update_channel']

langs                   = ["de_DE", "en_US"]
verified_list           = []

api                     = "https://api.strawberryfoundations.xyz/v1/"
ver                     = "2.6.0"

config_ver              = 4
config_ver_yml          = data['config_ver']

author                  = "Juliandev02"
use_sys_argv            = False
experimental_debug_mode = False

notification            = Notify(default_notification_application_name="Strawberry Chat")


# Open language strings
with open(client_dir + "/lang.yml", encoding="utf-8") as langStrings:
        Str = yaml.load(langStrings, Loader=SafeLoader)


# Client-important functions

# Check verification of a server
def is_verified(addr):
    try:
        if online_mode:
            if addr in verified_list: return f"[{Str[lang]['Verified']}] "
            else: return ""            
        else:
            return ""
        
    except Exception as e: 
        print(f"{RED}{e}{RESET}")

# Return current time
def current_time(): return datetime.datetime.now().strftime("%H:%M")

# Escape ansi from a string
def escape_ansi(string): return re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]').sub('', string)

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


# Select server
def server_selector():
    print(f"{Fore.CYAN + BOLD + UNDERLINE}Strawberry Chat Client (v{ver}){CRESET}")
    print(f"{Fore.LIGHTGREEN_EX}{Str[lang]['Welcome']}{Fore.RESET}\n")
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
            enableAutologin = False 
            
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}{Str[lang]['Aborted']}{Fore.RESET}")
            sys.exit(1)
        
        except ValueError:
            print(f"{Fore.RED + BOLD}{Str[lang]['InvalidInput']}{Fore.RESET + CRESET}")
            sys.exit(1)

    elif server_selection > custom_server_sel:
        print(f"{Fore.RED + BOLD}{Str[lang]['InvalidServerSelection']}{Fore.RESET + CRESET}")
        sys.exit(1)
        
    elif server_selection == "":
        print(f"{Fore.RED + BOLD}{Str[lang]['InvalidServerSelection']}{Fore.RESET + CRESET}")
        sys.exit(1)
        
    else:
        try: enableAutologin = data["server"][(int(server_selection) - 1)]["autologin"]
        except KeyError: enableAutologin = False 
            
        try:
            host = data["server"][(int(server_selection) - 1)]["address"]
            port = data["server"][(int(server_selection) - 1)]["port"]
            port = int(port)
            
            
        except KeyError: pass
    
    return host, port, enableAutologin, server_selection, custom_server_sel

# Try requesting our api server
if online_mode:
    try:
        print(f"{YELLOW}{Str[lang]['VerifyClient']}{RESET}")
        requests.get(api)
        check_for_updates()
        delete_last_line()
        print(f"{YELLOW}{Str[lang]['VerifyClient']} {GREEN}✓{RESET}")
    
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
        print(f"{YELLOW}{Str[lang]['VerifyServer']}{RESET} {GREEN}✓{RESET}")
        time.sleep(.1)
        delete_last_line()
        delete_last_line()
        
    else: pass
    
except Exception as e: print(f"{RED}{e}{RESET}")

# Check if language is available
if lang not in langs:
    print(f"{Fore.RED + BOLD}Error loading language: Selected language is not available.{Fore.RESET}")
    print(f"{Fore.YELLOW + BOLD}Falling back to en_US\n{Fore.RESET}")
    time.sleep(1)
    lang = "en_US"
    
    

# If --server is in the arguments, skip server selection input
if len(sys.argv) >= 2:
    if "--compatibility-mode" in sys.argv:
        use_sys_argv = False
        host, port, enableAutologin, server_selection, custom_server_sel = server_selector()
    
    elif sys.argv[1] == "--server":
        use_sys_argv = True
        server_selection = sys.argv[2]
        
        host = data["server"][(int(server_selection) - 1)]["address"]
        port = int(data["server"][(int(server_selection) - 1)]["port"])
        
        try: enableAutologin = data["server"][(int(server_selection) - 1)]["autologin"]     
        except KeyError: enableAutologin = False
 
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
    
    try: enableAutologin = data["server"][(int(server_id))]["autologin"]
    except KeyError: enableAutologin = False

# If no arguments passed, start client without any special functions
else:
    host, port, enableAutologin, server_selection, custom_server_sel = server_selector()
    

def send(sock):
    if use_sys_argv == True:
        if enableAutologin == True:
            print(f"{Fore.GREEN + BOLD}{Str[lang]['AutologinActive']}{Fore.RESET + CRESET}\n")
            
            if latency_mode:
                time.sleep(latency_mode_time)
                
            sock.send(f"{data['server'][(int(server_selection) - 1)]['credentials']['username']}".encode("utf8"))
            
            if latency_mode:
                time.sleep(latency_mode_time)
            else:
                time.sleep(0.1)
            
            sock.send(f"{data['server'][(int(server_selection) - 1)]['credentials']['password']}".encode("utf8"))
        
        else:
            print(f"{Fore.GREEN + BOLD}{Str[lang]['AutologinNotActive']}{Fore.RESET + CRESET}\n")
            
    elif server_selection == custom_server_sel:
        print(f"{Fore.YELLOW + BOLD}{Str[lang]['Warning']}: {Str[lang]['AutologinNotAvailable']}{Fore.RESET + CRESET}\n")
        
    else:
        if enableAutologin == True:
            print(f"{Fore.GREEN + BOLD}{Str[lang]['AutologinActive']}{Fore.RESET + CRESET}\n")
            if latency_mode:
                time.sleep(latency_mode_time)
                
            sock.send(f"{data['server'][(int(server_selection) - 1)]['credentials']['username']}".encode("utf8"))
            
            if latency_mode:
                time.sleep(latency_mode_time)
            else:
                time.sleep(0.1)
            
            sock.send(f"{data['server'][(int(server_selection) - 1)]['credentials']['password']}".encode("utf8"))
        
        else:
            print(f"{Fore.GREEN + BOLD}{Str[lang]['AutologinNotActive']}{Fore.RESET + CRESET}\n")
    
    while threadFlag:
        try:
            message = input("")
            delete_last_line()
            sock.send(message.encode("utf8"))

        except:
            if threadFlag == False:
                pass
            else:
                print(f"{Fore.RED + BOLD}{Str[lang]['ErrCouldNotSendMessage']}{Fore.RESET + CRESET}")
                break


def receive(sock):
    try: compatibility_mode = data['server'][(int(server_selection) - 1)]['compatibility_mode']
    except: compatibility_mode = False
    
    if "--compatibility-mode" in sys.argv: compatibility_mode = True
    
    interrupt_counter = 0
    retry_limit = 4
    _prev_message = None
    experimental_debug_mode = True
    
    if compatibility_mode: 
            while threadFlag:
                try:
                    message = sock.recv(2048).decode()
                    
                    if message:
                        print("[{}] {}".format(current_time(), message))
                    else:
                        break
                    
                except:
                    print(host, port)
                    print(f"{Fore.RED + BOLD}{Str[lang]['ErrNotReachable']}{Fore.RESET + CRESET}")
                    break
                
    elif compatibility_mode == False: 
        while threadFlag:
            try:
                message = sock.recv(2048).decode('utf-8')

                try: message = conv_json_data(message)
                except: message = message
                
                time_fmt = f"{GRAY}{current_time()}{RESET}"
                
                if message:
                    try:
                        try: message_type = message["message_type"]
                        except: message_type = "unknown"
                        
                        if message_type == "user_message":
                            username    = message["username"]
                            nickname    = message["nickname"]
                            badge       = badge_handler(message["badge"])
                            role_color  = message["role_color"]
                            message     = message["message"]["content"]
                            
                            if nickname == username:
                                fmt = f"{CRESET}[{current_time()}] {role_color}{username}{badge}:{CRESET} {message}{CRESET}"
                                # fmt = f"{time_fmt} {role_color}{username}{badge}:{CRESET} {message}"
                            else:
                                fmt = f"{CRESET}[{current_time()}] {role_color}{nickname} (@{username.lower()}){badge}:{CRESET} {message}{CRESET}"
                                # fmt = f"{time_fmt} {role_color}{nickname} (@{username.lower()}){badge}:{CRESET} {message}"
                            
                            print(fmt)
                            
                        # todo: add user profile picture caching
                        elif message_type == "stbchat_notification":
                            if enable_notifications:
                                try:
                                    notify_content     = message["content"]
                                    notify_username    = message["username"]
                                    notify_useravatar  = message["avatar_url"]
                                    
                                    notification.title = notify_username
                                    notification.message = notify_content
                                    notification.icon = "D:\Strawberry Foundations\Assets\png\sf_logo_downscaled.png"
                                    
                                    notification.send()
                                except: 
                                    print(f"{Fore.RED + BOLD}{Str[lang]['NotificationError']}{Fore.RESET + CRESET}")
                                
                            else:
                                pass
                            
                        else:
                            message     = message["message"]["content"]
                            print(f"{CRESET}[{current_time()}] {message}{CRESET}")
                            
                            
                            if det_same_sysmsg:
                                _message = str(message)
                                _message = _message[:28]
                                
                                if _message == _prev_message:
                                    if escape_ansi(_prev_message).startswith("You're currently at"):
                                        delete_last_line()
                                
                                _prev_message = _message
                                _prev_message = _prev_message[:30]
                    
                    except Exception as e:
                        time.sleep(0.05)
                        message         = message["message"]["content"]
                        print(f"[{current_time()}] {message}")
                        
                        if experimental_debug_mode:
                            print(f"{Fore.RED + BOLD}{Str[lang]['ConnectionInterrupt']}{Fore.RESET + CRESET}")
                            print(e)

                else:
                    break
                
            except Exception as e:
                interrupt_counter += 1 
                
                if experimental_debug_mode:
                    print(f"{Fore.RED + BOLD}{Str[lang]['ConnectionInterrupt']}{Fore.RESET + CRESET}")
                    print(e)
                
                if interrupt_counter > retry_limit: 
                    print(f"{Fore.RED + BOLD}{Str[lang]['CheckCompatibilityMode']}{Fore.RESET + CRESET}")
                    retry_limit += 4
                    
                time.sleep(0.5)
                pass
                

def main():
    global threadFlag
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
    
    if use_sys_argv == True:
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
        threadFlag = False
        sys.exit(1)
        
    threadFlag = False

    client_socket.close()
    print(f"\n{Fore.YELLOW}{Str[lang]['CloseApplication']}{Fore.RESET}")
    

threadFlag = True

if __name__ == "__main__":
    main()
    pass
