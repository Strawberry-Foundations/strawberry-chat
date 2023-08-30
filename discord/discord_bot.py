# unfinished
from discord.ext import commands, tasks
import discord
import socket
import datetime
import re
import time
import threading

bot = commands.Bot(command_prefix='.', intents=discord.Intents.all())
log_channel_id = 1140708601372086313
host = "192.168.0.157"
port = 8080


def escape_ansi(line):
    ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', line)


def stbchat_login(sock):
    sock.send("Discord".encode("utf8"))
    time.sleep(1)
    sock.send("".encode("utf8"))
    time.sleep(1)

def discord_login(token):
    bot.run(token)


def discord_to_stbchat(sock, msg=None):    
    try:
        sock.send(escape_ansi(msg).encode("utf8"))

    except Exception as e:
        print(e)


def stbchat_to_discord(sock):
    while threadFlag: 
        try:
            message = str
            message = sock.recv(2048).decode()
            
            if message:
                # print("[{}] {}".format(datetime.datetime.now().strftime("%H:%M"), message))
                return message

            else:
                break
            
        except Exception as e:
            print(e)
            break

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    

@bot.event
async def on_message(message):
    log_channel = bot.get_channel(log_channel_id)
    
    if message.author == bot.user:
        pass
    
    else:
        try:
            if log_channel:
                global log_message
                global clientSocket
                
                if message.attachments:
                    if message.content == "":
                        for attachment in message.attachments:
                            log_message = f"({message.author.display_name}): {attachment.url}"
                    else:
                        for attachment in message.attachments:
                            log_message = f"({message.author.display_name}): {message.content} ({attachment.url})"
                            
                else:
                    log_message = f"({message.author.display_name}): {message.content}"
                
                discord_to_stbchat(clientSocket, log_message)
                
        except Exception as e:
            print(e)
        
    await bot.process_commands(message)
            
def main():
    global threadFlag
    global clientSocket
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try: 
        clientSocket.connect((host, port))
        
    except: 
        print("server not reachable")
        exit(1)
        
    sendingThread = threading.Thread(target=discord_to_stbchat, args=(clientSocket,))
    receivingThread = threading.Thread(target=stbchat_to_discord, args=(clientSocket,))
    
    stbchat_login(clientSocket)
    
    receivingThread.start()
    sendingThread.start()
    
    discord_login("s")

    try:
        while receivingThread.is_alive() and sendingThread.is_alive():
            continue
        
    except KeyboardInterrupt:
        print(f"\nAborted")
        threadFlag = False
        exit(1)
    
    threadFlag = False
    
    clientSocket.close()
    print(f"\nClosed application")
    

threadFlag = True

if __name__ == "__main__":
    main()
    pass

