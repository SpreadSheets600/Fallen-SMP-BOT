import re
import discord
import sqlite3
from discord.ext import commands
from discord.commands import SlashCommandGroup

ADMINS = [
    727012870683885578,
    437622938242514945,
    243042987922292738,
    664157606587138048,
    1188730953217097811,
    896411007797325824,
]


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.whitelist_patterns = [
            re.compile(r"\bwhitelist\s?me\b", re.IGNORECASE),
            re.compile(r"\bwhitelist\s?kardo\b", re.IGNORECASE),
            re.compile(r"\bwhitelist\s?please\b", re.IGNORECASE),
            re.compile(r"\bwhitelist\s?kar\s?do\b", re.IGNORECASE)
        ]

        self.server_ip_pattern = re.compile(
            r"\b(?:[a-zA-Z0-9-]+\.){2}[a-zA-Z0-9-]+(?::\d{1,5})?\b"
        )

        self.whitelisted_servers = [
            "play.fallensmp.xyz",
            "fallenrp.gbnodes.host",
            "pre-01.gbnodes.host:25610",
        ]

        self.conn = sqlite3.connect("Moderation.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS warnings (
                               user_id INTEGER PRIMARY KEY,
                               count INTEGER DEFAULT 0)"""
        )
        self.conn.commit()

    def cog_unload(self):
        self.conn.close()

    def get_warnings(self, user_id):
        self.cursor.execute("SELECT count FROM warnings WHERE user_id = ?", (user_id,))
        result = self.cursor.fetchone()
        return result[0] if result else 0

    def add_warning(self, user_id):
        warnings = self.get_warnings(user_id)
        if warnings == 0:
            self.cursor.execute(
                "INSERT INTO warnings (user_id, count) VALUES (?, ?)", (user_id, 1)
            )
        else:
            self.cursor.execute(
                "UPDATE warnings SET count = ? WHERE user_id = ?",
                (warnings + 1, user_id),
            )
        self.conn.commit()
        return warnings + 1

    Warning = SlashCommandGroup(
        name="warning",
        description="Commands To Warn Users",
    )

    @Warning.command(name="give", description="Warns A User")
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member):

        warnings = self.add_warning(member.id)
        if warnings == 1:
            await member.timeout_for(
                discord.utils.utcnow() + discord.timedelta(minutes=10),
                reason="Received A Warning",
            )
            embed = self.create_embed(
                title="Warning",
                description=f"{member.mention} Received A Warning\n### Total Warnings : {warnings}",
            )
            await ctx.send(embed=embed)
        elif warnings == 3:
            await member.kick(reason="Received 3 Warnings")
            embed = self.create_embed(
                title="Warning",
                description=f"{member.mention} Received 3 Warnings And Has Been Kicked",
            )
            await ctx.send(embed=embed)
        elif warnings > 3:
            await member.ban(reason="Received More Than 3 Warnings.")
            embed = self.create_embed(
                title="Warning",
                description=f"{member.mention} Received More Than 3 Warnings And Has Been Banned",
            )
            await ctx.send(embed=embed)
        else:
            embed = self.create_embed(
                title="Warning",
                description=f"{member.mention} Received A Warning\n### Total Warnings : {warnings}",
            )
            await ctx.send(embed=embed)

    @Warning.command(name="reset", description="Resets Warnings Of A User")
    @commands.has_permissions(manage_messages=True)
    async def reset_warnings(self, ctx, member: discord.Member):
        self.cursor.execute("DELETE FROM warnings WHERE user_id = ?", (member.id,))
        self.conn.commit()

        embed = self.create_embed(
            title="Warning",
            description=f"{member.mention}'s Warnings Have Been Reset",
        )

        await ctx.send(embed=embed)

    @commands.command(name="warnings", description="Shows Warnings Of A User")
    async def show_warnings(self, ctx, member: discord.Member):
        warnings = self.get_warnings(member.id)
        embed = self.create_embed(
            title="Warnings",
            description=f"{member.mention} Has {warnings} Warnings",
        )
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user or message.author.id in ADMINS:
            return

        for pattern in self.whitelist_patterns:
            if pattern.search(message.content):

                await message.channel.send(
                    f"{user.mention} Please Watch The Video Below For Whitelisting Process\nhttps://cdn.discordapp.com/attachments/1195302501797343243/1273306886728585420/Whitelist.mp4?ex=66c0c5f2&is=66bf7472&hm=437a8e1b02dfb3ef02f45cc827f513f024e5820483ba014515bccb716018e560&"
                )

                user = message.author
                try:
                    await user.send(
                        f"{user.mention}, Please Watch The Video Below For Whitelisting Process\nhttps://cdn.discordapp.com/attachments/1195302501797343243/1273306886728585420/Whitelist.mp4?ex=66c0c5f2&is=66bf7472&hm=437a8e1b02dfb3ef02f45cc827f513f024e5820483ba014515bccb716018e560&"
                    )
                except discord.Forbidden:
                    pass

        if "whitelist" in message.content.lower():

            await message.channel.send(
                f"{user.mention} Please Watch The Video Below For Whitelisting Process\nhttps://cdn.discordapp.com/attachments/1195302501797343243/1273306886728585420/Whitelist.mp4?ex=66c0c5f2&is=66bf7472&hm=437a8e1b02dfb3ef02f45cc827f513f024e5820483ba014515bccb716018e560&"
            )

            user = message.author
            try:
                await user.send(
                    f"{user.mention}, Please Watch The Video Below For Whitelisting Process\nhttps://cdn.discordapp.com/attachments/1195302501797343243/1273306886728585420/Whitelist.mp4?ex=66c0c5f2&is=66bf7472&hm=437a8e1b02dfb3ef02f45cc827f513f024e5820483ba014515bccb716018e560&"
                )
            except discord.Forbidden:
                pass

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
            f"<@{user_id}>" in message.content or f"<@!{user_id}>" in message.content
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

        if all(
            keyword in message.content.lower()
            for keyword in ["submitted", "already", "form"]
        ):
            await message.channel.send(
                f"### {message.author.mention}, If You Have Submitted The Form, Please Be Patient\n### Your Form Will Be Reviewed Soon And Accepted If You Meet The Requirements",
                delete_after=5,
            )

            user = message.author
            try:
                await user.send(
                    f"{user.mention}, Please Be Patient, Your Form Will Be Reviewed Soon"
                )
            except discord.Forbidden:
                pass

        messages = await message.channel.history(limit=10, oldest_first=False).flatten()
        user_messages = [
            msg
            for msg in messages
            if msg.author == message.author
            and (discord.utils.utcnow() - msg.created_at).total_seconds() < 10
        ]

        if len(user_messages) >= 5:
            await message.channel.purge(
                limit=5, check=lambda msg: msg.author == message.author
            )

            warnings = self.add_warning(message.author.id)

            embed = self.create_embed(
                title="Spam Detected",
                description=f"{message.author.mention} You Are Sending Messages Too Quickly\n### Please Slow Down\n### Warnings: {warnings}",
            )
            await message.channel.send(embed=embed)

    def create_embed(self, title, description):
        return discord.Embed(title=title, description=description, color=0xFF0000)


def setup(bot):
    bot.add_cog(Moderation(bot))
