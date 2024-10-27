import discord
from discord.ext import commands
from typing import Literal

class Extensions(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def ext(self, ctx: commands.Context, action: Literal["load", "unload", "reload"], *, extension: str) -> None:
        if action == "load":
            try:
                await self.bot.load_extension(extension)
            except commands.ExtensionAlreadyLoaded:
                await ctx.send(f"Extension {extension} is already loaded.")
            except commands.ExtensionNotFound:
                await ctx.send("Extension not found.")
            except commands.ExtensionFailed:
                await ctx.send("Extension failed to load.")
            else:
                await ctx.send(f'Loaded extension "{extension}".')
        elif action == "unload":
            try:
                await self.bot.unload_extension(extension)
            except commands.ExtensionNotLoaded:
                await ctx.send(f"Extension {extension} is not loaded.")
            else:
                await ctx.send(f'Unloaded extension "{extension}".')
        elif action == "reload":
            try:
                await self.bot.reload_extension(extension)
            except commands.ExtensionNotLoaded:
                await ctx.send(f"Extension {extension} is not loaded.")
            except commands.ExtensionNotFound:
                await ctx.send("Extension not found.")
            except commands.ExtensionFailed:
                await ctx.send("Extension failed to load.")
            else:
                await ctx.send(f'Reloaded extension "{extension}".')

async def setup(bot) -> None:
    await bot.add_cog(Extensions(bot))
    print(f'Extensions cog loaded')