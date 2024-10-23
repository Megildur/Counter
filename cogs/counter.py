import discord
from discord.ext import commands
from discord import app_commands
import aiosqlite

class Counter(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.ctx_menu = app_commands.ContextMenu(name='Message Word Count', callback=self.message_word_count)
        self.ctx_menu2 = app_commands.ContextMenu(name='User Word Count', callback=self.user_word_count)
        print('Counter cog loaded')
        self.bot.tree.add_command(self.ctx_menu)
        self.bot.tree.add_command(self.ctx_menu2)

    async def cog_unload(self) -> None:
        self.bot.tree.remove_command(self.ctx_menu.name, type=self.ctx_menu.type)
        self.bot.tree.remove_command(self.ctx_menu2.name, type=self.ctx_menu2.type)

    async def message_word_count(self, interaction: discord.Interaction, message: discord.Message) -> None:
        async with aiosqlite.connect('channels.db') as db:
            cursor = await db.execute('SELECT * FROM channels WHERE guild_id = ?', (interaction.guild_id,))
            result = await cursor.fetchone()
            if not result:
                embed = discord.Embed(title='Error', description='Word count is not being recorded for this server!', color=discord.Color.red())
                await interaction.response.send_message(embed=embed)
                return
        if message.author.bot:
            embed = discord.Embed(title='Error', description='Bots cannot have word counts!', color=discord.Color.red())
            await interaction.response.send_message(embed=embed)
            return
        words = len(message.content.split())
        embed = discord.Embed(title='Word Count', description=f'{message.author.mention} has said {words} words in this message', color=discord.Color.from_str('#af2202'))
        await interaction.response.send_message(embed=embed)

    async def user_word_count(self, interaction: discord.Interaction, user: discord.Member) -> None:
        async with aiosqlite.connect('channels.db') as db:
            cursor = await db.execute('SELECT * FROM channels WHERE guild_id = ?', (interaction.guild_id,))
            result = await cursor.fetchone()
            if not result:
                embed = discord.Embed(title='Error', description='Word count is not being recorded for this server!', color=discord.Color.red())
                await interaction.response.send_message(embed=embed)
                return
        if user.bot:
            embed = discord.Embed(title='Error', description='Bots cannot have word counts!', color=discord.Color.red())
            await interaction.response.send_message(embed=embed)
            return
        async with aiosqlite.connect('server.db') as db:
            async with db.execute('SELECT count FROM server WHERE user_id = ? and guild_id = ?', (user.id, interaction.guild_id)) as cursor:
                result = await cursor.fetchone()
                if result is None:
                    await db.execute('INSERT INTO server (user_id, guild_id, count) VALUES (?, ?, ?)', (user.id, interaction.guild_id, 0))
                    await db.commit()
                    embed = discord.Embed(title='Word Count', description=f'{user.mention} has said 0 words in {interaction.guild.name}', color=discord.Color.from_str('#af2202'))
                else:
                    embed = discord.Embed(title='Word Count', description=f'{user.mention} has said {result[0]} words in {interaction.guild.name}', color=discord.Color.from_str('#af2202'))
                await interaction.response.send_message(embed=embed)

    async def cog_load(self) -> None:
        async with aiosqlite.connect('counter.db') as db:
            await db.execute('''CREATE TABLE IF NOT EXISTS counters (
                guild_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                count INTEGER NOT NULL,
                PRIMARY KEY (guild_id, user_id, channel_id)
                )'''
            )
            await db.commit()

        async with aiosqlite.connect('channels.db') as db:
            await db.execute('''CREATE TABLE IF NOT EXISTS channels (
                guild_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                PRIMARY KEY (guild_id, channel_id)
                )'''
            )
            await db.commit()
        
        async with aiosqlite.connect('server.db') as db:
            await db.execute('''CREATE TABLE IF NOT EXISTS server (
                guild_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                count INTEGER NOT NULL,
                PRIMARY KEY (guild_id, user_id)
                )'''
            )
            await db.commit()

        async with aiosqlite.connect('ignore.db') as db:
            await db.execute('''CREATE TABLE IF NOT EXISTS ignore (
                guild_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                PRIMARY KEY (guild_id, channel_id)
                )'''
            )
            await db.commit()
    
    @commands.Cog.listener()
    async def on_message(self, message) -> None:
        if message.author.bot:
            return
        async with aiosqlite.connect('ignore.db') as db:
            async with db.execute('SELECT channel_id FROM ignore WHERE guild_id = ?', (message.guild.id,)) as cursor:
                iresult = await cursor.fetchall()
                for row in iresult:
                    if message.channel.id in row:
                        return
        async with aiosqlite.connect('channels.db') as db:
            async with db.execute('SELECT channel_id FROM channels WHERE guild_id = ?', (message.guild.id,)) as cursor:
                result = await cursor.fetchall()
        if not result:
            return
        else:
            for channel_id in result:
                if message.channel.type != discord.ChannelType.public_thread:
                    if 1 in channel_id or message.channel.id in channel_id:
                        word_count = len(message.content.split())
                        await self.update_count(message.guild, message.author, message.channel.id, word_count)
                else:
                    if 1 in channel_id or message.channel.parent_id in channel_id:
                        word_count = len(message.content.split())
                        await self.update_count(message.guild, message.author, message.channel.parent_id, word_count)

    @commands.Cog.listener()
    async def on_message_delete(self, message) -> None:
        if message.author.bot:
            return
        async with aiosqlite.connect('ignore.db') as db:
            async with db.execute('SELECT channel_id FROM ignore WHERE guild_id = ?', (message.guild.id,)) as cursor:
                iresult = await cursor.fetchall()
                for row in iresult:
                    if message.channel.id in row:
                        return
        async with aiosqlite.connect('channels.db') as db:
            async with db.execute('SELECT channel_id FROM channels WHERE guild_id = ?', (message.guild.id,)) as cursor:
                result = await cursor.fetchall()
        if not result:
            return
        else:
            for channel_id in result:
                if message.channel.type != discord.ChannelType.public_thread:
                    if 1 in channel_id or message.channel.id in channel_id:
                        word_count = len(message.content.split())
                        await self.remove_count(message.guild, message.author, message.channel.id, word_count)
                else:
                    if 1 in channel_id or message.channel.parent_id in channel_id:
                        word_count = len(message.content.split())
                        await self.remove_count(message.guild, message.author, message.channel.parent_id, word_count)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after) -> None:
        if before.author.bot:
            return
        async with aiosqlite.connect('ignore.db') as db:
            async with db.execute('SELECT channel_id FROM ignore WHERE guild_id = ?', (before.guild.id,)) as cursor:
                iresult = await cursor.fetchall()
                for row in iresult:
                    if before.channel.id in row:
                        return
        async with aiosqlite.connect('channels.db') as db:
            async with db.execute('SELECT channel_id FROM channels WHERE guild_id = ?', (before.guild.id,)) as cursor:
                result = await cursor.fetchall()
        if not result:
            return
        else:
            for channel_id in result:
                if before.channel.type != discord.ChannelType.public_thread:
                    if 1 in channel_id or before.channel.id in channel_id:
                        old_msg_count = len(before.content.split())
                        new_msg_count = len(after.content.split())
                        await self.find_dif(before.guild, before.author, before.channel.id, old_msg_count, new_msg_count)
                else:
                    if 1 in channel_id or before.channel.parent_id in channel_id:
                        old_msg_count = len(before.content.split())
                        new_msg_count = len(after.content.split())
                        await self.find_dif(before.guild, before.author, before.cannel.parent_id, old_msg_count, new_msg_count)

    async def find_dif(self, guild, user, channel_id, old_msg_count, new_msg_count) -> None:
        if old_msg_count > new_msg_count:
            count = old_msg_count - new_msg_count
            await self.remove_count(guild, user, channel_id, count)
        elif old_msg_count < new_msg_count:
            count = new_msg_count - old_msg_count
            await self.update_count(guild, user, channel_id, count)
        elif old_msg_count == new_msg_count:
            return

    async def update_count(self, guild, user, channel_id, count) -> None:
        async with aiosqlite.connect('counter.db') as db:
            async with db.execute('SELECT count FROM counters WHERE guild_id = ? AND user_id = ? AND channel_id = ?', (guild.id, user.id, channel_id)) as cursor:
                result = await cursor.fetchone()
            if result is None:
                await db.execute('INSERT INTO counters (guild_id, user_id, channel_id, count) VALUES (?, ?, ?, ?)', (guild.id, user.id, channel_id, count))
            else:
                await db.execute('UPDATE counters SET count = ? WHERE guild_id = ? AND user_id = ? AND channel_id = ?', (result[0] + count, guild.id, user.id, channel_id))
            await db.commit()
        async with aiosqlite.connect('server.db') as db:
            async with db.execute('SELECT count FROM server WHERE guild_id = ? AND user_id = ?', (guild.id, user.id)) as cursor:
                result = await cursor.fetchone()
            if result is None:
                await db.execute('INSERT INTO server (guild_id, user_id, count) VALUES (?, ?, ?)', (guild.id, user.id, count))
            else:
                await db.execute('UPDATE server SET count = ? WHERE guild_id = ? AND user_id = ?', (result[0] + count, guild.id, user.id))
            await db.commit()

    async def remove_count(self, guild, user, channel_id, count) -> None:
        async with aiosqlite.connect('counter.db') as db:
            async with db.execute('SELECT count FROM counters WHERE guild_id = ? AND user_id = ? AND channel_id = ?', (guild.id, user.id, channel.id)) as cursor:
                result = await cursor.fetchone()
            if result is None:
                return
            else:
                await db.execute('UPDATE counters SET count = ? WHERE guild_id = ? AND user_id = ? AND channel_id = ?', (result[0] - count, guild.id, user.id, channel_id))
            await db.commit()
        async with aiosqlite.connect('server.db') as db:
            async with db.execute('SELECT count FROM server WHERE guild_id = ? AND user_id = ?', (guild.id, user.id)) as cursor:
                result = await cursor.fetchone()
            if result is None:
                return
            else:
                await db.execute('UPDATE server SET count = ? WHERE guild_id = ? AND user_id = ?', (result[0] - count, guild.id, user.id))
            await db.commit()

async def setup(bot) -> None:
    await bot.add_cog(Counter(bot))