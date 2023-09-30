#!/usr/bin/env python3

import socket
import sys
import colorama
from colorama import Fore
import datetime
import threading

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

ver             = "1.0.1"
author          = "Juliandev02"
use_sys_argv      = False

# Return current time
def currentTime():
    now = datetime.datetime.now()
    formattedTime = now.strftime("%H:%M")
    return formattedTime

# Delete last line to now show the written message
def deleteLastLine():
    cursorUp = "\x1b[1A"
    eraseLine = "\x1b[2K"
    sys.stdout.write(cursorUp)
    sys.stdout.write(eraseLine)


# If --server is in the arguments, skip server selection input
if len(sys.argv) >= 2:
    if sys.argv[1] == "--address":
        use_sys_argv = True
        args = sys.argv[2]
        
        host = args.split(":")[0]
        port = args.split(":")[1]
        port = int(port)

    else:
        print(f"{Fore.CYAN + Colors.BOLD + Colors.UNDERLINE}Strawberry Chat Client Lite - Help Menu{Colors.RESET}")
        print(f"{BLUE + Colors.BOLD}--address <host>:<port>: {RESET}Connect to server <host>:<port>")
        sys.exit(1)

# If no arguments passed, start client without any special functions
else:
    print(f"{Fore.CYAN + Colors.BOLD + Colors.UNDERLINE}Strawberry Chat Client Lite (stbchat_lite) (v{ver}){Colors.RESET}")
    print(f"{Fore.LIGHTGREEN_EX}Welcome back!{Fore.RESET}\n")

    try:
        host = input(f"{Fore.LIGHTBLUE_EX + Colors.BOLD}IP-Address: {Fore.RESET + Colors.RESET}")
        port = input(f"{Fore.LIGHTBLUE_EX + Colors.BOLD}Port: {Fore.RESET + Colors.RESET}")
        port = int(port)
        
    except: 
        print(f"\n{YELLOW}The Strawberry chat client has been closed.{RESET}")
        sys.exit(1)


def send(sock):
    while threadFlag:
        try:
            message = input("")
            deleteLastLine()
            sock.send(message.encode("utf8"))

        except:
            if threadFlag == False:
                pass
            else:
                print(f"{Fore.RED + Colors.BOLD}Could not send the message!{Fore.RESET + Colors.RESET}")
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
            print(f"{Fore.RED + Colors.BOLD}An attempt is made to establish a connection with the server...{Fore.RESET + Colors.RESET}")
            break

def main():
    global threadFlag
    colorama.init()
    
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try: 
        print(f"{Fore.YELLOW + Colors.BOLD}An attempt is made to establish a connection with the server...{Fore.RESET + Colors.RESET}")
        clientSocket.connect((host, port))
        
    except: 
        print(f"{Fore.RED + Colors.BOLD}The server is not available! Try again later or contact the server owner.{Fore.RESET + Colors.RESET}")
        sys.exit(1)
    
    if use_sys_argv == True:
        pass
        
    sendingThread = threading.Thread(target=send, args=(clientSocket,))
    receivingThread = threading.Thread(target=receive, args=(clientSocket,))

    receivingThread.start()
    sendingThread.start()

    try:
        while receivingThread.is_alive() and sendingThread.is_alive():
            continue
        
    except KeyboardInterrupt:
        print(f"\nAborted")
        threadFlag = False
        sys.exit(1)
        
    threadFlag = False

    clientSocket.close()
    print(f"\n{YELLOW}The Strawberry chat client has been closed.{RESET}")
    

threadFlag = True

if __name__ == "__main__":
    main()
    pass
