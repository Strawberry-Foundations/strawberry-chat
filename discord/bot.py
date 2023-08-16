import discord
import asyncio
import configparser
from datetime import datetime
import yaml
from yaml import SafeLoader
from discord.ext import commands

with open("config.yml", encoding="utf-8") as config:
        conf = yaml.load(config, Loader=SafeLoader)

bot = commands.Bot(command_prefix='.',intents=discord.Intents.all())

class DiscordBot(bot):
    def start_bot(self):
        try:
            self.run(conf["bot"]["token"])
            
        except discord.errors.LoginFailure:
            print("Login failed")
            
    async def on_ready(self):
        print("Logged in")

    async def on_message(self, message, edited=False):
        pass