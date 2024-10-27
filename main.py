import discord
from discord.ext import commands
from discord import app_commands
import aiosqlite
import dotenv
from dotenv import load_dotenv
import os
import io
from lxml import etree
from collections import defaultdict
from datetime import datetime
from itertools import groupby
import logging

load_dotenv()

intents = discord.Intents.all()

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

class MyBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(command_prefix='!wc', intents=intents)
    
    async def setup_hook(self) -> None:
        await self.load_extension('sync')
        await self.load_extension('ext')
        for filename in os.listdir('cogs'):
            if filename.endswith('.py'):
                cog_name = filename[:-3]  # Remove the .py extension
                await bot.load_extension(f'cogs.{cog_name}')

    async def on_ready(self) -> None:
        print(f'Logged in as {self.user.name} (ID: {self.user.id})')
        await bot.change_presence(activity=discord.Game(name="with words"), status=discord.Status.idle)

bot = MyBot()

API_TOKEN = str(os.getenv('API_TOKEN'))

bot.run(API_TOKEN, log_handler=handler, log_level=logging.ERROR)