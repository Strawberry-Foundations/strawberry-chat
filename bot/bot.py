import sys
import socket
import threading
import time

class Formatting:
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    PURPLE = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

version = "1.0"
msg_login = None

def flags(enableUserInput_flag):
    global enableUserInput
    enableUserInput = enableUserInput_flag
    pass

def login(username, token):
    global uname
    global bot_token
    uname = username
    bot_token = token

def login_message(message):
    global msg_login
    msg_login = message

def send(sock):
    def deleteLastLine():
        cursorUp = "\x1b[1A"
        eraseLine = "\x1b[2K"
        sys.stdout.write(cursorUp)
        sys.stdout.write(eraseLine)
        
    sock.send(str(uname).encode("utf8"))
    time.sleep(0.1)
    sock.send(str(bot_token).encode("utf8"))
    time.sleep(0.1)

    if msg_login is not None:
        sock.send(msg_login.encode("utf8"))

    if enableUserInput is True:
        while threadFlag:
            try:
                message = input("")
                deleteLastLine()
                sock.send(message.encode("utf8"))

            except:
                print("Message could not be sent")
                break

class client:
    def send(message):
        sock = clientSocket
        sock.send(str(message).encode("utf8"))
        

    
def receive(sock):
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
                print("{}".format(message))
                
            else:
                break
            
        except Exception as e:
            print(f"{Formatting.RED + Formatting.BOLD}The Server is not reachable{Formatting.RESET}")
            print(f"{Formatting.RED + Formatting.BOLD}Maybe this can help you:{Formatting.RESET}")
            print(e)
            break

def main(host, port):
    global threadFlag
    socketFamily = socket.AF_INET
    socketType = socket.SOCK_STREAM
    global clientSocket
    clientSocket = socket.socket(socketFamily, socketType)
    
    
    try: 
        clientSocket.connect((host, port))
    except: 
        print("The bot could not connect to the server.... Is the server online?")
        exit(1)
        
    print(f"{Formatting.CYAN + Formatting.BOLD}Strawberry Chat API v{version} (Vanilla Cake)")
    print(f"{Formatting.GREEN + Formatting.BOLD}The bot has connected{Formatting.RESET}\n")
    sendingThread = threading.Thread(target=send, args=(clientSocket,))
    receivingThread = threading.Thread(target=receive, args=(clientSocket,))
    receivingThread.start()
    sendingThread.start()
    
    try:
        while receivingThread.is_alive():
            continue
        
    except KeyboardInterrupt:
        print("\nAborted..")
        threadFlag = False
        exit(1)
    
    threadFlag = False
    clientSocket.close()
    print("\nYou can stop the bot now.")

# Flag used for threads termination
threadFlag = True

class Bot:
    class Net:
        Host = "192.168.0.157"
        Port = 8080
    
    class Credentials:
        Username = "Strawberry"
        Token = "QEAOyPaVCF6o-BJuIOaa0O1ss-psUTSjNyexNu"
        
flags(enableUserInput_flag=True)
login(Bot.Credentials.Username, Bot.Credentials.Token)
login_message(f"{Formatting.BOLD}Hallo! Ich bin der offizielle Bot für den Strawberry Chat! Vielen Dank für's hinzufügen!{Formatting.RESET}")


if __name__ == "__main__":
    main(Bot.Net.Host, Bot.Net.Port)
    pass