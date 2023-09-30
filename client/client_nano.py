#!/usr/bin/env python3

import socket
import sys
import colorama
import datetime
import threading

ver             = "1.0.1"
author          = "Juliandev02"
use_sys_argv    = False

def currentTime():
    now = datetime.datetime.now().strftime("%H:%M")
    return now

def deleteLastLine():
    cursorUp = "\x1b[1A"
    eraseLine = "\x1b[2K"
    sys.stdout.write(cursorUp)
    sys.stdout.write(eraseLine)

if len(sys.argv) >= 1:
    use_sys_argv = True
    args = sys.argv[1]
    
    host = args.split(":")[0]
    port = int(args.split(":")[1])

else:
    try:
        host = input(f"IP-Address: ")
        port = int(input(f"Port: "))
    except: 
        print(f"\nThe Strawberry chat client has been closed.")
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
                print(f"Could not send the message!")
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
            print(f"Trying to connect to the server...")
            break

def main():
    global threadFlag
    colorama.init()
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try: 
        print(f"Trying to connect to the server...")
        client_socket.connect((host, port)) 
    except: 
        print(f"Connection refused: The server is not available!")
        sys.exit(1)
    
    if use_sys_argv == True:
        pass
        
    sending_thread  = threading.Thread(target=send, args=(client_socket,))
    recv_thread     = threading.Thread(target=receive, args=(client_socket,))

    recv_thread.start()
    sending_thread.start()

    try:
        while recv_thread.is_alive() and sending_thread.is_alive():
            continue
    except KeyboardInterrupt:
        print(f"\nAborted")
        threadFlag = False
        sys.exit(1)
        
    threadFlag = False

    client_socket.close()
    print(f"\nThe Strawberry chat client has been closed.")
    

threadFlag = True

if __name__ == "__main__":
    main()
    pass
