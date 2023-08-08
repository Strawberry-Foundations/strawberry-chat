#!/usr/bin/env python3

import socket
import sys
import colorama
from colorama import Fore
import datetime
import threading
import yaml
from yaml import SafeLoader
import time

# Open Configuration
with open("config.yml") as config:
        data = yaml.load(config, Loader=SafeLoader)
        
lang = data['language']

# Color Variables
class Colors:
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'
    
ver = "2.0.20_beta"
useSysArgv = False

def isVerified(index):
    verified = data["server"][index]["verified"]
    if verified == True:
        return f"[{Str.Verified}] "
    else:
        return ""

class Str:
    if lang == "de":
        Welcome = "Willkommen zurück!"
        Verified = "Verifiziert"
        AvailableServers = "Verfügbare Chat-Server"
        Custom = "Benutzerdefiniert"
        SelChatServer = "Auswahl des Chat-Servers: "
        TryConnection = "Es wird versucht, eine Verbindung mit dem Server herzustellen..."
        AutologinActive = "Autologin ist aktiv."
        AutologinNotActive = "Autologin ist nicht aktiv."
        AutologinNotAvailable = "Autologin ist nicht verfügbar."
        Ipaddr = "IP-Adresse: "
        Port = "Port: "
        Warning = "Warnung"
        InvalidServerSelection = "Dieser Server existiert nicht!"
        InvalidArgument = "Dieser Befehl existiert nicht!"
        ErrCouldNotSendMessage = "Fehler beim Senden der Nachricht!"
        ErrNotReachable = "Der Server ist nicht erreichbar! Versuche es später erneuert oder kontaktiere den Server-Besitzer."
        CloseApplication = "Der Strawberry Client wurde beendet."
        Aborted = "Der Strawberry Client wurde abgebrochen!"
        ConnectedToServer = "Verbindung mit dem Server %s war erfolgreich. Viel Spaß!"
        
    if lang == "en":
        Welcome = "Welcome back!"
        Verified = "Verified"
        AvailableServers = "Available Thread-Servers"
        Custom = "Custom"
        SelChatServer = "Chat server selection: "
        TryConnection = "An attempt is made to establish a connection with the server..."
        AutologinActive = "Autologin is active."
        AutologinNotActive = "Autologin is not active."
        AutologinNotAvailable = "Autologin is not available."
        Ipaddr = "IP-Address: "
        Port = "Port: "
        Warning = "Warning"
        InvalidServerSelection = "This server does not exist!"
        InvalidArgument = "This command does not exist!"
        ErrCouldNotSendMessage = "Could not send the message!"
        ErrNotReachable = "The server is not available! Try again later or contact the server owner."
        CloseApplication = "The Strawberry client has been closed."
        Aborted = "The Strawberry client has been cancelled!"
        ConnectedToServer = "Connection with the server %s was successful. Have fun!"

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
        print(f"{Fore.RED + Colors.BOLD}{Str.InvalidArgument}{Fore.RESET + Colors.RESET}")
        sys.exit(1)

else:
    print(f"{Fore.CYAN + Colors.BOLD + Colors.UNDERLINE}Strawberry Chat Client (stbchat) (v{ver}){Colors.RESET}")
    print(f"{Fore.LIGHTGREEN_EX}{Str.Welcome}{Fore.RESET}\n")
    print(f"{Fore.GREEN + Colors.BOLD + Colors.UNDERLINE}{Str.AvailableServers}:{Fore.RESET + Colors.RESET}")

    for i in range(len(data["server"])):
        print(f"{Fore.LIGHTBLUE_EX}[{i + 1}]{Fore.RESET} {Colors.BOLD}{data['server'][i]['name']}{Colors.RESET} {Fore.LIGHTCYAN_EX}{isVerified(i)}{Fore.RESET}{Fore.LIGHTYELLOW_EX}({data['server'][i]['type']})")

    print(f"{Fore.LIGHTBLUE_EX}[{len(data['server']) + 1}]{Fore.RESET} {Colors.BOLD}{Str.Custom}{Colors.RESET}\n")


    try:
        server_selection = input(f"{Fore.LIGHTCYAN_EX}{Str.SelChatServer}{Fore.RESET}")
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}{Str.Aborted}{Fore.RESET}")
        sys.exit(1)

    server_count = len(data['server'])
    custom_server_sel = server_count + 1
    custom_server_sel = str(custom_server_sel)
    
    if server_selection == custom_server_sel:
        host = input(f"{Fore.LIGHTBLUE_EX + Colors.BOLD}{Str.Ipaddr}{Fore.RESET + Colors.RESET}")
        port = input(f"{Fore.LIGHTBLUE_EX + Colors.BOLD}{Str.Port}{Fore.RESET + Colors.RESET}")
        port = int(port)

    elif server_selection > custom_server_sel:
        print(f"{Fore.RED + Colors.BOLD}{Str.InvalidServerSelection}{Fore.RESET + Colors.RESET}")
        sys.exit(1)
        
    elif server_selection == "":
        print(f"{Fore.RED + Colors.BOLD}{Str.InvalidServerSelection}{Fore.RESET + Colors.RESET}")
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
            print(f"{Fore.GREEN + Colors.BOLD}{Str.AutologinActive}{Fore.RESET + Colors.RESET}\n")
            sock.send(f"{data['server'][(int(server_selection) - 1)]['credentials']['username']}".encode("utf8"))
            time.sleep(0.1)
            sock.send(f"{data['server'][(int(server_selection) - 1)]['credentials']['password']}".encode("utf8"))
        
        else:
            print(f"{Fore.GREEN + Colors.BOLD}{Str.AutologinNotActive}{Fore.RESET + Colors.RESET}\n")
    elif server_selection == custom_server_sel:
        print(f"{Fore.YELLOW + Colors.BOLD}{Str.Warning}: {Str.AutologinNotAvailable}{Fore.RESET + Colors.RESET}\n")
        
    else:
        if enableAutologin == True:
            print(f"{Fore.GREEN + Colors.BOLD}{Str.AutologinActive}{Fore.RESET + Colors.RESET}\n")
            sock.send(f"{data['server'][(int(server_selection) - 1)]['credentials']['username']}".encode("utf8"))
            time.sleep(0.1)
            sock.send(f"{data['server'][(int(server_selection) - 1)]['credentials']['password']}".encode("utf8"))
        
        else:
            print(f"{Fore.GREEN + Colors.BOLD}{Str.AutologinNotActive}{Fore.RESET + Colors.RESET}\n")
    
    while threadFlag:
        try:
            message = input("")
            deleteLastLine()
            sock.send(message.encode("utf8"))

        except:
            print(f"{Fore.RED + Colors.BOLD}{Str.ErrCouldNotSendMessage}{Fore.RESET + Colors.RESET}")
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
            print(f"{Fore.RED + Colors.BOLD}{Str.ErrNotReachable}{Fore.RESET + Colors.RESET}")
            break

def main():
    global threadFlag
    colorama.init()

    socketFamily = socket.AF_INET
    socketType = socket.SOCK_STREAM
    clientSocket = socket.socket(socketFamily, socketType)
    
    # Connects to the server
    try: 
        print(f"{Fore.YELLOW + Colors.BOLD}{Str.TryConnection}{Fore.RESET + Colors.RESET}")
        clientSocket.connect((host, port))
    except: 
        print(f"{Fore.RED + Colors.BOLD}{Str.ErrNotReachable}{Fore.RESET + Colors.RESET}")
        sys.exit(1)
    
    if useSysArgv == True:
        pass
    elif server_selection == custom_server_sel:
        print(f"{Fore.GREEN + Colors.BOLD}{Str.ConnectedToServer % host}{Fore.RESET + Colors.RESET}")
    else:
        print(f"{Fore.GREEN + Colors.BOLD}{Str.ConnectedToServer % data['server'][(int(server_selection) - 1)]['name']}{Fore.RESET + Colors.RESET}")
        
    sendingThread = threading.Thread(target=send, args=(clientSocket,))
    receivingThread = threading.Thread(target=receive, args=(clientSocket,))

    receivingThread.start()
    sendingThread.start()

    try:
        while receivingThread.is_alive() and sendingThread.is_alive():
            continue
    except KeyboardInterrupt:
        print(f"\n{Str.Aborted}")
        threadFlag = False
        sys.exit(1)
        
    threadFlag = False

    clientSocket.close()
    print(f"\n{Str.CloseApplication}")
    


threadFlag = True

if __name__ == "__main__":
    main()
    pass