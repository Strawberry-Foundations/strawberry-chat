from kivy.app import App
from kivy.uix.label import Label
import socket
import sys
import colorama
from colorama import Fore
import datetime
import threading

host = "192.168.0.157"
port = 8080

# Return current time
def currentTime():
    now = datetime.datetime.now()
    formattedTime = now.strftime("%H:%M")
    return formattedTime


def send(sock):
    while threadFlag:
        try:
            message = input("")
            sock.send(message.encode("utf8"))

        except:
            print(f"Could not send the message!")
            break
        

global message
class Main(App):            
    def build(self):
        while threadFlag:
            try:
                message = clientSocket.recv(2048).decode()
                
                if message:
                    print("[{}] {}".format(currentTime(), message))
                else:
                    break
                
            except:
                print(f"An attempt is made to establish a connection with the server...")
                break
        return Label(text=message)
    


def main():
    global threadFlag
    colorama.init()
    global clientSocket
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try: 
        print("An attempt is made to establish a connection with the server...")
        clientSocket.connect((host, port))
        
    except: 
        print(f"The server is not available! Try again later or contact the server owner.")
        sys.exit(1)
        
    sendingThread = threading.Thread(target=send, args=(clientSocket,))
    # receivingThread = threading.Thread(target=receive, args=(clientSocket,))
    appThread = threading.Thread(target=Main().run(), args=(clientSocket,))
    

    # receivingThread.start()
    sendingThread.start()
    appThread.start()

    try:
        while sendingThread.is_alive():
            continue
        
    except KeyboardInterrupt:
        print(f"\nAborted")
        threadFlag = False
        sys.exit(1)
        
    threadFlag = False

    clientSocket.close()
    print(f"\nThe Strawberry chat client has been closed.")
    

threadFlag = True

if __name__ == "__main__":
    main()
    pass