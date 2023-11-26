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

import webhook

with open("config.yml", encoding="utf-8") as config_file:
    config = yaml.load(config_file, Loader=SafeLoader)

log_channel_id  = config["bot"]["channel_id"]
token           = config["bot"]["token"]

stbchat_uname   = config["stbchat"]["username"]
stbchat_token   = config["stbchat"]["password"]
stbchat_host    = config["stbchat"]["server"]["host"]
stbchat_port    = config["stbchat"]["server"]["port"]

bot = commands.Bot(command_prefix='.', intents=discord.Intents.all())
scapi_bot = Scapi.Bot(username=stbchat_uname, token=stbchat_token, host=stbchat_host, port=stbchat_port, json=True)

scapi_bot.login()
scapi_bot.flag_handler(print_recv_msg=False, enable_user_input=True)


def escape_ansi(line):
    ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', line)

@bot.event
async def on_ready():
    scapi_bot.logger(f'(Discord) Logged in as {bot.user.name}', type=Scapi.LogLevel.INFO)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        pass
    
    elif message.webhook_id is not None:
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
                    
        except Exception as e:
            print(e)
        
    await bot.process_commands(message)

_webhook = threading.Thread(target=webhook.main)
_webhook.start()
    
scapi_bot.run()
bot.run(token)