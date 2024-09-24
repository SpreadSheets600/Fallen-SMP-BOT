import re
import os
import discord
import sqlite3
from datetime import timedelta
from pymongo import MongoClient
from discord.ext import commands
from discord.ui.item import Item
from discord.commands import SlashCommandGroup


ADMINS = [
    727012870683885578,
    437622938242514945,
    243042987922292738,
    664157606587138048,
    1188730953217097811,
    896411007797325824,
]

MODS = [
    1273283762624663625,
    1147935418508132423,
]


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.mongo_client = MongoClient(os.getenv("MONGO_URI"))
        self.db = self.mongo_client["Users"]
        self.collection = self.db["UserData"]

    def connect_database(self):
        self.connection = sqlite3.connect("Moderation.db")
        self.cursor = self.connection.cursor()

    def close_database(self):
        self.connection.commit()
        self.connection.close()

    @commands.command(name="ban", aliases=["b"])
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):

        if not reason:
            reason = "No Reason Provided"

        await member.ban(reason=reason)

        embed = discord.Embed(
            title=":hammer: Banned",
            description=f"**{member}** Has Been Banned By **{ctx.author}**",
            color=discord.Color.red(),
        )

        if reason:
            embed.add_field(name="Reason", value=reason, inline=False)

        await ctx.send(embed=embed)

        user = await self.bot.fetch_user(member.id)

        try:
            await user.send(embed=embed)
        except discord.Forbidden:
            pass

        await self.connect_database()
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS Bans (user_id INTEGER, guild_id INTEGER, reason TEXT)"
        )
        self.cursor.execute(
            "INSERT INTO Bans (user_id, guild_id, reason) VALUES (?, ?, ?)",
            (member.id, ctx.guild.id, reason),
        )
        await self.close_database()

        user_id = member.id

        document = self.collection.find_one({"ID": user_id})
        username = document["Username"]

        console_channel = self.bot.get_channel(1263898954999922720)
        await console_channel.send(f"ban {username} {reason}")

    @commands.command(name="unban", aliases=["ub"])
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, member):

        await self.connect_database()
        self.cursor.execute(
            "SELECT user_id FROM Bans WHERE guild_id = ? AND user_id = ?",
            (ctx.guild.id, member.id),
        )
        user_id = self.cursor.fetchone()

        if not user_id:
            return await ctx.send("User Is Not Banned")

        self.cursor.execute(
            "DELETE FROM Bans WHERE guild_id = ? AND user_id = ?",
            (ctx.guild.id, member.id),
        )

        await self.close_database()
        await ctx.guild.unban(discord.Object(id=member.id))

        embed = discord.Embed(
            title=":hammer: Unbanned",
            description=f"**{member}** Has Been Unbanned By **{ctx.author}**",
            color=discord.Color.green(),
        )

        await ctx.send(embed=embed)

        user = await self.bot.fetch_user(member.id)

        try:
            await user.send(embed=embed)
        except discord.Forbidden:
            pass

        user_id = member.id
        document = self.collection.find_one({"ID": user_id})
        username = document["Username"]

        console_channel = self.bot.get_channel(1263898954999922720)
        await console_channel.send(f"unban {username}")

    @commands.command(name="kick", aliases=["k"])
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):

        if not reason:
            reason = "No Reason Provided"

        await member.kick(reason=reason)

        embed = discord.Embed(
            title=":hammer: Kicked",
            description=f"**{member}** Has Been Kicked By **{ctx.author}**",
            color=discord.Color.red(),
        )

        if reason:
            embed.add_field(name="Reason", value=reason, inline=False)

        await ctx.send(embed=embed)

        user = await self.bot.fetch_user(member.id)

        try:
            await user.send(embed=embed)
        except discord.Forbidden:
            pass

        user_id = member.id
        document = self.collection.find_one({"ID": user_id})
        username = document["Username"]

        console_channel = self.bot.get_channel(1263898954999922720)
        await console_channel.send(f"kick {username} {reason}")

    @commands.command(name="mute", aliases=["m"])
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, *, reason=None):

        if not reason:
            reason = "No Reason Provided"

        role = discord.utils.get(ctx.guild.roles, name="Muted")
        await member.add_roles(role)

        embed = discord.Embed(
            title=":hammer: Muted",
            description=f"**{member}** Has Been Muted By **{ctx.author}**",
            color=discord.Color.red(),
        )

        if reason:
            embed.add_field(name="Reason", value=reason, inline=False)

        await ctx.send(embed=embed)

        user = await self.bot.fetch_user(member.id)

        try:
            await user.send(embed=embed)
        except discord.Forbidden:
            pass

        user_id = member.id
        document = self.collection.find_one({"ID": user_id})
        username = document["Username"]

        console_channel = self.bot.get_channel(1263898954999922720)
        await console_channel.send(f"mute {username} {reason}")

    @commands.command(name="unmute", aliases=["um"])
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member):

        role = discord.utils.get(ctx.guild.roles, name="Muted")
        await member.remove_roles(role)

        embed = discord.Embed(
            title=":hammer: Unmuted",
            description=f"**{member}** Has Been Unmuted By **{ctx.author}**",
            color=discord.Color.green(),
        )

        await ctx.send(embed=embed)

        user = await self.bot.fetch_user(member.id)

        try:
            await user.send(embed=embed)
        except discord.Forbidden:
            pass

        user_id = member.id
        document = self.collection.find_one({"ID": user_id})
        username = document["Username"]

        console_channel = self.bot.get_channel(1263898954999922720)
        await console_channel.send(f"unmute {username}")

    @commands.command(name="warn", aliases=["w"])
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason=None):

        if not reason:
            reason = "No Reason Provided"

        embed = discord.Embed(
            title=":hammer: Warned",
            description=f"**{member}** Has Been Warned By **{ctx.author}**",
            color=discord.Color.red(),
        )

        if reason:
            embed.add_field(name="Reason", value=reason, inline=False)

        await ctx.send(embed=embed)

        user = await self.bot.fetch_user(member.id)

        try:
            await user.send(embed=embed)
        except discord.Forbidden:
            pass

        user_id = member.id
        document = self.collection.find_one({"ID": user_id})
        username = document["Username"]

        console_channel = self.bot.get_channel(1263898954999922720)
        await console_channel.send(f"warn {username} {reason}")

        await self.connect_database()
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS Warns (user_id INTEGER, guild_id INTEGER, reason TEXT)"
        )
        self.cursor.execute(
            "INSERT INTO Warns (user_id, guild_id, reason) VALUES (?, ?, ?)",
            (member.id, ctx.guild.id, reason),
        )

        await self.close_database()

    @commands.command(name="warnings", aliases=["warns"])
    @commands.has_permissions(manage_messages=True)
    async def warnings(self, ctx, member: discord.Member):

        await self.connect_database()
        self.cursor.execute(
            "SELECT reason FROM Warns WHERE guild_id = ? AND user_id = ?",
            (ctx.guild.id, member.id),
        )
        warnings = self.cursor.fetchall()

        if not warnings:
            return await ctx.send("User Has No Warnings")

        embed = discord.Embed(
            title=":hammer: Warnings",
            description=f"**{member}** Has {len(warnings)} Warnings",
            color=discord.Color.red(),
        )

        for index, warning in enumerate(warnings):
            embed.add_field(name=f"Warning {index + 1}", value=warning[0], inline=False)

        await ctx.send(embed=embed)

        await self.close_database()

    @commands.command(name="clearwarns", aliases=["cw"])
    @commands.has_permissions(manage_messages=True)
    async def clearwarns(self, ctx, member: discord.Member):

        await self.connect_database()
        self.cursor.execute(
            "SELECT reason FROM Warns WHERE guild_id = ? AND user_id = ?",
            (ctx.guild.id, member.id),
        )
        warnings = self.cursor.fetchall()

        if not warnings:
            return await ctx.send("User Has No Warnings")

        self.cursor.execute(
            "DELETE FROM Warns WHERE guild_id = ? AND user_id = ?",
            (ctx.guild.id, member.id),
        )

        await self.close_database()

        embed = discord.Embed(
            title=":hammer: Cleared Warnings",
            description=f"**{member}**'s Warnings Have Been Cleared By **{ctx.author}**",
            color=discord.Color.green(),
        )

        await ctx.send(embed=embed)

        user = await self.bot.fetch_user(member.id)

        try:
            await user.send(embed=embed)
        except discord.Forbidden:
            pass

        user_id = member.id
        document = self.collection.find_one({"ID": user_id})
        username = document["Username"]

        console_channel = self.bot.get_channel(1263898954999922720)
        await console_channel.send(f"clearwarns {username}")

    @commands.command(name="lock", aliases=["l"])
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx, channel: discord.TextChannel = None):

        if not channel:
            channel = ctx.channel

        await channel.set_permissions(ctx.guild.default_role, send_messages=False)

        embed = discord.Embed(
            title=":hammer: Locked",
            description=f"**{channel}** Has Been Locked By **{ctx.author}**",
            color=discord.Color.red(),
        )

        await ctx.send(embed=embed)

    @commands.command(name="unlock", aliases=["ul"])
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx, channel: discord.TextChannel = None):

        if not channel:
            channel = ctx.channel

        await channel.set_permissions(ctx.guild.default_role, send_messages=True)

        embed = discord.Embed(
            title=":hammer: Unlocked",
            description=f"**{channel}** Has Been Unlocked By **{ctx.author}**",
            color=discord.Color.green(),
        )

        await ctx.send(embed=embed)

    @commands.command(name="purge", aliases=["clear", "prune"])
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int):

        await ctx.channel.purge(limit=amount + 1)

        embed = discord.Embed(
            title=":hammer: Purged",
            description=f"**{amount}** Messages Have Been Purged By **{ctx.author}**",
            color=discord.Color.red(),
        )

        await ctx.send(embed=embed)

    @commands.command(name="slowmode", aliases=["sm"])
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, seconds: int, channel: discord.TextChannel = None):

        if not channel:
            channel = ctx.channel

        await channel.edit(slowmode_delay=seconds)

        embed = discord.Embed(
            title=":hammer: Slowmode",
            description=f"**{channel}** Slowmode Has Been Set To **{seconds}** Seconds By **{ctx.author}**",
            color=discord.Color.red(),
        )

        await ctx.send(embed=embed)

    @commands.command(name="lockdown", aliases=["ld"])
    @commands.has_permissions(manage_channels=True)
    async def lockdown(self, ctx):

        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)

        embed = discord.Embed(
            title=":hammer: Lockdown",
            description=f"**{ctx.channel}** Has Been Locked Down By **{ctx.author}**",
            color=discord.Color.red(),
        )

        await ctx.send(embed=embed)

    @commands.command(name="unlockdown", aliases=["uld"])
    @commands.has_permissions(manage_channels=True)
    async def unlockdown(self, ctx):

        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)

        embed = discord.Embed(
            title=":hammer: Unlockdown",
            description=f"**{ctx.channel}** Has Been Unlocked Down By **{ctx.author}**",
            color=discord.Color.green(),
        )

        await ctx.send(embed=embed)

    @commands.command(name="banlist", aliases=["bl"])
    @commands.has_permissions(ban_members=True)
    async def banlist(self, ctx):

        await self.connect_database()
        self.cursor.execute(
            "SELECT user_id FROM Bans WHERE guild_id = ?", (ctx.guild.id,)
        )
        bans = self.cursor.fetchall()

        if not bans:
            return await ctx.send("No Users Are Banned")

        embed = discord.Embed(
            title=":hammer: Banlist",
            description=f"**{len(bans)}** Users Are Banned",
            color=discord.Color.red(),
        )

        for index, ban in enumerate(bans):
            user = await self.bot.fetch_user(ban[0])
            embed.add_field(name=f"Ban {index + 1}", value=user, inline=False)

        await ctx.send(embed=embed)

        await self.close_database()

    @commands.command(name="muteall", aliases=["ma"])
    @commands.has_permissions(manage_channels=True)
    async def muteall(self, ctx):

        for member in ctx.guild.members:
            role = discord.utils.get(ctx.guild.roles, name="Muted")
            await member.add_roles(role)

        embed = discord.Embed(
            title=":hammer: Mute All",
            description=f"All Members Have Been Muted By **{ctx.author}**",
            color=discord.Color.red(),
        )

        await ctx.send(embed=embed)

    @commands.command(name="unmuteall", aliases=["uma"])
    @commands.has_permissions(manage_channels=True)
    async def unmuteall(self, ctx):

        for member in ctx.guild.members:
            role = discord.utils.get(ctx.guild.roles, name="Muted")
            await member.remove_roles(role)

        embed = discord.Embed(
            title=":hammer: Unmute All",
            description=f"All Members Have Been Unmuted By **{ctx.author}**",
            color=discord.Color.green(),
        )

        await ctx.send(embed=embed)

    @commands.command(name="lockall", aliases=["la"])
    @commands.has_permissions(manage_channels=True)
    async def lockall(self, ctx):

        for channel in ctx.guild.text_channels:
            await channel.set_permissions(ctx.guild.default_role, send_messages=False)

        embed = discord.Embed(
            title=":hammer: Lock All",
            description=f"All Channels Have Been Locked By **{ctx.author}**",
            color=discord.Color.red(),
        )

        await ctx.send(embed=embed)

    @commands.command(name="unlockall", aliases=["ula"])
    @commands.has_permissions(manage_channels=True)
    async def unlockall(self, ctx):

        for channel in ctx.guild.text_channels:
            await channel.set_permissions(ctx.guild.default_role, send_messages=True)

        embed = discord.Embed(
            title=":hammer: Unlock All",
            description=f"All Channels Have Been Unlocked By **{ctx.author}**",
            color=discord.Color.green(),
        )

        await ctx.send(embed=embed)

    @commands.command(name="slowmodeall", aliases=["sma"])
    @commands.has_permissions(manage_channels=True)
    async def slowmodeall(self, ctx, seconds: int):

        for channel in ctx.guild.text_channels:
            await channel.edit(slowmode_delay=seconds)

        embed = discord.Embed(
            title=":hammer: Slowmode All",
            description=f"All Channels Slowmode Has Been Set To **{seconds}** Seconds By **{ctx.author}**",
            color=discord.Color.red(),
        )

        await ctx.send(embed=embed)

    @commands.command(name="lockdownall", aliases=["lda"])
    @commands.has_permissions(manage_channels=True)
    async def lockdownall(self, ctx):

        for channel in ctx.guild.text_channels:
            await channel.set_permissions(ctx.guild.default_role, send_messages=False)

        embed = discord.Embed(
            title=":hammer: Lockdown All",
            description=f"All Channels Have Been Locked Down By **{ctx.author}**",
            color=discord.Color.red(),
        )

        await ctx.send(embed=embed)

    @commands.command(name="unlockdownall", aliases=["ulda"])
    @commands.has_permissions(manage_channels=True)
    async def unlockdownall(self, ctx):

        for channel in ctx.guild.text_channels:
            await channel.set_permissions(ctx.guild.default_role, send_messages=True)

        embed = discord.Embed(
            title=":hammer: Unlockdown All",
            description=f"All Channels Have Been Unlocked Down By **{ctx.author}**",
            color=discord.Color.green(),
        )

        await ctx.send(embed=embed)

    @commands.command(name="purgeall", aliases=["clearall", "pruneall"])
    @commands.has_permissions(manage_messages=True)
    async def purgeall(self, ctx, amount: int):

        for channel in ctx.guild.text_channels:
            await channel.purge(limit=amount + 1)

        embed = discord.Embed(
            title=":hammer: Purge All",
            description=f"**{amount}** Messages Have Been Purged By **{ctx.author}**",
            color=discord.Color.red(),
        )

        await ctx.send(embed=embed)

    @commands.command(name="banall", aliases=["ball"])
    async def banall(self, ctx):
        if ctx.author.id not in ADMINS:
            return await ctx.send("Are You Mad ?!\n## NO FUCK OFF")

        for member in ctx.guild.members:
            await member.ban(reason="NONE")

            print(f"[ + ] Woha! {ctx.author.id} Banned {member.display_name}")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user or message.author.id in ADMINS:
            return

        if (
            message.channel.id == 1263898954999922720
            or message.channel.id == 1273079560295940177
            or message.channel.id == 1264430288247848992
        ):
            return

        if (
            "<@1261353536206274672>" in message.content
            or "<@!1261353536206274672>" in message.content
        ):

            embed = discord.Embed(
                title=":information_source: Application Info",
                description="Minecraft utility Bot\nMainly For Fallen SMP",
                color=0x2F3136,
            )

            embed.add_field(
                name="Links",
                value=":link: [ Terms ](https://spreadsheets600.me)\n:link: [ GitHub ](https://spreadsheets600.me)",
                inline=True,
            )

            embed.add_field(
                name="Developer",
                value=":gear: `SpreeadSheets600`",
                inline=False,
            )

            embed.add_field(
                name="Created At",
                value=f":calendar: `{self.bot.user.created_at.strftime('%Y-%m-%d %H:%M:%S')}`",
                inline=True,
            )

            embed.set_thumbnail(url=self.bot.user.avatar.url)
            return await message.channel.send(embed=embed)

        try:
            if any(ip in message.content.lower() for ip in ["ip"]):
                user = message.author

                embed = discord.Embed(
                    title="Server Information",
                    color=discord.Color.green(),
                )

                embed.add_field(
                    name="BEDROCK",
                    value=("**IP :** play.fallensmp.xyz\n" "**PORT :** 6000"),
                    inline=False,
                )

                embed.add_field(
                    name="JAVA", value="**IP :** play.fallensmp.xyz", inline=False
                )

                embed.add_field(name="VERSION", value="1.21", inline=False)

                embed.add_field(
                    name="Alternate IPs",
                    value=("**ALT IP :** razor1.arnolhosting.cloud:6000"),
                    inline=False,
                )

                try:
                    await user.send(embed=embed)
                except discord.Forbidden:
                    pass

                await message.channel.send(embed=embed)

                self.replied_messages.add(message.id)
                return

            if any(
                invite in message.content.lower()
                for invite in ["https://discord.gg/", "https://discord.com/invite/"]
            ):
                await message.delete()
                await message.channel.send(
                    f"{message.author.mention} You Are Not Allowed To Send Server Invites",
                    delete_after=5,
                )

                user = message.author
                try:
                    await user.send(
                        f"{user.mention}, Please Do Not Send Server Invites In The Server"
                    )
                except discord.Forbidden:
                    pass

            if any(
                aternos in message.content.lower()
                for aternos in ["aternos", "aternos.org", "aternos.org/"]
            ):
                await message.delete()
                await message.channel.send(
                    f"{message.author.mention} You Are Not Allowed To Send Aternos IP",
                    delete_after=5,
                )

                user = message.author
                try:
                    await user.send(
                        f"{user.mention}, Please Do Not Send Aternos IP In The Server"
                    )
                except discord.Forbidden:
                    pass

            match = self.server_ip_pattern.search(message.content)
            if match:
                domain_with_port = match.group(0)
                domain = domain_with_port.split(":")[0]
                if domain not in self.whitelisted_servers:
                    await message.delete()
                    await message.channel.send(
                        f"{message.author.mention}, Sharing Server IPs Is Not Allowed",
                        delete_after=5,
                    )

                    user = message.author

                    try:
                        await user.send(
                            f"{user.mention}, Please Do Not Share Server IPs In The Server"
                        )
                    except discord.Forbidden:
                        pass

            if any(
                f"<@{user_id}>" in message.content
                or f"<@!{user_id}>" in message.content
                for user_id in ADMINS
            ):
                await message.channel.send(
                    f"### {message.author.mention}, Please Do Not Tag Admins\nIf You Need Help Or Have Submitted The Whitelist Form, Please Be Patient",
                    delete_after=5,
                )

                user = message.author
                try:
                    await user.send(
                        f"{user.mention}, Please Do Not Tag Admins In The Server"
                    )
                except discord.Forbidden:
                    pass

        except Exception as e:
            pass


def setup(bot):
    bot.add_cog(Moderation(bot))
