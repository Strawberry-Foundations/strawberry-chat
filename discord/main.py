import threading
import asyncio
import re
from bot import DiscordBot
from stbchat import ChatClient

async def stbc_to_discord(self, message):
    channel_id = int(conf["bot"]["channel_id"])
    channel = dbot.get_channel(channel_id)
    asyncio.run_coroutine_threadsafe(channel.send(message), bot_loop)

async def discord_to_stbc(self, message):
    if not message.channel.id == int(conf["bot"]["channel_id"]):
        return
    
    sender = message.author.nick if message.author.nick != None else message.author.name

    stbchat.send_msg(f"{sender}: {message}")


ChatClient.react_on_message = stbc_to_discord
DiscordBot.on_message = discord_to_stbc

global bot_loop
bot_loop = asyncio.new_event_loop()
stbchat = ChatClient()
dbot = DiscordBot(loop=bot_loop)

global conf
conf = stbchat.reload_conf()
    
dbot.start_bot()