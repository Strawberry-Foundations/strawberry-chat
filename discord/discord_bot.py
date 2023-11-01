# unfinished
from discord.ext import commands, tasks
import discord
import socket
import datetime
import re
import time
import threading
import yaml
from yaml import SafeLoader

import scapi
from scapi import Scapi

with open("config.yml", encoding="utf-8") as config_file:
    config = yaml.load(config_file, Loader=SafeLoader)

log_channel_id  = config["bot"]["channel_id"]
token           = config["bot"]["token"]

stbchat_uname   = config["stbchat"]["username"]
stbchat_token   = config["stbchat"]["password"]
stbchat_host    = config["stbchat"]["server"]["host"]
stbchat_port    = config["stbchat"]["server"]["port"]

bot = commands.Bot(command_prefix='.', intents=discord.Intents.all())
scapi_bot = Scapi.Bot(username=stbchat_uname, token=stbchat_token, host=stbchat_host, port=stbchat_port)

scapi_bot.login()
scapi_bot.flag_handler(print_recv_msg=False, enable_user_input=True)


def escape_ansi(line):
    ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', line)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.event
async def on_message(message):
    target_channel_name = "🍓┇strawberry-chat"
    target_channel = discord.utils.get(message.guild.text_channels, name=target_channel_name)
    
    if message.author == bot.user:
        pass
    
    else:
        try:
            
            if message.channel.id == log_channel_id:
                global log_message

                if message.attachments:
                    if message.content == "":
                        for attachment in message.attachments:
                            log_message = f"({message.author.display_name}): {attachment.url}"
                    else:
                        for attachment in message.attachments:
                            log_message = f"({message.author.display_name}): {message.content} ({attachment.url})"
                            
                else:
                    log_message = f"({message.author.display_name}): {message.content}"
                
                scapi_bot.send_message(log_message)
            
            if target_channel:
                threadFlag = True
                while threadFlag: 
                    try:
                        msg = str
                        msg = clientSocket.recv(2048).decode()
                        
                        if msg:
                            print(msg + "\n")
                            await target_channel.send(escape_ansi(msg))

                        else:
                            break
                        
                    except Exception as e:
                        print(e)
                        break
                    
        except Exception as e:
            print(e)
        
    await bot.process_commands(message)

async def Commands():
    target_channel_name = "🍓┇strawberry-chat"
    target_channel = discord.utils.get(message.guild.text_channels, name=target_channel_name)
    
    while True:
        try:
            message = scapi_bot.recv_message(raw=True)
            await target_channel.send(escape_ansi(message))
            
        except: 
            scapi_bot.logger(f"{scapi.RED}An unknown exception occured{scapi.RESET}", type=Scapi.LogLevel.ERROR)
            break

# @bot.event
# async def on_message(message):
#     if message.author == bot.user:
#         return  # Ignoriere Nachrichten vom Bot selbst

#     # Bestimme den Zielkanal, in den die Nachricht weitergeleitet werden soll
#     target_channel_name = "🍓┇strawberry-chat"  # Ersetze "zielkanal" durch den Namen deines Zielkanals
#     target_channel = discord.utils.get(message.guild.text_channels, name=target_channel_name)

#     if target_channel:
#         # Sende die empfangene Nachricht in den Zielkanal
#         await target_channel.send(f'{message.author.name} hat geschrieben: {message.content}')
         
# def main():
#     global threadFlag
#     global clientSocket
#     clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
#     try: 
#         clientSocket.connect((stbchat_host, stbchat_port))
        
#     except: 
#         print("server not reachable")
#         exit(1)
        
#     # def stbchat_to_discord():
#     #     threadFlag = True
#     #     while threadFlag: 
#     #         try:
#     #             message = str
#     #             message = clientSocket.recv(2048).decode()
                
#     #             if message:
#     #                 print(message + "\n")
#     #                 return message

#     #             else:
#     #                 break
                
#     #         except Exception as e:
#     #             print(e)
#     #             break
        
#     sendingThread = threading.Thread(target=discord_to_stbchat, args=(clientSocket,))
#     # receivingThread = threading.Thread(target=receive, args=(clientSocket,))
        
#     # receivingThread.start()
#     sendingThread.start()
    
#     discord_login(token=token)

#     try:
#         # while receivingThread.is_alive() and sendingThread.is_alive():
#         while sendingThread.is_alive():
#             continue
        
#     except KeyboardInterrupt:
#         print(f"\nAborted")
#         threadFlag = False
#         exit(1)
    
#     threadFlag = False
    
#     clientSocket.close()
#     print(f"\nClosed application")
    

# threadFlag = True

# if __name__ == "__main__":
#     main()
#     pass

scapi_bot.run()
bot.run(token)
CommandThread = threading.Thread(target=Commands)
CommandThread.start()