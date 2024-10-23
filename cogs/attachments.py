import discord
from discord.ext import commands
from discord import app_commands
import aiosqlite
import itertools

class Attachments(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        print('Attachments cog loaded')

    async def cog_load(self) -> None:
        pass

async def setup(bot) -> None:
    await bot.add_cog(Attachments(bot))