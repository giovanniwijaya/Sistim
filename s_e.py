import csv
import itertools
import json
import subprocess
import sys
from discord import *
from discord.ext import commands, tasks


def jl(f):
    with open("s_" + f + ".json", "r") as p:
        return json.load(p)


def jd(c, f):
    with open("s_" + f + ".json", "w") as p:
        json.dump(c, p)


async def sn(g, c, m: Embed = None, n=None, o=""):
    q = jl(f"n{g}")
    try:
        s = q[c]
    except KeyError:
        pass
    else:
        for x in s:
            if m:
                await b.get_channel(x).send(embed=m)
            elif n:
                await b.get_channel(x).send(embeds=n)
            if o:
                await b.get_channel(x).send(q[c[0] * 2].replace("{member}", o))


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
        if d or h:
            y += ","
        if s:
            y += " and "
        f += f"{m} minute{y}"
    if s:
        f += f"{s} second{z}"
    return f


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


def gr(p):
    with open(f"s_r{p.guild_id}.csv", "r", encoding="utf-8") as c:
        for o in list(csv.reader(c)):
            if p.message_id == int(o[0]):
                if len(o[2]) < 9:
                    x = p.emoji.name == o[2]
                else:
                    x = p.emoji.id == int(o[2].split(":")[2][:-1])
                if x:
                    return b.get_guild(p.guild_id).get_role(int(o[1]))


b = commands.AutoShardedBot(
    command_prefix="+", intents=Intents.all(), max_messages=99999999
)
b.remove_command("help")
k, cf = itertools.cycle(
    [
        "myself",
        "with fire",
        "maths educational videos",
        "4′33″",
        "games with your heart",
    ]
), jl("c")


@b.event
async def on_ready():
    s = cf["status"]
    if s != "on":
        await b.change_presence(status=Status.idle, activity=Game(s))
    else:
        subprocess.Popen([sys.executable, "s.py"])
        cf["status"] = "on"
        jd(cf, "c")
        st.start()
    print(b.user.name + "event")


@tasks.loop(seconds=23)
async def st():
    await b.change_presence(status=Status.online, activity=Game(next(k)))


@b.event
async def on_guild_join(g):
    try:
        p = jl(f"n{g.id}")
        p = p["pp"]
    except KeyError or FileNotFoundError:
        p = "+"
        jd(
            {
                "pp": p,
                "ww": "Welcome, {member}! Hope you enjoy it here :)",
                "gg": "Goodbye, {member}! We ***totally*** will miss you :)",
            },
            f"n{g.id}",
        )
    s = cf["status"]
    a = (
        f"\n\nI am currently undergoing **{s}** so my commands and/or functionalities are unavailable for now. I’ll be back soon!"
        if s != "on"
        else ""
    )
    await g.system_channel.send(
        embed=Embed(
            title=f"Hello, I am {b.user.name}!",
            color=Color(0x9EA450),
            description=f"""I’m glad to be in {g}
**My prefix** here is `{p}` (in addition to mentioning me) but you can change it in your guild by typing `{p}prefix [prefix]`
I can **remind you of events**, send **moderation-related logs**, **manage users**, and **have some fun**!
Type `{p}help` for all my commands"""
            + a,
        )
    )


@b.event
async def on_member_join(m):
    mc = m.guild.member_count
    if mc % 10 == 1 and mc % 100 != 11:
        ss = "st"
    elif mc % 10 == 2 and mc % 100 != 12:
        ss = "nd"
    elif mc % 10 == 3 and mc % 100 != 13:
        ss = "rd"
    else:
        ss = "th"
    await sn(
        m.guild.id,
        "mj",
        Embed(
            title="Member joined",
            color=Color(0x54C247),
            description=f"{m.mention} {mc}{ss} member\n**Account existed for** {dl(m.joined_at-m.created_at)}",
            timestamp=utils.utcnow(),
        )
        .set_footer(text=f"User ID: {m.id}")
        .set_author(name=str(m), icon_url=m.display_avatar),
    )
    await sn(m.guild.id, "wm", o=m.mention)


@b.event
async def on_member_remove(m):
    rl = " ".join(r.mention for r in m.roles[1:])
    await sn(
        m.guild.id,
        "mr",
        Embed(
            title="Member left",
            color=Color(0xF5EF96),
            description=f"{m.mention}\n**Joined for** {dl(utils.utcnow()-m.joined_at)}\n**Roles**: {rl}",
            timestamp=utils.utcnow(),
        )
        .set_footer(text=f"User ID: {m.id}")
        .set_author(name=str(m), icon_url=m.display_avatar),
    )
    await sn(m.guild.id, "gm", o=m.mention)


@b.event
async def on_member_ban(g, m):
    rl = " ".join(r.mention for r in m.roles[1:])
    await sn(
        g.id,
        "mb",
        Embed(
            title="Member banned",
            color=Color(0xFA4616),
            description=f"{m.mention}\n**Joined for** {dl(utils.utcnow()-m.joined_at)}\n**Roles**: {rl}",
            timestamp=utils.utcnow(),
        )
        .set_footer(text=f"User ID: {m.id}")
        .set_author(name=str(m), icon_url=m.display_avatar),
    )


@b.event
async def on_member_unban(g, u):
    await sn(
        g.id,
        "mu",
        Embed(
            title="Member unbanned",
            color=Color(0x2399D0),
            description=f"{u.mention}",
            timestamp=utils.utcnow(),
        )
        .set_footer(text=f"User ID: {u.id}")
        .set_author(name=str(u), icon_url=u.display_avatar),
    )


@b.event
async def on_member_update(e, r):
    if e.roles != r.roles:
        x, y = [i for i in e.roles if i not in r.roles], [
            j for j in r.roles if j not in e.roles
        ]
        if len(e.roles) < len(r.roles):
            a, x = "add", y
        elif len(e.roles) > len(r.roles):
            a = "remov"
        l, m = "mo", Embed(
            title=f"Role {a}ed",
            color=Color(0x34558B),
            description=f"{r.mention}\n{x[0].mention}",
            timestamp=utils.utcnow(),
        )
    if e.display_name != r.display_name:
        a = "chang"
        if not e.nick:
            a = "add"
        elif not r.nick:
            a = "remov"
        l, m = "mn", Embed(
            title=f"Nickname {a}ed",
            color=Color(0x7AABDE),
            description=f"{r.mention}\n**Before**: {e.display_name}\n**After**: {r.display_name}",
            timestamp=utils.utcnow(),
        )
    if e.pending != r.pending:
        l, m = "mv", Embed(
            title="Verification passed",
            color=Color(0x3F43AD),
            description=f"{r.mention}",
            timestamp=utils.utcnow(),
        )
    await sn(
        r.guild.id,
        l,
        m.set_footer(text=f"User ID: {r.id}").set_author(
            name=str(r), icon_url=r.display_avatar
        ),
    )


@b.event
async def on_presence_update(e, r):
    if e.status != r.status:
        l, m = "ms", Embed(
            title="Status changed",
            color=Color(0x3CA1D5),
            description=f"{r.mention}\n**Before**: {e.status}\n**After**: {r.status}",
            timestamp=utils.utcnow(),
        )
    if e.activity != r.activity:
        l, m = "ma", Embed(
            title="Activity changed",
            color=Color(0x6667AB),
            description=f"{r.mention}\n**Before**: {e.activity}\n**After**: {r.activity}",
            timestamp=utils.utcnow(),
        )
    await sn(
        r.guild.id,
        l,
        m.set_footer(text=f"User ID: {r.id}").set_author(
            name=str(r), icon_url=r.display_avatar
        ),
    )


@b.event
async def on_user_update(e, r):
    for m in b.get_all_members():
        if m.id == r.id:
            if e.display_avatar != r.display_avatar:
                a = "chang"
                if not e.avatar:
                    a = "add"
                elif not r.avatar:
                    a = "remov"
                l, m = "ua", Embed(
                    title=f"Avatar {a}ed",
                    color=Color(0x679BBE),
                    description=f"{m.mention}",
                    timestamp=utils.utcnow(),
                ).set_thumbnail(url=e.display_avatar).set_image(
                    url=r.display_avatar
                ).set_footer(
                    text=f"User ID: {m.id}"
                ).set_author(
                    name=str(r), icon_url=r.display_avatar
                )
            if e.name != r.name:
                l, m = "un", Embed(
                    title="Name changed",
                    color=Color(0x7AABDE),
                    description=f"{m.mention}\n**Before**: {e.name}\n**After**: {r.name}",
                    timestamp=utils.utcnow(),
                ).set_footer(text=f"User ID: {m.id}").set_author(
                    name=str(r), icon_url=r.display_avatar
                )
            if e.discriminator != r.discriminator:
                l, m = "ud", Embed(
                    title="Discriminator changed",
                    color=Color(0x00629B),
                    description=f"{r.mention}\n**Before**: {e.discriminator}\n**After**: {r.discriminator}",
                    timestamp=utils.utcnow(),
                ).set_footer(text=f"User ID: {m.id}").set_author(
                    name=str(r), icon_url=r.display_avatar
                )
            await sn(m.guild.id, l, m)


@b.event
async def on_guild_role_create(r):
    rc = len(r.guild.roles)
    if rc % 10 == 1 and rc % 100 != 11:
        ss = "st"
    elif rc % 10 == 2 and rc % 100 != 12:
        ss = "nd"
    elif rc % 10 == 3 and rc % 100 != 13:
        ss = "rd"
    else:
        ss = "th"
    m, e, h = "", "Unm", "Unh"
    if r.managed:
        m = "\n**Managed** by integration"
    if r.mentionable:
        e = "M"
    if r.hoist:
        h = "H"
    await sn(
        r.guild.id,
        "rc",
        Embed(
            title="Role created",
            color=Color(0x45B8AC),
            description=f"{r.mention} {rc}{ss} role\n**Name**: {r}\n**Color**: {r.color}\n**{e}entionable**\n**{h}oisted**{m}",
            timestamp=utils.utcnow(),
        ).set_footer(text=f"Role ID: {r.id}"),
    )


@b.event
async def on_guild_role_delete(r):
    x, z = len(r.guild.roles), " ".join(
        f"`{y[0]}`" for y in iter(r.permissions) if y[1]
    )
    await sn(
        r.guild.id,
        "rd",
        Embed(
            title="Role removed",
            color=Color(0xBC243C),
            description=f"{r}\n**Color**: {r.color}\n**Mentionable**: {r.mentionable}\n**Hoisted**: {r.hoist}\n**Position**: {x-r.position+1} out of {x+1}\n**Permissions**: {z}\n**Role existed for** {dl(utils.utcnow()-r.created_at)}",
            timestamp=utils.utcnow(),
        ).set_footer(text=f"Role ID: {r.id}"),
    )


@b.event
async def on_guild_role_update(e, r):
    if e.permissions != r.permissions:
        g, h = [c[0] for c in iter(e.permissions) if c[1]], [
            d[0] for d in iter(r.permissions) if d[1]
        ]
        l, x, y = "rp", [i for i in g if i not in h], [j for j in h if j not in g]
        if y:
            m = Embed(
                title="Role permission added",
                color=Color(0x00A1B4),
                description=f'{r.mention}\n{" ".join(f"`{d}`" for d in y)}',
                timestamp=utils.utcnow(),
            )
        if x:
            m = Embed(
                title="Role permission removed",
                color=Color(0x00A1B4),
                description=f'{r.mention}\n{" ".join(f"`{c}`" for c in x)}',
                timestamp=utils.utcnow(),
            )
    if e.name != r.name:
        l, m = "rn", Embed(
            title="Role name changed",
            color=Color(0x003DA5),
            description=f"{r.mention}\n**Before**: {e.name}\n**After**: {r.name}",
            timestamp=utils.utcnow(),
        )
    if e.hoist != r.hoist:
        l, m = "rh", Embed(
            title=f'Role {"" if r.hoist else "un"}hoisted',
            color=Color(0x0072CE),
            description=f"{r.mention}",
            timestamp=utils.utcnow(),
        )
    if e.mentionable != r.mentionable:
        l, m = "rm", Embed(
            title=f'Role {"" if r.mentionable else "un"}mentionable',
            color=Color(0x0085CA),
            description=f"{r.mention}",
            timestamp=utils.utcnow(),
        )
    if e.position != r.position:
        l, x = "ro", len(r.guild.roles)
        m = Embed(
            title="Role position changed",
            color=Color(0x0E4174),
            description=f"{r.mention}\n**Before**: {x-e.position} out of {x}\n**After**: {x-r.position}",
            timestamp=utils.utcnow(),
        )
    if e.color != r.color:
        l, m = "rl", Embed(
            title="Role color changed",
            color=Color(0x009CDE),
            description=f"{r.mention}\n**Before**: {e.color}\n**After**: {r.color}",
            timestamp=utils.utcnow(),
        )
    await sn(r.guild.id, l, m.set_footer(text=f"Role ID: {r.id}"))


@b.event
async def on_raw_message_delete(p):
    n, z = [], p.cached_message
    if z:
        m, a = z.content, z.author
        x, y, w = a.mention, a.id, a.display_avatar
        if y != b.user.id:
            d = sh(f"{x} in <#{p.channel_id}>\n{m}")
            for j in range(len(d)):
                e = Embed(
                    color=Color(0xDC3D46), description=d[j], timestamp=utils.utcnow()
                )
                if j == 0:
                    e = Embed(
                        title="Message deleted",
                        color=Color(0xDC3D46),
                        description=d[0],
                        timestamp=utils.utcnow(),
                        url=f"https://discord.com/channels/{p.guild_id}/{p.channel_id}/{p.message_id}",
                    ).set_author(name=str(a), icon_url=w)
                if j == len(d) - 1:
                    e.set_footer(text=f"Message ID: {p.message_id}\nUser ID: {y}")
                n.append(e)
    else:
        n = [
            Embed(
                title="Message deleted (unrecorded)",
                color=Color(0xDC3D46),
                timestamp=utils.utcnow(),
                url=f"https://discord.com/channels/{p.guild_id}/{p.channel_id}/{p.message_id}",
            ).set_footer(text=f"Message ID: {p.message_id}")
        ]
    await sn(p.guild_id, "md", n=n)


@b.event
async def on_raw_message_edit(p):
    n, y, z = [], p.data, p.cached_message
    a, r = y["author"], y["content"]
    x = b.get_user(int(a["id"]))
    e = f"**Before**: {z.content}\n**After**: {r}" if z else r
    if a and e != r and x.id != b.user.id:
        a = int(a["id"])
        d = sh(f"<@!{a}> in <#{p.channel_id}>\n{e}")
        for j in range(len(d)):
            e = Embed(color=Color(0x007FAF), description=d[j], timestamp=utils.utcnow())
            if j == 0:
                e = Embed(
                    title="Message edited" + ""
                    if z
                    else "(previous version unrecorded)",
                    color=Color(0x007FAF),
                    description=d[0],
                    timestamp=utils.utcnow(),
                    url=f'https://discord.com/channels/{y["guild_id"]}/{y["channel_id"]}/{y["id"]}',
                ).set_author(name=x, icon_url=x.display_avatar)
            if j == len(d) - 1:
                e.set_footer(text=f"Message ID: {p.message_id}\nUser ID: {a}")
            n.append(e)
        await sn(y["guild_id"], "me", n=n)


@b.event
async def on_raw_reaction_add(p):
    await sn(
        p.guild_id,
        "ra",
        Embed(
            title="Reaction added",
            color=Color(0xF5DF4D),
            description=f"<@!{p.user_id}> in <#{p.channel_id}>\n{p.emoji}",
            timestamp=utils.utcnow(),
            url=f"https://discord.com/channels/{p.guild_id}/{p.channel_id}/{p.message_id}",
        )
        .set_footer(text=f"Message ID: {p.message_id}\nUser ID: {p.user_id}")
        .set_author(name=p.member, icon_url=p.member.display_avatar),
    )
    if p.user_id != b.user.id:
        r = gr(p)
        await p.member.add_roles(r, reason=f"Reacted to message ID {p.message_id}")


@b.event
async def on_raw_reaction_remove(p):
    n = b.get_user(p.user_id)
    await sn(
        p.guild_id,
        "rr",
        Embed(
            title="Reaction removed",
            color=Color(0xF0CD5B),
            description=f"<@!{p.user_id}> in <#{p.channel_id}>\n{p.emoji}",
            timestamp=utils.utcnow(),
            url=f"https://discord.com/channels/{p.guild_id}/{p.channel_id}/{p.message_id}",
        )
        .set_footer(text=f"Message ID: {p.message_id}\nUser ID: {p.user_id}")
        .set_author(name=n, icon_url=n.display_avatar),
    )
    if p.user_id != b.user.id:
        r = gr(p)
        await b.get_guild(p.guild_id).get_member(p.user_id).remove_roles(
            r, reason=f"Unreacted to message ID {p.message_id}"
        )


@b.event
async def on_message(m):
    p = jl(f"n{m.guild.id}")["pp"] if m.guild else "+"
    s = cf["status"]
    if s != "on":
        if m.content.startswith(f"{p}start") and m.author.id == 215446858754031616:
            subprocess.Popen([sys.executable, "s.py"])
            st.start()
            await m.channel.send("Restarted main")
        elif m.content.startswith(f"{p}shut") and m.author.id == 215446858754031616:
            await b.change_presence(status=Status.offline, activity=Game(s))
            await m.channel.send("Shut down event")
            await b.close()
        elif m.content.startswith(p):
            st.cancel()
            await b.change_presence(status=Status.idle, activity=Game(s))


b.run(cf["token"])
