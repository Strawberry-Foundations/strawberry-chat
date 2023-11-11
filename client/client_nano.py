#!/usr/bin/env python3

import socket
import sys
import colorama
import datetime
import threading
import json
import time 

ver             = "1.1.0"
author          = "Juliandev02"
use_sys_argv    = False
experimental_debug_mode = False

def current_time():
    return datetime.datetime.now().strftime("%H:%M")

def delete_last_line():
    sys.stdout.write("\x1b[1A")
    sys.stdout.write("\x1b[2K")

def conv_json_data(data):
    return json.loads(data)

def badge_handler(badge):
    if not badge == "":
        return " [" + badge + "]"
    else:
        return ""

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
            delete_last_line()
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
                            fmt = f"[{current_time()}] {role_color}{username}{badge}:\033[0m {message}"
                        else:
                            fmt = f"[{current_time()}] {role_color}{nickname} (@{username.lower()}){badge}:\033[0m {message}"
                            
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
            if experimental_debug_mode: print(f"Error while receiving server data: Has the connection been interrupted?")
            pass

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
