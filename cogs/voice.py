import discord
import asyncio
from discord.ext import commands
import sqlite3


class voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        conn = sqlite3.connect("voice.db")
        c = conn.cursor()
        guildID = member.guild.id
        c.execute("SELECT voiceChannelID FROM guild WHERE guildID = ?", (guildID,))
        voice = c.fetchone()
        if voice:
            voiceID = voice[0]
            try:
                if after.channel.id == voiceID:
                    c.execute(
                        "SELECT * FROM voiceChannel WHERE userID = ?", (member.id,)
                    )
                    cooldown = c.fetchone()
                    if cooldown:
                        await member.send(
                            "Creating channels too quickly you've been put on a 15 second cooldown!"
                        )
                        await asyncio.sleep(15)
                    c.execute(
                        "SELECT voiceCategoryID FROM guild WHERE guildID = ?",
                        (guildID,),
                    )
                    voice = c.fetchone()
                    c.execute(
                        "SELECT channelName, channelLimit FROM userSettings WHERE userID = ?",
                        (member.id,),
                    )
                    setting = c.fetchone()
                    c.execute(
                        "SELECT channelLimit FROM guildSettings WHERE guildID = ?",
                        (guildID,),
                    )
                    guildSetting = c.fetchone()
                    if setting:
                        name = setting[0]
                        if guildSetting and setting[1] == 0:
                            limit = guildSetting[0]
                        else:
                            limit = setting[1]
                    else:
                        name = f"{member.name}'s channel"
                        limit = guildSetting[0] if guildSetting else 0
                    categoryID = voice[0]
                    category = self.bot.get_channel(categoryID)
                    channel2 = await member.guild.create_voice_channel(
                        name, category=category
                    )
                    channelID = channel2.id
                    await member.move_to(channel2)
                    await channel2.set_permissions(
                        self.bot.user, connect=True, read_messages=True
                    )
                    await channel2.edit(name=name, user_limit=limit)
                    c.execute(
                        "INSERT INTO voiceChannel VALUES (?, ?)", (member.id, channelID)
                    )
                    conn.commit()

                    def check(a, b, c):
                        return len(channel2.members) == 0

                    await self.bot.wait_for("voice_state_update", check=check)
                    await channel2.delete()
                    await asyncio.sleep(3)
                    c.execute("DELETE FROM voiceChannel WHERE userID=?", (member.id,))
            except:
                pass
        conn.commit()
        conn.close()

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        print(error)
        if isinstance(error, commands.MissingPermissions):
            await ctx.channel.send(
                f"{ctx.author.mention} only the admin of the server can setup the bot!"
            )

    @commands.group(aliases=["v"])
    async def voice(self, ctx):
        pass

    @voice.command()
    @commands.has_permissions(administrator=True)
    async def setup(self, ctx):
        conn = sqlite3.connect("voice.db")
        c = conn.cursor()
        guildID = ctx.guild.id
        authorID = ctx.author.id

        def check(m):
            return m.author.id == authorID

        await ctx.channel.send("**You have 60 seconds to answer each question!**")
        await ctx.channel.send(
            f"**Enter the name of the category you wish to create the channels in:(e.g Voice Channels)**"
        )
        try:
            category = await self.bot.wait_for("message", check=check, timeout=60.0)
        except asyncio.TimeoutError:
            await ctx.channel.send("Took too long to answer!")
        else:
            new_cat = await ctx.guild.create_category_channel(category.content)
            await ctx.channel.send(
                "**Enter the name of the voice channel: (e.g Join To Create)**"
            )
            try:
                channel = await self.bot.wait_for("message", check=check, timeout=60.0)
            except asyncio.TimeoutError:
                await ctx.channel.send("Took too long to answer!")
            else:
                try:
                    channel = await ctx.guild.create_voice_channel(
                        channel.content, category=new_cat
                    )
                    c.execute(
                        "SELECT * FROM guild WHERE guildID = ? AND ownerID=?",
                        (guildID, authorID),
                    )
                    voice = c.fetchone()
                    if voice:
                        c.execute(
                            "UPDATE guild SET guildID = ?, ownerID = ?, voiceChannelID = ?, voiceCategoryID = ? WHERE guildID = ?",
                            (guildID, authorID, channel.id, new_cat.id, guildID),
                        )
                    else:
                        c.execute(
                            "INSERT INTO guild VALUES (?, ?, ?, ?)",
                            (guildID, authorID, channel.id, new_cat.id),
                        )
                    await ctx.channel.send("**You are all setup and ready to go!**")
                except:
                    await ctx.channel.send(
                        "You didn't enter the names properly.\nUse `.voice setup` again!"
                    )
        conn.commit()
        conn.close()

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setlimit(self, ctx, num):
        conn = sqlite3.connect("voice.db")
        c = conn.cursor()
        c.execute("SELECT * FROM guildSettings WHERE guildID = ?", (ctx.guild.id,))
        voice = c.fetchone()
        if voice:
            c.execute(
                "UPDATE guildSettings SET channelLimit = ? WHERE guildID = ?",
                (num, ctx.guild.id),
            )
        else:
            c.execute(
                "INSERT INTO guildSettings VALUES (?, ?, ?)",
                (ctx.guild.id, f"{ctx.author.name}'s channel", num),
            )
        await ctx.send("You have changed the default channel limit for your server!")
        conn.commit()
        conn.close()

    @voice.command()
    async def lock(self, ctx):
        conn = sqlite3.connect("voice.db")
        c = conn.cursor()
        author = ctx.author
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (author.id,))
        voice = c.fetchone()
        if voice:
            channelID = voice[0]
            role = ctx.guild.default_role
            channel = self.bot.get_channel(channelID)
            await channel.set_permissions(role, connect=False)
            await ctx.channel.send(f"{author.mention} Voice chat locked! 🔒")
        else:
            await ctx.channel.send(f"{author.mention} You don't own a channel.")
        conn.commit()
        conn.close()

    @voice.command()
    async def unlock(self, ctx):
        conn = sqlite3.connect("voice.db")
        c = conn.cursor()
        author = ctx.author
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (author.id,))
        voice = c.fetchone()
        if voice:
            channelID = voice[0]
            role = ctx.guild.default_role
            channel = self.bot.get_channel(channelID)
            await channel.set_permissions(role, connect=True)
            await ctx.channel.send(f"{author.mention} Voice chat unlocked! 🔓")
        else:
            await ctx.channel.send(f"{author.mention} You don't own a channel.")
        conn.commit()
        conn.close()

    @voice.command(aliases=["permit"])
    async def allow(self, ctx, member: discord.Member):
        conn = sqlite3.connect("voice.db")
        c = conn.cursor()
        author = ctx.author
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (author.id,))
        voice = c.fetchone()
        if voice:
            channelID = voice[0]
            channel = self.bot.get_channel(channelID)
            await channel.set_permissions(member, connect=True)
            await ctx.channel.send(
                f"{author.mention} You have permited {member.name} to have access to the channel. ✅"
            )
        else:
            await ctx.channel.send(f"{author.mention} You don't own a channel.")
        conn.commit()
        conn.close()

    @voice.command(aliases=["reject"])
    async def deny(self, ctx, member: discord.Member):
        conn = sqlite3.connect("voice.db")
        c = conn.cursor()
        author = ctx.author
        guildID = ctx.guild.id
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (author.id,))
        voice = c.fetchone()
        if voice:
            channelID = voice[0]
            channel = self.bot.get_channel(channelID)
            for members in channel.members:
                if members.id == member.id:
                    c.execute(
                        "SELECT voiceChannelID FROM guild WHERE guildID = ?", (guildID,)
                    )
                    voice = c.fetchone()
                    channel2 = self.bot.get_channel(voice[0])
                    await member.move_to(channel2)
            await channel.set_permissions(member, connect=False, read_messages=True)
            await ctx.channel.send(
                f"{author.mention} You have rejected {member.name} from accessing the channel. ❌"
            )
        else:
            await ctx.channel.send(f"{author.mention} You don't own a channel.")
        conn.commit()
        conn.close()

    @voice.command()
    async def limit(self, ctx, limit):
        conn = sqlite3.connect("voice.db")
        c = conn.cursor()
        author = ctx.author
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (author.id,))
        voice = c.fetchone()
        if voice:
            channelID = voice[0]
            channel = self.bot.get_channel(channelID)
            await channel.edit(user_limit=limit)
            await ctx.channel.send(
                f"{author.mention} You have set the channel limit to be "
                + "{}!".format(limit)
            )
            c.execute(
                "SELECT channelName FROM userSettings WHERE userID = ?", (author.id,)
            )
            voice = c.fetchone()
            if voice:
                c.execute(
                    "UPDATE userSettings SET channelLimit = ? WHERE userID = ?",
                    (limit, author.id),
                )
            else:
                c.execute(
                    "INSERT INTO userSettings VALUES (?, ?, ?)",
                    (author.id, author.name, limit),
                )
        else:
            await ctx.channel.send(f"{author.mention} You don't own a channel.")
        conn.commit()
        conn.close()

    @voice.command()
    async def name(self, ctx, *, name):
        conn = sqlite3.connect("voice.db")
        c = conn.cursor()
        author = ctx.author
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (author.id,))
        voice = c.fetchone()
        if voice:
            channelID = voice[0]
            channel = self.bot.get_channel(channelID)
            await channel.edit(name=name)
            await ctx.channel.send(
                f"{author.mention} You have changed the channel name to "
                + "{}!".format(name)
            )
            c.execute(
                "SELECT channelName FROM userSettings WHERE userID = ?", (author.id,)
            )
            voice = c.fetchone()
            if voice:
                c.execute(
                    "UPDATE userSettings SET channelName = ? WHERE userID = ?",
                    (name, author.id),
                )
            else:
                c.execute(
                    "INSERT INTO userSettings VALUES (?, ?, ?)", (author.id, name, 0)
                )
        else:
            await ctx.channel.send(f"{author.mention} You don't own a channel.")
        conn.commit()
        conn.close()

    @voice.command()
    async def claim(self, ctx):
        author = ctx.author
        x = True
        conn = sqlite3.connect("voice.db")
        c = conn.cursor()
        channel = author.voice.channel
        if channel:
            c.execute(
                "SELECT userID FROM voiceChannel WHERE voiceID = ?", (channel.id,)
            )
            voice = c.fetchone()
            if voice:
                for data in channel.members:
                    if data.id == voice[0]:
                        owner = ctx.guild.get_member(voice[0])
                        await ctx.channel.send(
                            f"{author.mention} This channel is already owned by {owner.mention}!"
                        )
                        x = False
                if x:
                    await ctx.channel.send(
                        f"{author.mention} You are now the owner of the channel!"
                    )
                    c.execute(
                        "UPDATE voiceChannel SET userID = ? WHERE voiceID = ?",
                        (author.id, channel.id),
                    )
            else:
                await ctx.channel.send(f"{author.mention} You can't own that channel!")
        else:
            await ctx.channel.send(f"{author.mention} you're not in a voice channel.")
        conn.commit()
        conn.close()


def setup(bot):
    bot.add_cog(voice(bot))
