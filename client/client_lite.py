#!/usr/bin/env python3

import socket
import sys
import colorama
from colorama import Fore
import datetime
import threading
import json
import time


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

ver             = "1.1.0"
author          = "Juliandev02"
use_sys_argv      = False
experimental_debug_mode = False

# Return current time
def current_time():
    return datetime.datetime.now().strftime("%H:%M")

# Delete last line to now show the written message
def delete_last_line():
    sys.stdout.write("\x1b[1A")
    sys.stdout.write("\x1b[2K")

# Convert raw input to json data
def conv_json_data(data):
    return json.loads(data)

# Handle user badges
def badge_handler(badge):
    if not badge == "":
        return " [" + badge + "]"
    else:
        return ""

# If --server is in the arguments, skip server selection input
if len(sys.argv) >= 2:
    if sys.argv[1] == "--address":
        use_sys_argv = True
        args = sys.argv[2]
        
        host = args.split(":")[0]
        port = args.split(":")[1]
        port = int(port)

    else:
        print(f"{Fore.CYAN + BOLD + UNDERLINE}Strawberry Chat Client Lite - Help Menu{CRESET}")
        print(f"{BLUE + BOLD}--address <host>:<port>: {RESET}Connect to server <host>:<port>")
        sys.exit(1)

# If no arguments passed, start client without any special functions
else:
    print(f"{Fore.CYAN + BOLD + UNDERLINE}Strawberry Chat Client Lite (stbchat_lite) (v{ver}){CRESET}")
    print(f"{Fore.LIGHTGREEN_EX}Welcome back!{Fore.RESET}\n")

    try:
        host = input(f"{Fore.LIGHTBLUE_EX + BOLD}IP-Address: {Fore.RESET + CRESET}")
        port = input(f"{Fore.LIGHTBLUE_EX + BOLD}Port: {Fore.RESET + CRESET}")
        port = int(port)
        
    except: 
        print(f"\n{YELLOW}The Strawberry chat client has been closed.{RESET}")
        sys.exit(1)


def send(sock):
    while threadFlag:
        try:
            message = input("")
            delete_last_line()
            sock.send(message.encode("utf8"))

        except:
            if threadFlag == False:
                pass
            else:
                print(f"{Fore.RED + BOLD}Could not send the message!{Fore.RESET + CRESET}")
                break

def receive(sock):
    while threadFlag:
        try:
            message = sock.recv(2048).decode('utf-8')

            try: message = conv_json_data(message)
            except: message = message
            
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
                            fmt = f"[{current_time()}] {role_color}{username}{badge}:{CRESET} {message}"
                        else:
                            fmt = f"[{current_time()}] {role_color}{nickname} (@{username.lower()}){badge}:{CRESET} {message}"
                            
                        print(fmt)
                        
                    else:
                        message     = message["message"]["content"]
                        print(f"[{current_time()}] {message}")
                
                except Exception as e:
                    time.sleep(0.05)
                    message         = message["message"]["content"]
                    print(f"[{current_time()}] {message}")
                        
            else:
                break
            
        except Exception as e: 
            if experimental_debug_mode: print(f"{Fore.RED + BOLD}Error while receiving server data: Has the connection been interrupted?{Fore.RESET + CRESET}")
            pass

def main():
    global threadFlag
    colorama.init()
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try: 
        print(f"{Fore.YELLOW + BOLD}An attempt is made to establish a connection with the server...{Fore.RESET + CRESET}")
        client_socket.connect((host, port))
        
    except: 
        print(f"{Fore.RED + BOLD}The server is not available! Try again later or contact the server owner.{Fore.RESET + CRESET}")
        sys.exit(1)
    
    if use_sys_argv == True:
        pass
        
    _sending = threading.Thread(target=send, args=(client_socket,))
    _receiving = threading.Thread(target=receive, args=(client_socket,))

    _receiving.start()
    _sending.start()

    try:
        while _receiving.is_alive() and _sending.is_alive():
            continue
        
    except KeyboardInterrupt:
        print(f"\nAborted")
        threadFlag = False
        sys.exit(1)
        
    threadFlag = False

    client_socket.close()
    print(f"\n{YELLOW}The Strawberry chat client has been closed.{RESET}")
    

threadFlag = True

if __name__ == "__main__":
    main()
    pass
