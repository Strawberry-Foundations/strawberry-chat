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

# Color Variables
class Colors:
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'
    GRAY = "\033[90m"

# Alias for colorama colors
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

api = "http://192.168.0.157:8081/v1/"
ver = "2.2.0_beta"
author = "Juliandev02"

try:
    requests.get(api)
    
except: 
    print(f"{RED + Colors.UNDERLINE}Connection Error{RESET + Colors.RESET}")
    print(f"{YELLOW}The server did not give a valid answer.\nEither the Strawberry API servers are overloaded, or offline. Please try again later{RESET}")

# Path of client.py
client_dir = os.path.dirname(os.path.realpath(__file__))

# Open Configuration
with open(client_dir + "/config.yml") as config:
        data = yaml.load(config, Loader=SafeLoader)

lang = data['language']
langs = ["de_DE", "en_US"]

with open(client_dir + "/lang.yml", encoding="utf-8") as langStrings:
        Str = yaml.load(langStrings, Loader=SafeLoader)




if lang not in langs:
    print(f"{Fore.RED + Colors.BOLD}Error loading selected language is not available.")
    print(f"{Fore.YELLOW + Colors.BOLD}Falling back to en_US\n")
    time.sleep(1)
    lang = "en_US"
    

useSysArgv = False

def isVerified(addr):
    try:
        verified = requests.get(api + "server/verified?addr=" + addr)
        
        if verified.text == "True":
            return f"[{Str[lang]['Verified']}] "
        else:
            return ""
        
    except Exception as e: 
        print(e)

if len(sys.argv) >= 2:
    if sys.argv[1] == "--server":
        useSysArgv = True
        server_selection = sys.argv[2]
        host = data["server"][(int(server_selection) - 1)]["address"]
        port = data["server"][(int(server_selection) - 1)]["port"]
        port = int(port)
        
        try:
            global enableAutologin
            enableAutologin = data["server"][(int(server_selection) - 1)]["autologin"]
            
        except KeyError:
            enableAutologin = False
    else:
        print(f"{Fore.RED + Colors.BOLD}{Str[lang]['InvalidArgument']}{Fore.RESET + Colors.RESET}")
        sys.exit(1)

else:
    print(f"{Fore.CYAN + Colors.BOLD + Colors.UNDERLINE}Strawberry Chat Client (stbchat) (v{ver}){Colors.RESET}")
    print(f"{Fore.LIGHTGREEN_EX}{Str[lang]['Welcome']}{Fore.RESET}\n")
    print(f"{Fore.GREEN + Colors.BOLD + Colors.UNDERLINE}{Str[lang]['AvailableServers']}:{Fore.RESET + Colors.RESET}")

    for i in range(len(data["server"])):
        print(f"{Fore.LIGHTBLUE_EX}[{i + 1}]{Fore.RESET} {Colors.BOLD}{data['server'][i]['name']}{Colors.RESET} {Fore.LIGHTCYAN_EX}{isVerified(data['server'][i]['address'])}{Fore.RESET}{Fore.LIGHTYELLOW_EX}({data['server'][i]['type']})")

    print(f"{Fore.LIGHTBLUE_EX}[{len(data['server']) + 1}]{Fore.RESET} {Colors.BOLD}{Str[lang]['Custom']}{Colors.RESET}\n")


    try:
        server_selection = input(f"{Fore.LIGHTCYAN_EX}{Str[lang]['SelChatServer']}{Fore.RESET}")
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}{Str[lang]['Aborted']}{Fore.RESET}")
        sys.exit(1)

    server_count = len(data['server'])
    custom_server_sel = server_count + 1
    custom_server_sel = str(custom_server_sel)
    
    if server_selection == custom_server_sel:
        host = input(f"{Fore.LIGHTBLUE_EX + Colors.BOLD}{Str[lang]['Ipaddr']}{Fore.RESET + Colors.RESET}")
        port = input(f"{Fore.LIGHTBLUE_EX + Colors.BOLD}{Str[lang]['Port']}{Fore.RESET + Colors.RESET}")
        port = int(port)

    elif server_selection > custom_server_sel:
        print(f"{Fore.RED + Colors.BOLD}{Str[lang]['InvalidServerSelection']}{Fore.RESET + Colors.RESET}")
        sys.exit(1)
        
    elif server_selection == "":
        print(f"{Fore.RED + Colors.BOLD}{Str[lang]['InvalidServerSelection']}{Fore.RESET + Colors.RESET}")
        sys.exit(1)
        
    else:
        try:
            enableAutologin = data["server"][(int(server_selection) - 1)]["autologin"]
            
        except KeyError:
            enableAutologin = False 
            
        try:
            host = data["server"][(int(server_selection) - 1)]["address"]
            port = data["server"][(int(server_selection) - 1)]["port"]
            port = int(port)
            
        except KeyError:
            pass
    

def currentTime():
    now = datetime.datetime.now()
    formattedTime = now.strftime("%H:%M")
    return formattedTime


def deleteLastLine():
    cursorUp = "\x1b[1A"
    eraseLine = "\x1b[2K"
    sys.stdout.write(cursorUp)
    sys.stdout.write(eraseLine)


def send(sock):
    if useSysArgv == True:
        if enableAutologin == True:
            print(f"{Fore.GREEN + Colors.BOLD}{Str[lang]['AutologinActive']}{Fore.RESET + Colors.RESET}\n")
            sock.send(f"{data['server'][(int(server_selection) - 1)]['credentials']['username']}".encode("utf8"))
            time.sleep(0.1)
            sock.send(f"{data['server'][(int(server_selection) - 1)]['credentials']['password']}".encode("utf8"))
        
        else:
            print(f"{Fore.GREEN + Colors.BOLD}{Str[lang]['AutologinNotActive']}{Fore.RESET + Colors.RESET}\n")
            
    elif server_selection == custom_server_sel:
        print(f"{Fore.YELLOW + Colors.BOLD}{Str[lang]['Warning']}: {Str[lang]['AutologinNotAvailable']}{Fore.RESET + Colors.RESET}\n")
        
    else:
        if enableAutologin == True:
            print(f"{Fore.GREEN + Colors.BOLD}{Str[lang]['AutologinActive']}{Fore.RESET + Colors.RESET}\n")
            sock.send(f"{data['server'][(int(server_selection) - 1)]['credentials']['username']}".encode("utf8"))
            time.sleep(0.1)
            sock.send(f"{data['server'][(int(server_selection) - 1)]['credentials']['password']}".encode("utf8"))
        
        else:
            print(f"{Fore.GREEN + Colors.BOLD}{Str[lang]['AutologinNotActive']}{Fore.RESET + Colors.RESET}\n")
    
    while threadFlag:
        try:
            message = input("")
            deleteLastLine()
            sock.send(message.encode("utf8"))

        except:
            print(f"{Fore.RED + Colors.BOLD}{Str[lang]['ErrCouldNotSendMessage']}{Fore.RESET + Colors.RESET}")
            break

def receive(sock):
    while threadFlag:
        try:
            message = sock.recv(2048).decode()
            
            if message:
                print("[{}] {}".format(currentTime(), message))
            else:
                break
            
        except:
            print(f"{Fore.RED + Colors.BOLD}{Str[lang]['ErrNotReachable']}{Fore.RESET + Colors.RESET}")
            break

def main():
    global threadFlag
    colorama.init()
    
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try: 
        print(f"{Fore.YELLOW + Colors.BOLD}{Str[lang]['TryConnection']}{Fore.RESET + Colors.RESET}")
        clientSocket.connect((host, port))
        
    except: 
        print(f"{Fore.RED + Colors.BOLD}{Str[lang]['ErrNotReachable']}{Fore.RESET + Colors.RESET}")
        sys.exit(1)
    
    if useSysArgv == True:
        pass
    
    elif server_selection == custom_server_sel:
        print(f"{Fore.GREEN + Colors.BOLD}{Str[lang]['ConnectedToServer'] % host}{Fore.RESET + Colors.RESET}")
        
    else:
        print(f"{Fore.GREEN + Colors.BOLD}{Str[lang]['ConnectedToServer'] % data['server'][(int(server_selection) - 1)]['name']}{Fore.RESET + Colors.RESET}")
        
    sendingThread = threading.Thread(target=send, args=(clientSocket,))
    receivingThread = threading.Thread(target=receive, args=(clientSocket,))

    receivingThread.start()
    sendingThread.start()

    try:
        while receivingThread.is_alive() and sendingThread.is_alive():
            continue
        
    except KeyboardInterrupt:
        print(f"\n{Str[lang]['Aborted']}")
        threadFlag = False
        sys.exit(1)
        
    threadFlag = False

    clientSocket.close()
    print(f"\n{Str[lang]['CloseApplication']}")
    

threadFlag = True

if __name__ == "__main__":
    main()
    pass
