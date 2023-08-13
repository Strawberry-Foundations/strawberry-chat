#!/usr/bin/env python3

import atexit
from colorama import Fore
import socket
import threading
import json
import os
import datetime

with open("./config.json", "r") as f:
    config = json.load(f)

ipaddr = config["adress"]
port = config["port"]

class Time:
    def currentTime():
        time = datetime.datetime.now()
        formattedTime = time.strftime("%H:%M:%S")
        return formattedTime

    def currentDate():
        date = datetime.date.today()
        formattedDate = date.strftime("%Y-%m-%d")
        return formattedDate

class Logger:
    def System(log_message):
        os.system(f"echo '[{Time.currentDate()} {Time.currentTime()}] {log_message}' >> log.txt")
        
    def Message(log_message):
        os.system(f"echo '[{Time.currentDate()} {Time.currentTime()}] {log_message}' >> messages.txt")

Logger.System("Server started")
    
def connectionThread(sock):
    while True:
        try:
            client, address = sock.accept()

        except:
            print(f"[{Fore.RED}!{Fore.RESET}]Something went wrong while accepting incoming connections!")
            break
        
        print(f"[{Fore.GREEN}>{Fore.RESET}] {address[0]} has connected")
        Logger.System(f"[>] {address[0]} has connected")
        
        addresses[client] = address
        threading.Thread(target=clientThread, args=(client,)).start()


def clientThread(client):
    address = addresses[client][0]
    try:
        user = getNickname(client)

    except:
        print("[" + Fore.YELLOW + "?" + Fore.RESET +
              "] Something went wrong while setting the nickname for {}!".format(address))
        del addresses[client]
        client.close()
        return
    
    print(f"[{Fore.GREEN}+{Fore.RESET}] {address} set its nickname to {user}")
    Logger.System(f"[+] {address} set its nickname to {user}")

    users[client] = user

    try:
        client.send(
            "Hi {}! You are now connected to the Chat. Type \"/help\" for a list of available commands!".format(user).encode("utf8"))

    except:
        print("Communication error with {} ({}).".format(address, user))
        del addresses[client]
        del users[client]
        client.close()
        return

    broadcast("{} has joined the chat room!".format(user))

    while True:
        try:
            message = client.recv(2048).decode("utf8")
            
            if message == "/quit":
                client.send("You left the chat!".encode("utf8"))
                del addresses[client]
                del users[client]
                client.close()
                print("[" + Fore.RED + "<" + Fore.RESET +
                      "] {} ({}) has left.".format(address, user))
                Logger.System(f"[<] {address} has left")
                broadcast("{} has left the chat.".format(user))
                break

            elif message == "/online":
                onlineUsers = ', '.join(
                    [user for user in sorted(users.values())])
                client.send("Users online are: {}".format(
                    onlineUsers).encode("utf8"))

            elif message == "/help":
                client.send(
                    "Available commands are /help, /online and /quit".encode("utf8"))

            else:
                # print("{} ({}): {}".format(address, user, message))
                Logger.Message(f"{address} ({user}): {message}")
                broadcast(message, user)
                
        except:
            print("[" + Fore.RED + "<" + Fore.RESET +
                  "] {} ({}) has left.".format(address, user))
            Logger.System(f"[<] {address} has left")
            del addresses[client]
            del users[client]
            client.close()
            broadcast("{} has left the chat.".format(user))
            break


def getNickname(client):
    client.send("Welcome to the Chat! Please type your nickname:".encode("utf8"))
    nickname = client.recv(2048).decode("utf8")
    alreadyTaken = False

    if nickname in users.values():
        alreadyTaken = True
        while alreadyTaken:
            client.send(
                "This nickname has already been taken. Please choose a different one:".encode("utf8"))
            nickname = client.recv(2048).decode("utf8")
            if nickname not in users.values():
                alreadyTaken = False

    return nickname


def broadcast(message, sentBy=""):
    try:
        if sentBy == "":
            for user in users:
                user.send(message.encode("utf8"))

        else:
            for user in users:
                user.send("{}: {}".format(sentBy, message).encode("utf8"))

    except:
        print("Something went wrong while broadcasting a message!")


def cleanup():
    if len(addresses) != 0:
        for sock in addresses.keys():
            sock.close()
    print("Runtime has stopped.")


def main():
    atexit.register(cleanup)

    socketFamily = socket.AF_INET
    socketType = socket.SOCK_STREAM
    serverSocket = socket.socket(socketFamily, socketType)
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serverSocket.bind((ipaddr, port))
    serverSocket.listen()
    print(Fore.GREEN + "-- Chat App --" + Fore.RESET)
    print("")
    print(Fore.YELLOW + "Thread is running on {}:{}".format(ipaddr, port) + Fore.RESET)

    connThread = threading.Thread(
        target=connectionThread, args=(serverSocket,))
    connThread.start()
    connThread.join()

    cleanup()
    serverSocket.close()
    Logger.System("Server stopped")
    print("Server has shut down.")
    

users = {}
addresses = {}

if __name__ == "__main__":
    main()
    pass
