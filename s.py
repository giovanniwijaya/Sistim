import aiohttp
import asyncio
import bs4
import csv
import json
import os
import psutil
import pytz
import textwrap
from discord import *
from secrets import *
from datetime import datetime as dt, timedelta
from discord.ext import commands
from geopy.distance import distance
from urllib.parse import quote


def jl(f, s=0):
    with open("" if s else "s_" + f + ".json", "r") as p:
        return json.load(p)


def jd(c, f, s=0):
    with open("" if s else "s_" + f + ".json", "w") as p:
        json.dump(c, p)


def dl(e):
    d = e.days
    m, s = divmod(e.seconds, 60)
    h, m = divmod(m, 60)
    f, w, x, y, z = (
        "",
        "" if d == 1 else "s",
        "" if h == 1 else "s",
        "" if m == 1 else "s",
        "" if s == 1 else "s",
    )
    if d:
        if h or m:
            w += ", "
        elif s:
            w += " and "
        f += f"{d} day{w}"
    if h:
        if m:
            x += ", "
        elif s:
            x += " and "
        f += f"{h} hour{x}"
    if m:
        if s:
            if d or h:
                y += ","
            y += " and "
        f += f"{m} minute{y}"
    if s:
        f += f"{s} second{z}"
    return f


def ds(e):
    if e.total_seconds() < 0:
        return "Arr"
    m, s = divmod(e.seconds, 60)
    h, m = divmod(m, 60)
    f = ""
    if h:
        f += f"{h}h "
    if m:
        f += f"{m}m "
    if s:
        f += f"{s}s"
    return f


def tc(n):
    n = n.casefold()
    if all(x not in n for x in ["d", "h", "m", "s"]):
        raise ValueError
    if "d" in n:
        y, n = n.split("d", maxsplit=1)
        y = int(y)
    else:
        y = 0
    if "h" in n:
        h, n = n.split("h", maxsplit=1)
        h = int(h)
    else:
        h = 0
    if "m" in n:
        u, n = n.split("m", maxsplit=1)
        u = int(u)
    else:
        u = 0
    if "s" in n:
        s, n = n.split("s", maxsplit=1)
        s = int(s)
    else:
        s = 0
    return timedelta(days=y, hours=h, minutes=u, seconds=s)


def sh(l, x=2048):
    m, n = [l], [0]
    for i in range(round(len(l) / x)):
        try:
            if len(l) > n[i] + x:
                n.append(l[: n[i] + x].rfind("\n"))
                m[i] = l[n[i] : n[i + 1]]
                m.append(l[n[i + 1] :])
        except IndexError:
            return m


def sp(s):
    return [
        n
        for n in list(csv.reader(open("stops.csv", "r")))
        if s.casefold() == n[0].casefold()
    ][0]


i = [
    "welcome_message",
    "goodbye_message",
    "member_join",
    "member_remove",
    "member_ban",
    "member_unban",
    "member_roles",
    "member_nickname",
    "member_status",
    "member_verification",
    "user_avatar",
    "user_name",
    "user_discriminator",
    "role_create",
    "role_delete",
    "role_permissions",
    "role_name",
    "role_hoist",
    "role_mentionable",
    "role_order",
    "role_color",
    "reaction_add",
    "reaction_remove",
    "message_delete",
    "message_edit",
]
a = [
    "wm",
    "gm",
    "mj",
    "mr",
    "mb",
    "mu",
    "mo",
    "mn",
    "ms",
    "mv",
    "ua",
    "un",
    "ud",
    "rc",
    "rd",
    "rp",
    "rn",
    "rh",
    "rm",
    "ro",
    "rl",
    "ra",
    "rr",
    "md",
    "me",
]
up, cf = dt.now(), jl("c")
cf["status"] = "on"
jd(cf, "c")


async def gt(u, h=None, p=None, f=0):
    async with aiohttp.ClientSession() as c:
        async with c.get(url=u, headers=h, params=p) as r:
            if r.status == 200:
                return await r.json() if f else await r.text()


def pr(b, m):
    x = jl(f"n{m.guild.id}")["pp"] if m.guild else "+"
    return commands.when_mentioned_or(x)(b, m)


b = commands.AutoShardedBot(
    command_prefix=pr, case_insensitive=True, help_command=None, intents=Intents.all()
)


@b.event
async def on_ready():
    print(b.user.name)


@b.event
async def on_command_error(t, e):
    if isinstance(e, (commands.MissingRequiredArgument, commands.BadArgument)):
        await help.__call__(t, z=t.command.qualified_name)
    if isinstance(e, commands.NoPrivateMessage):
        await t.send("Command only works in guilds")
    if isinstance(e, commands.PrivateMessageOnly):
        await t.send("Command only works in private message")
    if isinstance(e, commands.MissingPermissions):
        await t.send("You don’t have the permissions")
    if isinstance(e, commands.BotMissingPermissions):
        await t.send("I don’t have the permissions")
    if isinstance(e, commands.DisabledCommand):
        await t.send("Command is temporarily unavailable")
    raise e


@b.command()
@commands.is_owner()
async def load(t, s):
    b.load_extension(f"cogs.{s}")


@b.command()
@commands.is_owner()
async def unload(t, s):
    b.unload_extension(f"cogs.{s}")


@b.command()
@commands.is_owner()
async def reload(t, s):
    b.unload_extension(f"cogs.{s}")
    b.load_extension(f"cogs.{s}")


for fn in os.listdir("./cogs"):
    if fn.endswith(".py"):
        b.load_extension(f"cogs.{fn[:-3]}")


@b.command(aliases=["h"])
async def help(t, *, z=""):
    p = jl(f"n{t.guild.id}")["pp"] if t.guild else "+"
    if z in ["prefix", "pr"]:
        await t.send(
            f"""The syntax is `{p}prefix [prefix]`
You send prefix, I make that my prefix here
Leave prefix blank to check current prefix
Only works in guilds
Aliases: `pr`"""
        )
    elif z in ["welcome", "w"]:
        await t.send(
            f"""The syntax is `{p}welcome [message]`
You send message, I make that my welcome message here
Leave message blank for default message, type """
            + "{member}"
            + """ to mention the joining member
Only works in guilds
Aliases: `w`"""
        )
    elif z in ["goodbye", "g"]:
        await t.send(
            f"""The syntax is `{p}goodbye [message]`
You send message, I make that my goodbye message here
Leave message blank for default message, type """
            + "{member}"
            + """ to mention the leaving member
Only works in guilds
Aliases: `g`"""
        )
    elif z in ["purge", "p", "clear", "c"]:
        await t.send(
            f"""The syntax is `{p}purge [number]`
You send number, I delete that many messages
Only works in guilds
Aliases: `p` | `clear` | `c`"""
        )
    elif z in ["role", "r"]:
        await t.send(
            f"""The syntax is `{p}role [message ID]`
You send the message ID, then specify emojis and roles; you react to the message, I give you the corresponding role
Leave message ID blank for your next message after the reaction role assignments
Only works in guilds
Aliases: `r`"""
        )
    elif z in ["schedule", "s", "sc"]:
        await t.send(
            f"""The syntax is `{p}schedule [event]`
You name an event and the time in UTC (`dd/mm/yyyy hh:mm:ss`), then I remind you periodically up to the time of event
You can optionally set custom reminder timings (`[days]d [hours]h [minutes]m [seconds]s`), or use the default values of 1 day, 1 hour, and 5 minutes before
Usage example:
```{p}schedule send breakup text
20/04/2022 11:11:11
1d
1h 15m
10s```
Aliases: `s` | `sc`"""
        )
    elif z in ["remind", "re"]:
        await t.send(
            f"""The syntax is `{p}remind [event]`
You name an event, I ask for amount of time (`[days]d [hours]h [minutes]m [seconds]s`), then I remind you once the time has elapsed
Usage example:
```{p}remind check the fridge
5m```
Aliases: `re`"""
        )
    elif z in ["event", "e", "ev"]:
        await t.send(
            f"""The syntax is `{p}event [time]`
You pick the time, I show you all scheduled events from `{p}schedule` and `{p}event`
Time choices: `past` `p` | `future` `f` | `all` `a`
Defaults to `all` option
Aliases: `e` | `ev`"""
        )
    elif z in ["kick", "k"]:
        await t.send(
            f"""The syntax is `{p}kick [user] [reason]`
You mention user and (optionally) reason, I kick them
Only works in guilds
Kick member permission needs to be enabled
Aliases: `k`"""
        )
    elif z in ["ban", "b"]:
        await t.send(
            f"""The syntax is `{p}ban [user] [reason]`
You mention user and (optionally) reason, I ban them
Only works in guilds
Ban member permission needs to be enabled
Aliases: `b`"""
        )
    elif z in ["unban", "u"]:
        await t.send(
            f"""The syntax is `{p}unban [user] [reason]`
You send user ID or name#discriminator and (optionally) reason, I unban them
Only works in guilds
Ban member permission needs to be enabled
Aliases: `u`"""
        )
    elif z in ["notify", "n", "log"]:
        await t.send(
            f"""The syntax is `{p}notify [type] [channel]`
You send type of updates and mention channel to send notifications to, I send messages
Leave channel blank to check current channel, set channel to `disable` or `d` to disable notifications
Leave both type and channel blank to check the channels for each notification type in the guild
Available types:
`welcome_message` `wm`
`goodbye_message` `gm`
`member_join` `mj`
`member_remove` `mr`
`member_ban` `mb`
`member_unban` `mu`
`member_roles` `mo`
`member_nickname` `mn`
`member_status` `ms`
`member_verification` `mv`
`user_avatar` `ua`
`user_name` `un`
`user_discriminator` `ud`
`role_create` `rc`
`role_delete` `rd`
`role_permissions` `rp`
`role_name` `rn`
`role_hoist` `rh`
`role_mentionable` `rm`
`role_order` `ro`
`role_color` `rl`
`reaction_add` `ra`
`reaction_remove` `rr`
`message_delete` `md`
`message_edit` `me`
Only works in guilds
Aliases: `n` `log`"""
        )
    elif z in ["voice", "v"]:
        await t.send(
            embed=Embed(
                title="Voice help",
                description="",
                color=0xF8786B,
                url="https://github.com/SamSanai/VoiceMaster-Discord-Bot",
            )
            .add_field(name="Lock your channel", value=f"`{p}voice lock`", inline=False)
            .add_field(
                name="Unlock your channel", value=f"`{p}voice unlock`", inline=False
            )
            .add_field(
                name="Change your channel name",
                value=f"`{p}voice name [name]`\n**Example:** `{p}voice name EU 5kd+`",
                inline=False,
            )
            .add_field(
                name="Change your channel limit",
                value=f"`{p}voice limit [number]` \n**Example:** `{p}voice limit 2`",
                inline=False,
            )
            .add_field(
                name="Give users permission to join",
                value=f"`{p}voice permit [member]`\n**Example:** `{p}voice permit @Sam#9452`",
                inline=False,
            )
            .add_field(
                name="Claim ownership of channel once the owner has left",
                value=f"`{p}voice claim`",
                inline=False,
            )
            .add_field(
                name="Remove permission and the user from your channel",
                value=f"`{p}voice reject [user]`\n**Example:** `{p}voice reject @Sam#9452`",
                inline=False,
            )
            .set_footer(
                text="Powered by SamSanai’s VoiceMaster",
                icon_url="https://avatars.githubusercontent.com/u/38131935",
            )
        )
    elif z in ["urbandictionary", "ud", "urban", "urbandict"]:
        await t.send(
            f"""The syntax is `{p}urbandictionary [word]`
You send word, I send the top Urban Dictionary definition and example
Leave word blank to get a random word’s definition and example
Aliases: `ud` | `urban` | `urbandict`"""
        )
    elif z in ["lyric", "l", "lyrics"]:
        await t.send(
            f"""The syntax is `{p}lyric [song]`
You send song, I send lyrics straight from Musixmatch
Aliases: `l` | `lyrics`
For lyrics from Genius, use `lyricg` or `lyricsg`"""
        )
    elif z in ["bus time", "bus times", "bus timings", "bus t", "bus arrival", "bus a"]:
        await t.send(
            f"""The syntax is `{p}bus time [stop]`
You send bus stop (name or code), I send the next bus timings
To get information about specific bus services only, type their numbers, separated by space, on the next line
Usage example:
```{p}bus time 84009
222 69```
Aliases: `bus t` | `bus times` | `bus timings` | `bus a` | `bus arrival`"""
        )
    elif z in ["bus route", "bus routes", "bus r"]:
        await t.send(
            f"""The syntax is `{p}bus route [number]`
You send route number, I send information about all the stops
Usage example:
```{p}bus route 69```
Aliases: `bus routes` | `bus r`"""
        )
    elif z in ["fizzbuzz", "fb"]:
        await t.send(
            f"""Oh, you don’t know how to play fizzbuzz?
I send number (starting from 1), you send the next number
But you have to send `fizz` or `buzz` or `fizzbuzz` instead if your number is a multiple of certain number(s), which I’ll tell you
The syntax is just `{p}fizzbuzz` by the way
Aliases: `fb`"""
        )
    elif z in ["cowsay", "cs"]:
        await t.send(
            f"""The syntax is `{p}cowsay [phrase]`
You send phrase, a cow will say it
Leave phrase blank to get a random fortune
Aliases: `cs`"""
        )
    elif z in ["dice", "d", "rolldice", "random"]:
        await t.send(
            f"""The syntax is `{p}dice [number]`
You send number, I send random number between 1 and that number
Aliases: `d` | `rolldice` | `random`"""
        )
    elif z in ["8ball", "8", "eightball"]:
        await t.send(
            f"""The syntax is `{p}8ball [question]`
You ask, I answer
Aliases: `8` | `eightball`"""
        )
    elif z in ["ask", "a"]:
        await t.send(
            f"""The syntax is `{p}ask [question]`
You ask, I answer
Aliases: `a`"""
        )
    elif z in ["moo"]:
        await moo.__call__(t)
    elif z in ["bus", "sgbus"]:
        await t.send(f"`{p}bus` command has been modified")
        await help.__call__(t, z="bus t")
        await help.__call__(t, z="bus r")
    else:
        await t.send(
            embed=Embed(
                title="Help",
                color=Color(0xFAE03C),
                description=f"**My prefix** here is `{p}`, in addition to mentioning me",
            )
            .set_author(
                name=t.me.name,
                url=f"https://discord.com/oauth2/authorize?client_id={t.me.id}&permissions=4294967295&scope=bot",
                icon_url=t.me.display_avatar,
            )
            .add_field(
                name="My information",
                value=f"""`{p}help` `{p}h` reveals this message
`{p}me` reveals my identity
`{p}ping` reveals my ping
`{p}stats` `{p}stat` reveals my stats (only those I’m proud of though)""",
                inline=False,
            )
            .add_field(
                name="Fun",
                value=f"""`{p}urbandictionary` `{p}ud` `{p}urbandict` shows top UrbanDictionary definition of a word*
`{p}lyric` `{p}l` `{p}lyrics` `{p}sing` shows song lyrics from Musixmatch*
`{p}fizzbuzz` `{p}fb` `{p}fizz` `{p}buzz` plays the fizzbuzz game*
`{p}hangman` `{p}hm` plays hangman
`{p}tictactoe` `{p}ttt` `{p}tic` `{p}tac` `{p}toe` plays tictactoe
`{p}cowsay` `{p}cs` makes a cow say something*
`{p}dice` `{p}d` selects a random number*
`{p}8ball` `{p}8` `{p}eightball` selects a random answer*
`{p}cram` selects a random cram""",
                inline=False,
            )
            .add_field(
                name="General utilities",
                value=f"""`{p}schedule` `{p}s` `{p}sc` reminds you of a future event*
`{p}remind` `{p}re` also reminds you of a future event*
`{p}event` `{p}e` shows all scheduled events*""",
                inline=False,
            )
            .add_field(
                name="Guild-only utilities",
                value=f"""`{p}prefix` `{p}pr` checks or changes my prefix*
`{p}welcome` `{p}w` changes my welcome message*
`{p}goodbye` `{p}g` changes my goodbye message*
`{p}purge` `{p}p` `{p}clear` `{p}c` deletes messages*
`{p}role` `{p}r` gives reaction roles*
`{p}kick` `{p}k` kicks a user*
`{p}ban` `{p}b` bans a user*
`{p}unban` `{p}u` unbans a user*
`{p}notify` `{p}n` `{p}log` adjusts update notification settings*
`{p}voice` `{p}v` [manages voice channels](https://github.com/SamSanai/VoiceMaster-Discord-Bot "powered by SamSanai’s VoiceMaster")*""",
                inline=False,
            )
            .set_footer(text=f"*Type {p}help [command] for more info")
        )


@b.command(aliases=["about"])
async def me(t):
    m = await t.send("I am ***totally*** a bot")
    await asyncio.sleep(3)
    await m.edit(
        content="I am ***totally*** a bot\n\nOr am I?\n***vsauce music plays***"
    )


@b.command(aliases=["latency"])
async def ping(t):
    await t.send(
        f'My ping is so {"slow" if b.latency>.03 else "fast"}! ({round(b.latency*1000)} ms)'
    )


@b.command(aliases=["stats"])
async def stat(t):
    a, c, e, g, y, z = (
        len(b.guilds),
        len(b.users),
        "s",
        "s",
        len([*b.get_all_channels()]),
        "s",
    )
    if a == 1:
        e = ""
    if c == 1:
        g = ""
    if y == 1:
        z = ""
    await t.send(
        embed=Embed(
            title="My stats!",
            color=Color(0x9EA450),
            description=f'I am in **{a} guild{e}** with a total of **{y} channel{z}**\nI have **{c} friend{g}**, {c} more than the owner!\nMy ping is **{round(b.latency*1000)} milliseconds**\nMy uptime is **{dl(dt.now()-up)}**\nI currently hog **{psutil.Process().memory_full_info().uss} bytes of RAM**!\n\nThis {b.user.name} has **Super Cow Powers**.\n\n**[Invite me!](https://discord.com/oauth2/authorize?client_id={t.me.id}&permissions=4294967295&scope=bot "i am very friendly")**',
            timestamp=utils.utcnow(),
        )
    )


@b.command(aliases=["pr"])
@commands.guild_only()
async def prefix(t, r=1):
    x = jl(f"n{t.guild.id}")
    if r == 1:
        await t.send(f'My prefix here is `{x["pp"]}`')
    else:
        x["pp"] = r
        jd(x, f"n{t.guild.id}")
        await t.send(f"My prefix here was changed to {r}")


@b.command(aliases=["w"])
@commands.guild_only()
@commands.has_permissions(manage_guild=True)
async def welcome(t, *, w="Welcome, {member}! Hope you enjoy it here :)"):
    m = jl(f"n{t.guild.id}")
    m["ww"] = w
    jd(m, f"n{t.guild.id}")
    if w == "Welcome, {member}! Hope you enjoy it here :)":
        w = "default message"
    await t.send(f"Welcome message in {t.guild} has been changed to {w}")


@b.command(aliases=["g"])
@commands.guild_only()
@commands.has_permissions(manage_guild=True)
async def goodbye(t, *, g="Goodbye, {member}! We ***totally*** will miss you :)"):
    m = jl(f"n{t.guild.id}")
    m["gg"] = g
    jd(m, f"n{t.guild.id}")
    if g == "Goodbye, {member}! We ***totally*** will miss you :)":
        g = "default message"
    await t.send(f"Goodbye message in {t.guild} has been changed to {g}")


@b.command(aliases=["p", "clear", "c"])
@commands.guild_only()
@commands.has_permissions(manage_messages=True)
async def purge(t, a: int):
    await t.channel.purge(limit=a + 1)
    s, h = "", "s"
    if a != 1:
        s, h = "s", "ve"
    await t.send(f"The last **{a}** message{s} ha{h} been deleted", delete_after=3)


@b.command(aliases=["r"])
@commands.guild_only()
async def role(t, l: int = 0):
    def c1(m):
        return m.author == t.author and m.channel == t.channel

    def c2(m):
        return m.author == t.author and m.guild == t.guild

    if l:
        for h in t.guild.channels:
            try:
                j = await h.fetch_message(l)
            except:
                pass
            else:
                m = j
                q = "specified"
        try:
            m.id
        except NameError:
            await t.send("Message not found")
    else:
        q = "next"
    e = await t.send(
        f"What emoji reaction in your {q} message will assign what role? Type one `[emoji],[role name]` pair on one line"
    )
    a = await b.wait_for("message", check=c1)
    el = csv.writer(open(f"s_r{t.guild.id}.csv", "a", encoding="utf-8", newline=""))
    r, c = [z.name for z in t.guild.roles], []
    for s in a.content.splitlines():
        d, f = s.split(",", maxsplit=1)
        f = f.strip()
        x = (
            utils.get(t.guild.roles, name=f)
            if f in r
            else await t.guild.create_role(name=f)
        )
        c.append([x.id, d.strip()])
    await e.edit(
        content=f"Role assignment successful, reactions in your {q} message will assign these specified roles:"
    )
    if l == 0:
        m = await b.wait_for("message", check=c2)
        l = m.id
    for d in c:
        await m.add_reaction(d[1])
        el.writerow([l] + d)


@b.command(aliases=["s", "sc"])
async def schedule(t, *, m):
    def sj(z):
        try:
            x = jl(f"l{k}")
        except FileNotFoundError:
            x = {}
        x[z.id] = [v, n, t.author.id, t.channel.id] + g
        jd(x, f"l{k}")

    m = m.splitlines()
    if len(m) < 2:
        raise commands.BadArgument
    [v, n], g = m[:2], m[2:]
    if not g:
        g = ["1d", "1h", "5m"]
    if n.isnumeric():
        d = dt.fromtimestamp(int(n))
    else:
        try:
            d = dt.strptime(n, "%d/%m/%Y %H:%M:%S")
        except ValueError:
            await t.send(
                "Invalid date or format, restart and input date and time in the correct format"
            )
            raise commands.BadArgument
        else:
            n = d.timestamp()
    k = t.guild.id if t.guild else t.author.id
    w = []
    for y in g:
        try:
            l = tc(y)
        except ValueError:
            await t.send(f"Discarding invalid time format `{y}`")
            g.remove(y)
        else:
            if l.total_seconds() > 0:
                w.append((l.total_seconds(), dl(l)))
    w.append((0,))
    da = pytz.utc.localize(d)
    n = int(da.timestamp())
    if (d - dt.utcnow()).total_seconds() > 0:
        z = await t.send(
            embed=Embed(
                title=v,
                color=Color(0x9DE7D7),
                description=f"will start **<t:{n}:R>**\n\n**Please stand by!**",
                timestamp=da,
            )
        )
        sj(z)
        j = await b.get_user(k).create_dm() if t.author.id == k else t.channel
        for q in w:
            c = (d - dt.utcnow()).total_seconds()
            if c > q[0]:
                await asyncio.sleep(c - q[0])
                z = f"in ***{q[1]}***" if q[0] else "***NOW***"
                await j.send(
                    embed=Embed(
                        title=v,
                        color=Color(0xFCAEBB),
                        description="is happening " + z,
                        timestamp=da,
                    )
                )
    else:
        z = await t.send(
            embed=Embed(
                title=v,
                color=Color(0xFFB990),
                description=f"has started **<t:{n}:R>**",
                timestamp=da,
            )
        )
        sj(z)


@b.command(aliases=["re"])
async def remind(t, *, m):
    n = m.splitlines()
    v = n[0]
    try:
        l = tc(n[1])
    except IndexError:
        await t.send("Time not specified")
        raise commands.BadArgument
    except ValueError:
        await t.send("Invalid format, restart and input time in the correct format")
        raise commands.BadArgument
    else:
        d, k = dt.utcnow() + l, t.guild.id if t.guild else t.author.id
        da = pytz.utc.localize(d)
        z = await t.send(
            embed=Embed(
                title=v,
                color=Color(0x9DE7D7),
                description=f"will start **<t:{int(da.timestamp())}:R>**\n\n**Please stand by!**",
                timestamp=da,
            )
        )
        try:
            x = jl(f"l{k}")
        except FileNotFoundError:
            x = {}
        x[z.id] = [v, d.timestamp(), t.author.id, t.channel.id, "0s"]
        jd(x, f"l{k}")
        j = await b.get_user(k).create_dm() if t.author.id == k else t.channel
        await asyncio.sleep(l.total_seconds())
        await j.send(
            embed=Embed(
                title=v,
                color=Color(0xFCAEBB),
                description="is happening ***NOW***",
                timestamp=da,
            )
        )


@b.command(aliases=["e", "ev"])
async def event(t, p="a"):
    k, m, o = t.guild.id if t.guild else t.author.id, "", dt.utcnow()
    if p in ["past", "p"]:
        e = "Past"
    elif p in ["future", "f"]:
        e = "Future"
    else:
        e = "All"
    oa = pytz.utc.localize(o)
    try:
        r = jl(f"l{k}")
    except FileNotFoundError:
        await t.send(
            embed=Embed(
                title=f"No scheduled events", color=Color(0xCDB8A0), timestamp=oa
            )
        )
    for v in r.values():
        vt = dt.fromtimestamp(int(v[1]))
        if (e != "Future" and vt <= o) or (e != "Past" and vt >= o):
            m += f"**{v[0]}** on **<t:{v[1]}:F>**"
            m += f", set by <@!{v[2]}>" if t.guild else ""
    if m:
        f, m = [], sh(m)
        for j in range(len(m)):
            f.append(
                Embed(
                    title=e + " scheduled events:",
                    color=Color(0xD2C2AC),
                    description=m[0],
                    timestamp=oa,
                )
                if j == 0
                else Embed(color=Color(0xD2C2AC), description=m[j], timestamp=oa)
            )
        await t.send(embeds=f)
    else:
        await t.send(
            embed=Embed(
                title=f"No {e.casefold()} scheduled events",
                color=Color(0xCDB8A0),
                timestamp=oa,
            )
        )


@b.command(aliases=["k"])
@commands.guild_only()
@commands.has_permissions(kick_members=True)
async def kick(t, m: Member, *, r=None):
    await m.kick(reason=r)
    if r:
        r = " for " + r
    await t.send(f"{m.mention} has been kicked{r}")


@b.command(aliases=["b"])
@commands.guild_only()
@commands.has_permissions(ban_members=True)
async def ban(t, m: Member, *, r=None):
    await m.ban(reason=r)
    if r:
        r = " for " + r
    await t.send(f"{m.mention} has been banned{r}")


@b.command(aliases=["u"])
@commands.guild_only()
@commands.has_permissions(ban_members=True)
async def unban(t, *, m):
    try:
        m, r = m.splitlines()
    except ValueError:
        r = None
    x = await t.guild.bans()
    try:
        m = int(m)
    except ValueError:
        if "#" not in m:
            await t.send("Discriminator has to be specified")
        n, d = m.split("#")
        if len(d) != 4:
            await t.send("Discriminator has to be 4 digits")
        y = utils.get(x, user__name=n, user__discriminator=d)
    else:
        y = utils.get(x, user__id=m)
    if y:
        await t.guild.unban(y.user, reason=r)
        if r:
            r = " for " + r
        await t.send(f"**{y.user.mention}** has been unbanned{r}")
    else:
        await t.send("User not found or not banned")


@b.command(aliases=["n", "log"])
@commands.guild_only()
async def notify(t, n="", *, v=""):
    n = n.casefold()
    if n in i:
        d = n[0].upper() + n[1:]
        n = a[i.index(n)]
    elif n in a:
        d = i[a.index(n)]
        d = d[0].upper() + d[1:]
    elif n != "":
        n = 0
        await t.send(
            embed=Embed(title="Invalid notification type", color=Color(0xC3447A))
        )
    m = jl(f"n{t.guild.id}")
    if n:
        if v in ["disable", "d"]:
            try:
                m.pop(n)
            except KeyError:
                x = "are disabled"
            else:
                jd(m, f"n{t.guild.id}")
                x = "have been disabled"
        elif v == "":
            try:
                y = m[n]
            except KeyError:
                x = "are disabled"
            else:
                x = "are enabled in " + " ".join([f"<#{z}>" for z in y])
        else:
            g, x = [], "have been "
            for c in v.split(" "):
                if c.startswith("<#") and c.endswith(">"):
                    f = int(c[2:-1])
                    try:
                        m[n].remove(f)
                        l = "dis"
                    except ValueError:
                        m[n].append(f)
                        l = "en"
                    except KeyError:
                        m[n] = [f]
                        l = "en"
                    jd(m, f"n{t.guild.id}")
                    g.append(f"{l}abled in {c}")
            x = (x + ", ".join(g)) if g else "Invalid input"
        e = Embed(
            title=f'{d.replace("_"," ")} notifications',
            color=Color(0xC3447A),
            description=x,
        )
    else:
        j = k = ""
        for n in a:
            d = i[a.index(n)].replace("_", " ")
            d = d[0].upper() + d[1:]
            try:
                y = m[n]
            except KeyError:
                j += d + "\n"
            else:
                k += f'{d} {" ".join(f"<#{z}>" for z in y)}\n'
        e = Embed(
            title=f"Notification status in {t.guild}",
            color=Color(0xC74375),
            timestamp=utils.utcnow(),
        )
        if k:
            e.add_field(name="Enabled", value=k, inline=False)
        if j:
            e.add_field(name="Disabled", value=j, inline=False)
    await t.send(embed=e)


@b.command(aliases=["ud", "urbandict", "urbandictionary"])
async def urban(t, *, w=""):
    async with t.typing():
        l = "define?term=" + quote(w) if w else "random"
        d = await gt("https://api.urbandictionary.com/v0/" + l, f=1)
        n, x = "", {}
        if "list" in d and len(d["list"]):
            x = d["list"][0]
            m, n = x["word"], "".join(
                c
                for c in f'{x["definition"]}\n\n*{x["example"]}*'
                if c not in ["[", "]"]
            )
        else:
            m = "No definitions found"
    await t.send(
        embed=Embed(
            title=m,
            color=Color(0x1D2439),
            description=n,
            url="https://urbandictionary.com/define.php?term=" + quote(x["word"])
            if x
            else "",
        ).set_footer(
            text="Powered by Urban Dictionary",
            icon_url="https://g.udimg.com/assets/apple-touch-icon-2ad9dfa3cb34c1d2740aaf1e8bcac791e2e654939e105241f3d3c8b889e4ac0c.png",
        )
    )


@b.command(aliases=["l", "lyrics", "sing"])
async def lyric(t, *, w="never gonna give you up"):
    def gg(a):
        return gt("https://musixmatch.com" + quote(a), h={"User-Agent": "Mozilla/5.0"})

    async with t.typing():
        z = gg("/search/" + w + "/tracks")
        s = bs4.BeautifulSoup(z, "html.parser").find(
            "div", attrs={"class": "media-card-text"}
        )
        try:
            a, s, u = (
                jl("ly2", 1),
                s.find("a", attrs={"class": "title"}),
                s.find("a", attrs={"class": "artist"}).get_text(),
            )
            m = a[s["href"]]
        except AttributeError:
            await t.send("Lyrics not found, please try again")
        except KeyError:
            l = ""
            while not l:
                y = gg(s["href"])
                l = bs4.BeautifulSoup(y, "html.parser")
            m = sh(
                "\n".join(
                    l.get_text()
                    for l in l.find_all(
                        "span",
                        attrs={"lyrics__content__ok", "lyrics__content__warning"},
                    )
                )
            )
            a[s["href"]] = m
            jd(a, "ly2", 1)
    n = []
    for j in range(len(m)):
        e = Embed(color=Color(0xFF6050), description=m[j])
        if j == 0:
            e = Embed(
                title=s.get_text().replace("'", "’"),
                url="https://musixmatch.com" + s["href"],
                color=Color(0xFF6050),
                description=m[0],
            ).set_author(name=u)
        if j == len(m) - 1:
            e.set_footer(
                text="Powered by Musixmatch",
                icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/Musixmatch_logo_icon_only.svg/2089px-Musixmatch_logo_icon_only.svg.png",
            )
        n.append(e)
    await t.send(embeds=n)


@b.command(aliases=["lg", "lyricsg"])
async def lyricg(t, *, w="never gonna give you up"):
    async with t.typing():
        z = await gt(
            "https://api.genius.com/search?q=" + quote(w),
            p={"access_token": cf["genius"]},
            f=1,
        )
        s, l, a = z["response"]["hits"][0]["result"], "", jl("ly", 2)
        try:
            m = a[s["url"]]
        except KeyError:
            while not l:
                y = await gt(s["url"])
                l = bs4.BeautifulSoup(y, "html.parser").find(
                    "div", attrs={"class": "lyrics"}
                )
            l = l.get_text().removeprefix("\n\n").removesuffix("\n\n")
            m = sh(l)
            a[s["url"]] = m
            jd(a, "ly", 2)
        f, h = " ".join(s["full_title"].replace("'", "’").split()), s["primary_artist"]
    n = []
    for j in range(len(m)):
        e = Embed(color=Color(0xC78D6B), description=m[j])
        if j == 0:
            e = (
                Embed(
                    title=s["title"].replace("'", "’"),
                    url=s["url"],
                    color=Color(0xC78D6B),
                    description=m[0],
                )
                .set_author(
                    name=f[f.index(" ".join(h["name"].replace("'", "’").split())) :],
                    url=h["url"],
                    icon_url=h["image_url"],
                )
                .set_thumbnail(url=s["song_art_image_url"])
            )
        if j == len(m) - 1:
            e.set_footer(
                text="Powered by Genius",
                icon_url="https://images.genius.com/8ed669cadd956443e29c70361ec4f372.1000x1000x1.png",
            )
        n.append(e)
    await t.send(embeds=n)


@b.group(aliases=["sgbus"], case_insensitive=True, invoke_without_command=True)
async def bus(t):
    raise commands.BadArgument


@bus.command(aliases=["a", "arrival", "t", "times", "timings"])
async def time(t, *, s):
    async def bb(x):
        c, d, v = x[0], x[2], ""
        y = await gt(
            "http://datamall2.mytransport.sg/ltaodataservice/BusArrivalv2?BusStopCode="
            + c,
            h={"AccountKey": cf["lta"]},
            f=1,
        )
        p, q, r = y["Services"], [], []
        if f:
            for s in p:
                if s["ServiceNo"].casefold() in f:
                    r.append(s)
                    q.append(s["ServiceNo"])
        else:
            r = p
        if isinstance(f, list) and len(f) > len(q):
            f.sort()
            k = [j for j in f if j not in q]
            v = "Unavailable service(s) here:"
            for s in k:
                v += f" **{s}**"
        g = Embed(
            title=f"Bus arrival timings from {d} ({c})",
            color=Color(0x21368B),
            description=v,
            timestamp=utils.utcnow(),
            url=f"https://www.google.com/maps/place/{x[3]},{x[4]}",
        ).set_footer(
            text="Powered by LTA DataMall",
            icon_url="https://datamall.lta.gov.sg/content/dam/datamall/images/DT_logoBeta.jpg",
        )
        o = dt.now()
        for s in r:
            s = list(s.values())
            e = s[2]["DestinationCode"]
            async with t.typing():
                n = ":one: "
                for l in range(2, 5):
                    try:
                        m = list(s[l].values())
                        i, j, k = m[3], m[4], ""
                        if float(i) != 0 and float(j) != 0:
                            k = f'([{round(distance((x[3],x[4]),(i,j)).m)}m](https://www.google.com/maps/place/{i},{j} "Location")) '
                        if l == 3:
                            n += "\n:two: "
                        if l == 4:
                            n += "\n:three: "
                        n += f'**{ds(dt.strptime(m[2],"%Y-%m-%dT%H:%M:%S+08:00")-o)}** {k}| '
                        if m[6] == "SEA":
                            n += ":seat:"
                        if m[6] == "SDA":
                            n += ":person_standing:"
                        if m[6] == "LSD":
                            n += ":people_holding_hands:"
                        n += f" | {m[8]}"
                        if m[5] != "1":
                            n += " | Visit " + m[5]
                    except ValueError:
                        break
                g.add_field(
                    name=f"{s[0]} to {sp(e)[2]} ({sp(e)[0]})", value=n, inline=False
                )
            if len(g.fields) % 25 == 0 and len(r) > 25:
                await t.send(embed=g)
                g.clear_fields()
        await t.send(embed=g)

    class T(ui.Button["I"]):
        def __init__(self, c):
            super().__init__(label=c)
            self.c = c

        async def callback(self, i):
            self.style = ButtonStyle.blurple
            await s.edit(embed=q, view=self.view)
            await bb(w[r.index(self.c)])
            self.style = ButtonStyle.green
            await s.edit(embed=q, view=self.view)

    class I(ui.View):
        def __init__(self):
            super().__init__(timeout=None)
            for c in r[:25]:
                self.add_item(T(c))

    try:
        s, f = s.split("\n", maxsplit=1)
        f = f.casefold().split(" ")
    except ValueError:
        f = ""
    try:
        if len(s) != 5:
            raise ValueError
        int(s)
        try:
            await bb(sp(s))
        except IndexError:
            await t.send("Stop not found")
    except ValueError:
        w = [
            n
            for n in list(csv.reader(open(f"stops.csv", "r")))
            if s.casefold() in n[2].casefold()
        ]
        if len(w) > 1:
            r = [f"{s[2]} ({s[0]}) at {s[1]}" for s in w]
            x = (
                f"\n{len(w)-25} more stops were found\nYou may want to narrow down your query"
                if len(w) > 25
                else ""
            )
            q = Embed(title="Which bus stop?", color=Color(0x068795)).set_footer(text=x)
            s = await t.send(embed=q, view=I())
        elif not w:
            await t.send("Stop not found")
        else:
            print(w)
            await bb(w[0])


@bus.command(aliases=["r", "routes"])
async def route(t, *, s):
    async def sm(m, n):
        f = []
        for j in range(len(m)):
            e = Embed(color=Color(h), description=m[j])
            if j == 0:
                e = Embed(
                    title=f"Service {p} route " + n,
                    url="https://busrouter.sg/#/services/" + p,
                    color=Color(h),
                    description=m[0],
                ).set_author(name="Operated by " + q, icon_url=x + y, url=x)
            if j == len(m) - 1:
                e.set_footer(
                    text="Powered by LTA DataMall",
                    icon_url="https://datamall.lta.gov.sg/content/dam/datamall/images/DT_logoBeta.jpg",
                )
            f.append(e)
        await t.send(embeds=f)

    c, d, f = (
        "",
        [
            j
            for j in list(csv.reader(open("routes.csv", "r")))
            if j[0].casefold() == s.casefold()
        ],
        "",
    )
    try:
        p, q = d[0][0], d[0][1]
    except IndexError:
        await t.send("Route not found")
    else:
        async with t.typing():
            for h in d:
                s = sp(h[4])
                a = f'{h[3]} | **{s[2]} ({h[4]})** at [{s[1]}](https://www.google.com/maps/place/{s[3]},{s[4]} "Location") | {h[5]}km\n'
                if h[2] == "1":
                    c += a
                elif h[2] == "2":
                    f += a
            if q == "SBST":
                h, x, y = (
                    0x5D1E79,
                    "https://www.sbstransit.com.sg/",
                    "Content/img/sbs-transit-logo.png",
                )
            if q == "SMRT":
                h, x, y = (
                    0xED1B2D,
                    "https://www.smrt.com.sg/",
                    "portals/0/Skins/SMRTNEW/images/businesses/SMRT_Buses-Logo.jpg",
                )
            if q == "TTS":
                h, x, y = (
                    0x009548,
                    "https://towertransit.sg/",
                    "wp-content/themes/tower-transit/assets/images/page_template/logo_tower_transit.png",
                )
            if q == "GAS":
                h, x, y = (
                    0xED1C24,
                    "https://www.go-aheadsingapore.com/",
                    "static/images/colorways/singapore/logo.png",
                )
            await sm(sh(c), "direction 1" if f else "")
            if f:
                await sm(sh(f), "direction 2")


@b.command(aliases=["fb", "fizz", "buzz"])
async def fizzbuzz(t):
    def an(x):
        y, z = str(x) if (x % c and x % d) else "", 0
        if x % c == 0:
            y += "fizz"
            z += 1
        if x % d == 0:
            y += "buzz"
            z += 2
        return y, z

    def ch(m):
        return (
            m.channel == t.channel
            and m.author != t.me
            and m.content.lower in ["fizz", "buzz", "fizzbuzz"]
        )

    x, c, d, l = 0, randbelow(5) + 3, 1, 3
    while c >= d or d % c == 0:
        d = randbelow(6) + 4
    await t.send(
        f"Every multiple of {c} = **fizz**, {d} = **buzz**, {c} AND {d} = **fizzbuzz**\nYou have **{l}** lives"
    )
    while l > 0:
        x += 1
        await t.send(an(x)[0])
        y = await b.wait_for("message", check=ch)
        y = y.content.casefold()
        x += 1
        j, k = an(x)
        if y != j:
            l -= 1
            if k == 1:
                n = f"{x} is a multiple of {c}"
            if k == 2:
                n = f"{x} is a multiple of {d}"
            if k == 3:
                n = f"{x} is a multiple of {c} AND {d}"
            if k == 0:
                n = ""
            await t.send(f"**WRONG!** {n}\nLives left: **{l}**")
    await t.send("**Congrats, you lost!**")


@b.command(aliases=["hm"])
async def hangman(t, d=""):
    def ch(m):
        return (
            m.channel == t.channel
            and m.author != t.me
            and len(m.content) == 1
            and m.content.isalpha()
        )

    if d in ["e", "easy"]:
        a = open("easy.txt", "r").read()
    elif d in ["m", "medium"]:
        a = open("medium.txt", "r").read()
    elif d in ["h", "hard", "d", "difficult"]:
        a = open("hard.txt", "r").read()
    else:
        a = ""
        for j in ["easy", "medium", "hard"]:
            a += open(f"{j}.txt", "r").read()
    y, p, n = [], choice(a.splitlines()), 0
    x = ["_" if j != " " else " " for j in p]
    g, h = "".join(x), ["", "|", "|", "|", "|", "|"]
    e = (
        Embed(
            title="Enter guess",
            color=Color(0xE95C20),
            description=f"Your word is:\n**```{' '.join(g)}```**",
        )
        .add_field(name="Wrong guesses", value="None yet")
        .add_field(name="Hangman", value="```" + "\n".join(h) + "```")
    )
    c = await t.send(embed=e)
    while g != p:
        k = await b.wait_for("message", check=ch)
        l = k.content.casefold()
        if l in y + x:
            await c.edit(embed=e.set_footer(text=f"You have guessed {l} before"))
        elif l not in p:
            n += 1
            y.append(l)
            if n >= 1:
                h[0] = "————"
            if n >= 2:
                h[1] = "|  0"
            if n >= 3:
                h[2] = "|  |"
                h[3] = h[2]
            if n >= 4:
                h[2] = "| /|"
            if n >= 5:
                h[2] = "| /|\\"
            if n >= 6:
                h[4] = "| /"
            if n >= 7:
                h[4] = "| /|\\"
            await c.edit(
                embed=e.set_field_at(0, name="Wrong guesses", value=" ".join(y))
                .set_field_at(1, name="Hangman", value="```" + "\n".join(h) + "```")
                .set_footer(text="")
            )
            if n >= 7:
                await t.send(
                    embed=Embed(
                        title="Out of chances!",
                        color=Color(0xE95C23),
                        description="```"
                        + "\n".join(h)
                        + f"```\nYour word was: **[{p}](https://www.merriam-webster.com/dictionary/{quote(p)} 'Definition')**",
                    )
                )
                break
        else:
            for a in range(len(p)):
                if p[a] == l:
                    x[a] = l
                    g = "".join(x)
            f = e.to_dict()
            f["description"] = f"Your word is:\n**```{' '.join(g)}```**"
            e = Embed.from_dict(f)
            await c.edit(embed=e.set_footer(text=""))
    else:
        await t.send(
            embed=Embed(
                title="You guessed it!",
                color=Color(0xE95C23),
                description=f"Your word was: **[{p}](https://www.merriam-webster.com/dictionary/{quote(p)} 'Definition')**",
            )
        )
    open("hmstat.csv", "a").write(",".join([p, str(n)] + y) + "\n")


@b.command(aliases=["tictactoe", "tic", "tac", "toe"])
async def ttt(t, g: int = 3):
    class B(ui.Button["TicTacToe"]):
        def __init__(self, x: int, y: int):
            super().__init__(style=ButtonStyle.gray, label="\u200b", row=y)
            self.x = x
            self.y = y

        async def callback(self, i):
            v: T = self.view
            s = v.o[self.y][self.x]
            if s in (v.X, v.O):
                return
            if v.p == v.X:
                self.style = ButtonStyle.red
                self.label = "X"
                v.o[self.y][self.x] = v.X
                v.p = v.O
                n = "It is now O’s turn"
            else:
                self.style = ButtonStyle.green
                self.label = "O"
                v.o[self.y][self.x] = v.O
                v.p = v.X
                n = "It is now X’s turn"
            self.disabled = True
            w = v.r()
            if w:
                if w == v.X:
                    n = "X won!"
                elif w == v.O:
                    n = "O won!"
                else:
                    n = "It’s a tie!"
                for h in v.children:
                    h.disabled = True
                v.stop()
            await i.response.edit_message(content=n, view=v)

    class T(ui.View):
        X, O, E = -1, 1, 9

        def __init__(self, g):
            super().__init__(timeout=None)
            self.p = self.X
            self.g = g
            self.o = []
            for _ in range(self.g):
                self.o.append([0] * self.g)
            for x in range(self.g):
                for y in range(self.g):
                    self.add_item(B(x, y))

        def r(self):
            s = (
                [sum(i) for i in self.o]
                + [sum(self.o[i][j] for i in range(self.g)) for j in range(self.g)]
                + [sum(self.o[i][self.g - i - 1] for i in range(self.g))]
                + [sum(self.o[i][i] for i in range(self.g))]
            )
            if self.g in s:
                return self.O
            elif -self.g in s:
                return self.X
            if all(j != 0 for r in self.o for j in r):
                return self.E

    if 1 < g < 6:
        await t.send("Tic Tac Toe: X goes first", view=T(g))
    else:
        await t.send("Whoa whoa whoa, that number’s too large!")


@b.command(aliases=["cs"])
async def cowsay(t, *, r=""):
    w = (
        textwrap.wrap(r.strip(), 39)
        if r
        else choice(open("fortunes.txt", "r").read().split("%"))
        .strip()
        .replace("\t", r"    ")
        .splitlines()
    )
    l = [i.ljust(len(max(w, key=len))) for i in w]
    s = len(l[0])
    f = [" " + "_" * (s + 2)]
    for j, k in enumerate(l):
        if len(l) < 2:
            x, y = "<", ">"
        elif j == 0:
            x, y = "/", "\\"
        elif j == len(l) - 1:
            x, y = "\\", "/"
        else:
            x = y = "|"
        f.append(f"{x} {k} {y}")
    await t.send(
        "```"
        + "\n".join(f + [" " + "-" * (s + 2)])
        + r"""
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||```"""
    )


@b.command(aliases=["d", "rolldice", "random"])
async def dice(t, *, s=6):
    await t.send(randbelow(int(s)) + 1)


@b.command(aliases=["8", "8ball"])
async def eightball(t, *, q=" "):
    await t.send(
        f'Question: **{q}**\nAnswer: **{choice(["It is certain.","It is decidedly so.","Without a doubt.","Yes – definitely.","You may rely on it.","As I see it, yes.","Most likely.","Outlook good.","Yes.","Signs point to yes.","Reply hazy, try again.","Ask again later.","Better not tell you now.","Cannot predict now.","Concentrate and ask again.","Don’t count on it.","My reply is no.","My sources say no.","Outlook not so good.","Very doubtful."])}**'
    )


@b.command(aliases=["a"])
async def ask(t, *, q=" "):
    await t.send(
        f'Question: **{q}**\nAnswer: **{choice(["yes","no","lol","wut","bruh","hmm","ah","ofc"])}**'
    )


@b.command()
async def cram(t):
    await t.send(
        choice(
            [
                "Who is cram?",
                "What is cram?",
                "Where is cram?",
                "Is cram even worth it?",
            ]
        )
    )


@b.command()
async def moo(t):
    await t.send(
        r"""```
                 (__)
                 (oo)
           /------\/
          / |    ||
         *  /\---/\
            ~~   ~~
..."Have you mooed today?"...```"""
    )


@b.command()
async def sd(t, *, s=""):
    if t.author.id in cf["owners"]:
        cf["status"] = s
        jd(cf, "c")
        await t.send("Shut down main")
        await b.close()
        print(f"not {b.user.name} main")
    else:
        raise commands.CommandNotFound


@b.command()
async def shut(t, *, s=""):
    if t.author.id in cf["owners"]:
        cf["status"] = s
        jd(cf, "c")
        await t.send("Shut down main and event")
        await b.close()
        print(f"not {b.user.name} main and event")
    else:
        raise commands.CommandNotFound


b.run(cf["token"])
