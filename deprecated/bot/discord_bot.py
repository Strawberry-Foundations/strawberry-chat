# Warning: This is unfinished and should not be used anymore

import sys
import socket
import colorama
from colorama import Fore
import datetime
import threading
import requests
import re
import time
import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='.', intents=discord.Intents.all())


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    
@bot.event
async def on_message(message):
    await bot.process_commands(message)
    
    if message.author == bot.user:
        return
    
    msgContent = message.content.lower()
    print(msgContent)
    if msgContent == 'ja':
        await message.channel.send('Ja')
            

@bot.command()
async def ping(ctx):
    await ctx.send(":ping_pong: Pong!")

# Color Variables
class Colors:
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'

host = "192.168.0.157"
port = 8080

port = int(port)

def currentTime():
    now = datetime.datetime.now()
    formattedTime = now.strftime("%H:%M")
    return formattedTime

def deleteLastLine():
    cursorUp = "\x1b[1A"
    eraseLine = "\x1b[2K"
    sys.stdout.write(cursorUp)
    sys.stdout.write(eraseLine)

def escape_ansi(line):
    ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', line)


def send(sock):
    sock.send("discord".encode("utf8"))
    time.sleep(1)
    sock.send("discord".encode("utf8"))
    time.sleep(1)
    
    while threadFlag:
        try:
            message = input("")
            deleteLastLine()
            sock.send(message.encode("utf8"))

        except Exception as e:
            print(e)
            break

def receive(sock):    
    while threadFlag: 
        try:
            message = str
            message = sock.recv(2048).decode()
            dc_msg = message
            
            @bot.event
            async def on_condition_triggered():
                channel_id = 1140708601372086313
                channel = bot.get_channel(channel_id)

                if channel:
                    await channel.send(escape_ansi(message))
                else:
                    print('Kanal nicht gefunden.')
                
                while threadFlag:
                    if message:
                        print("[{}] {}".format(currentTime(), message))

                    else:
                        break
            
            
            
                          
                
        except Exception as e:
            print(e)
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
        print("server not reachable")
        exit(1)
        
    print(f"{Fore.GREEN}connected to server{Fore.RESET}\n")
    # Creates two threads for sending and receiving messages from the server
    sendingThread = threading.Thread(target=send, args=(clientSocket,))
    receivingThread = threading.Thread(target=receive, args=(clientSocket,))
    # Start those threads
    receivingThread.start()
    sendingThread.start()
    TOKEN = ":)"
    bot.run(TOKEN)
    

    
    # Checks if both threads are alive for handling their termination
    try:
        while receivingThread.is_alive() and sendingThread.is_alive():
            continue
    except KeyboardInterrupt:
        print(f"\nAborted")
        threadFlag = False
        exit(1)
    
    threadFlag = False
    # Finally closes the socket object connection
    clientSocket.close()
    print(f"\nClosed application")

# Flag used for threads termination
threadFlag = True

if __name__ == "__main__":
    main()
    pass