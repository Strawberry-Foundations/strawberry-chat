# Warning: This is unfinished and should not be used anymore

import sys
import socket
import colorama
from colorama import Fore
import datetime
import threading

# Color Variables
class Colors:
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'

lang = "de"

if lang == "de":
    WelcomeMessage = "Willkommen!"
    AvailableServers = "Verfügbare Thread-Server"
    StringOfficial = f"{Fore.GREEN}(Offiziell){Fore.RESET}"
    StringOwn = "Benutzerdefiniert.."
    EnterServerID = "Eingabe der Server-ID → "
    EnterThreadChannel = "Eingabe des Thread-Kanals → "
    NoValidServerID = f"{Fore.RED}Die Server-ID ist ungültig!{Fore.RESET}"
    ErrCouldNotSendMessage = f"{Fore.RED}Fehler beim Senden der Nachricht!{Fore.RESET}"
    ErrNotReachable = f"{Fore.RED}Der Server ist nicht erreichbar!{Fore.RESET}"
    CloseApplication = "Programm wurde beendet."
    Aborted = f"{Fore.YELLOW}Programm wurde abgebrochen!{Fore.RESET}"
    ConnectedToServer = f"{Fore.GREEN}Verbindung mit Server wurde hergestellt!{Fore.RESET}"
    AvailableThreadChannels = "%s unterstützt mehrere Thread-Kanäle. Verfügbare Thread-Kanäle: "
    
if lang == "en":
    WelcomeMessage = "Welcome!"
    AvailableServers = "Available Thread-Servers"
    StringOfficial = f"{Fore.GREEN}(Official){Fore.RESET}"
    StringOwn = "Custom.."
    EnterServerID = "Enter the Server-ID → "
    EnterThreadChannel = "Enter the Thread-Channel → "
    NoValidServerID = f"{Fore.RED}The Server-ID is invalid!{Fore.RESET}"
    ErrCouldNotSendMessage = f"{Fore.RED}Could not send the message!{Fore.RESET}"
    ErrNotReachable = f"{Fore.RED}The Server is not reachable!{Fore.RESET}"
    CloseApplication = "Program has been closed."
    Aborted = f"{Fore.YELLOW}Program has been aborted!{Fore.RESET}"
    ConnectedToServer = f"{Fore.GREEN}Connected to the server!{Fore.RESET}"
    AvailableThreadChannels = "%s supports multiple Thread-Channels. Available Thread-Channels: "

host = "192.168.0.157"
port = 8080

port = int(port)

def currentTime():
    # Retrieves local time formatted as HH:MM:SS
    now = datetime.datetime.now()
    formattedTime = now.strftime("%H:%M")
    return formattedTime

def deleteLastLine():
    # Writes ANSI codes to perform cursor movement and current line clear
    cursorUp = "\x1b[1A"
    eraseLine = "\x1b[2K"
    sys.stdout.write(cursorUp)
    sys.stdout.write(eraseLine)

def send(sock):
    import time
    sock.send("Strawberry [Bot]".encode("utf8"))
    time.sleep(0.1)
    sock.send("strawberry".encode("utf8"))
    time.sleep(0.1)
    sock.send("Hallo! Ich bin der offizielle Bot für den Strawberry Chat! Vielen Dank für's hinzufügen!".encode("utf8"))
    # Handles sending messages to the server
    while threadFlag:
        try:
            message = input("")
            deleteLastLine()
            sock.send(message.encode("utf8"))

        except:
            print(ErrCouldNotSendMessage)
            break

def receive(sock):
    # Handles receiving messages from the server
    while threadFlag:
        try:
            message = str
            
            message = sock.recv(2048).decode()
            index = message.find(":")
            part = message[index + 2:]
            
            match part:
                case "Hallo":
                    sock.send("Hallo :D".encode("utf8"))
                
                case "!help":
                    sock.send("Das kann ich noch nicht. Wie wärs wenn du dir mal die eingebauten Commands anschaust?".encode("utf8"))
            
            if message:
                print("[{}] {}".format(currentTime(), message))
            else:
                # When the server closes the socket, messages received are empty
                break
        except:
            print(ErrNotReachable)
            break

def main():
    # main() will refer to threadFlag as to the global variable defined globally
    global threadFlag
    # Colorama handles the ANSI escape codes to work also on Windows
    colorama.init()
    # The host and port of the chat server

    # Creates the socket for a TCP application
    socketFamily = socket.AF_INET
    socketType = socket.SOCK_STREAM
    clientSocket = socket.socket(socketFamily, socketType)
    
    # Connects to the server
    try: 
        clientSocket.connect((host, port))
    except: 
        print(ErrNotReachable)
        exit(1)
        
    print(f"{Fore.GREEN}{ConnectedToServer}{Fore.RESET}\n")
    # Creates two threads for sending and receiving messages from the server
    sendingThread = threading.Thread(target=send, args=(clientSocket,))
    receivingThread = threading.Thread(target=receive, args=(clientSocket,))
    # Start those threads
    receivingThread.start()
    sendingThread.start()
    
    # Checks if both threads are alive for handling their termination
    try:
        while receivingThread.is_alive() and sendingThread.is_alive():
            continue
    except KeyboardInterrupt:
        print(f"\n{Aborted}")
        threadFlag = False
        exit(1)
    
    threadFlag = False
    # Finally closes the socket object connection
    clientSocket.close()
    print(f"\n{CloseApplication}")

# Flag used for threads termination
threadFlag = True

if __name__ == "__main__":
    main()
    pass