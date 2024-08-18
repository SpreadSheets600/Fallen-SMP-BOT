import re
import discord
import sqlite3
from discord.ext import commands
from discord.commands import SlashCommandGroup
from discord.ui.item import Item

ADMINS = [
    727012870683885578,
    437622938242514945,
    243042987922292738,
    664157606587138048,
    1188730953217097811,
    896411007797325824,
    1147935418508132423,
    1261684685235294250,
]


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.whitelist_patterns = [
            re.compile(r"\bwhitelist\s?me\b", re.IGNORECASE),
            re.compile(r"\bwhitelist\s?kardo\b", re.IGNORECASE),
            re.compile(r"\bwhitelist\s?please\b", re.IGNORECASE),
            re.compile(r"(?=.*\bwhitelist\b)(?=.*\bkardo\b)", re.IGNORECASE),
            re.compile(r"(?=.*\bwhitelist\b)(?=.*\bplease\b)", re.IGNORECASE),
            re.compile(r"\bwhitelist\s?kar\s?do\b", re.IGNORECASE),
            re.compile(r"\bwhitelist\s?plz\b", re.IGNORECASE),
        ]

        self.backstory_patterns = [
            re.compile(r"\bbackstory\b", re.IGNORECASE),
            re.compile(r"\bback\s?story\b", re.IGNORECASE),
            re.compile(r"\bbackstory\s?samaj\s?nehi\b", re.IGNORECASE),
            re.compile(r"\bbackstory\s?samjha\s?nehi\b", re.IGNORECASE),
            re.compile(r"\bbackstory\s?explain\b", re.IGNORECASE),
            re.compile(r"\bbackstory\s?samaj\s?nehi\b", re.IGNORECASE),
            re.compile(
                r"(?=.*\backstory\b)(?=.*\bkaya\b)(?=.*\blikhu\b)", re.IGNORECASE
            ),
        ]

        self.whitelist_already_patterns = [
            re.compile(r"\bwhitelist\s?already\b", re.IGNORECASE),
            re.compile(r"\bwhitelist\s?ho\s?gaya\b", re.IGNORECASE),
            re.compile(r"(?=.*\bwhitelist\b)(?=.*\bacceptet\b)", re.IGNORECASE),
            re.compile(
                r"(?=.*\bwhitelist\b)(?=.*\bform\b)(?=.*\bsubmitted\b)", re.IGNORECASE
            ),
            re.compile(r"(?=.*\bwhitelist\b)(?=.*\bdone\b)", re.IGNORECASE),
            re.compile(r"(?=.*\bwhitelist\b)(?=.*\bcompleted\b)", re.IGNORECASE),
            re.compile(r"(?=.*\bwhitelist\b)(?=.*\bsubmitted\b)", re.IGNORECASE),
            re.compile(r"\bwhitelist\s?done\b", re.IGNORECASE),
            re.compile(r"\bwhitelist\s?complete\b", re.IGNORECASE),
            re.compile(r"\bwhitelist\s?submitted\b", re.IGNORECASE),
            re.compile(r"\bwhitelist\s?form\s?submitted\b", re.IGNORECASE),
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

        self.replied_messages = set()

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

    @commands.slash_command(name="warnings", description="Shows Warnings Of A User")
    async def show_warnings(self, ctx, member: discord.Member):
        warnings = self.get_warnings(member.id)
        embed = self.create_embed(
            title="Warnings",
            description=f"{member.mention} Has {warnings} Warnings",
        )
        await ctx.send(embed=embed)

    @commands.slash_command(name="clear", description="Clears Messages Of A User")
    async def clear_messages(self, ctx, member: discord.Member, limit: int = 5):
        if ctx.author.id not in ADMINS:
            return await ctx.send(
                "You Are Not Allowed To Use This Command\nSOHAM Must Be Noob To Let You Use This Command"
            )

        await ctx.channel.purge(
            limit=limit, check=lambda msg: msg.author == member, bulk=True
        )

        embed = self.create_embed(
            title="Messages Cleared",
            description=f"{limit} Messages Of {member.mention} Have Been Cleared",
        )
        await ctx.send(embed=embed, delete_after=5)

    @commands.slash_command(name="purge", description="Clears Messages In A Channel")
    async def purge_messages(self, ctx, limit: int = 5):
        if ctx.author.id not in ADMINS:
            return await ctx.send(
                "You Are Not Allowed To Use This Command\nSOHAM Must Be Noob To Let You Use This Command"
            )

        await ctx.channel.purge(limit=limit, bulk=True)

        embed = self.create_embed(
            title="Messages Cleared",
            description=f"{limit} Messages Have Been Cleared",
        )
        await ctx.send(embed=embed, delete_after=5)

    @commands.slash_command(name="kick", description="Kicks A User")
    async def kick_user(
        self, ctx, member: discord.Member, *, reason: str = "No Reason Provided"
    ):
        if ctx.author.id not in ADMINS:
            return await ctx.send(
                "You Are Not Allowed To Use This Command\nSOHAM Must Be Noob To Let You Use This Command"
            )

        await member.kick(reason=reason)
        embed = self.create_embed(
            title="Kicked",
            description=f"{member.mention} Has Been Kicked\n### Reason: {reason}",
        )
        await ctx.send(embed=embed)

    @commands.slash_command(name="ban", description="Bans A User")
    async def ban_user(
        self, ctx, member: discord.Member, *, reason: str = "No Reason Provided"
    ):
        if ctx.author.id not in ADMINS:
            return await ctx.send(
                "You Are Not Allowed To Use This Command\nSOHAM Must Be Noob To Let You Use This Command"
            )

        await member.ban(reason=reason)
        embed = self.create_embed(
            title="Banned",
            description=f"{member.mention} Has Been Banned\n### Reason: {reason}",
        )
        await ctx.send(embed=embed)

    @commands.slash_command(name="unban", description="Unbans A User")
    async def unban_user(
        self, ctx, member: discord.Member, *, reason: str = "No Reason Provided"
    ):
        if ctx.author.id not in ADMINS:
            return await ctx.send(
                "You Are Not Allowed To Use This Command\nSOHAM Must Be Noob To Let You Use This Command"
            )

        await member.unban(reason=reason)
        embed = self.create_embed(
            title="Unbanned",
            description=f"{member.mention} Has Been Unbanned\n### Reason: {reason}",
        )
        await ctx.send(embed=embed)

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

        if message.id in self.replied_messages:
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
            for pattern in self.whitelist_already_patterns:
                if pattern.search(message.content):

                    user = message.author

                    try:
                        await user.send(
                            f"### {user.mention}, Please Be Patient, Your Form Will Be Reviewed Soon"
                        )

                    except discord.Forbidden:
                        pass

                    await message.channel.send(
                        f"### {user.mention}, Please Be Patient, Your Form Will Be Reviewed Soon"
                    )

                    self.replied_messages.add(message.id)
                    return

            for pattern in self.whitelist_patterns:
                if pattern.search(message.content):

                    user = message.author

                    try:
                        await user.send(
                            f"{user.mention}, Please Watch The Video Below For Whitelisting Process\nhttps://cdn.discordapp.com/attachments/1195302501797343243/1273306886728585420/Whitelist.mp4?ex=66c0c5f2&is=66bf7472&hm=437a8e1b02dfb3ef02f45cc827f513f024e5820483ba014515bccb716018e560&"
                        )

                    except discord.Forbidden:
                        pass

                    await message.channel.send(
                        f"{user.mention} Please Watch The Video Below For Whitelisting Process\nhttps://cdn.discordapp.com/attachments/1195302501797343243/1273306886728585420/Whitelist.mp4?ex=66c0c5f2&is=66bf7472&hm=437a8e1b02dfb3ef02f45cc827f513f024e5820483ba014515bccb716018e560&"
                    )

                    self.replied_messages.add(message.id)
                    return

            for pattern in self.backstory_patterns:
                if pattern.search(message.content):

                    user = message.author

                    embed = discord.Embed(
                        title="Guide to Creating a Backstory for Your Character",
                        description=(
                            "A backstory is like a character's secret life. It's all the stuff that happened before the story starts. "
                            "It helps shape who they are and why they do the things they do.\n\n"
                            "Here's how to create one:"
                        ),
                        color=discord.Color.blue(),
                    )

                    embed.add_field(
                        name="**Who are they?**",
                        value=(
                            " - What's their name, age, and where are they from?\n"
                            " - What do they look like?\n"
                            " - What's their personality like? Are they shy, brave, funny, or something else?"
                        ),
                        inline=False,
                    )

                    embed.add_field(
                        name="**What's their story?**",
                        value=(
                            " - Think about big events in their life. Did something bad happen? Did they have a great childhood?\n"
                            " - What are their dreams and goals?\n"
                            " - What are they afraid of?"
                        ),
                        inline=False,
                    )

                    embed.add_field(
                        name="**How do they act?**",
                        value=(
                            " - Their past shapes how they behave.\n"
                            " - Did a bad experience make them mistrustful?\n"
                            " - Did a happy childhood make them optimistic?"
                        ),
                        inline=False,
                    )

                    try:
                        await user.send(embed=embed, view=BackstoryExample())

                    except Exception as e:
                        pass

                    await message.channel.send(embed=embed, view=BackstoryExample())

                    self.replied_messages.add(message.id)
                    return

            if any(ip in message.content.lower() for ip in ["ip"]):
                user = message.author

                embed = discord.Embed(
                    title="Server Information",
                    color=discord.Color.green(),
                )

                embed.add_field(
                    name="BEDROCK",
                    value=("**IP :** play.fallensmp.xyz\n" "**PORT :** 25671"),
                    inline=False,
                )

                embed.add_field(
                    name="JAVA", value="**IP :** play.fallensmp.xyz", inline=False
                )

                embed.add_field(name="VERSION", value="1.21", inline=False)

                embed.add_field(
                    name="Alternate IPs",
                    value=(
                        "**ALT IP 1 :** pre-01.gbnodes.host:25610\n"
                        "**ALT IP 2 :** fallenrp.gbnodes.host"
                    ),
                    inline=False,
                )

                try:
                    await user.send(embed=embed, view=IPButtons())
                except discord.Forbidden:
                    pass

                await message.channel.send(embed=embed, view=IPButtons())

                self.replied_messages.add(message.id)
                return

            if any(backstory in message.content.lower() for backstory in ["backstory"]):
                user = message.author

                embed = discord.Embed(
                    title="Guide to Creating a Backstory for Your Character",
                    description=(
                        "A backstory is like a character's secret life. It's all the stuff that happened before the story starts. "
                        "It helps shape who they are and why they do the things they do.\n\n"
                        "Here's how to create one:"
                    ),
                    color=discord.Color.blue(),
                )

                embed.add_field(
                    name="**Who are they?**",
                    value=(
                        " - What's their name, age, and where are they from?\n"
                        " - What do they look like?\n"
                        " - What's their personality like? Are they shy, brave, funny, or something else?"
                    ),
                    inline=False,
                )

                embed.add_field(
                    name="**What's their story?**",
                    value=(
                        " - Think about big events in their life. Did something bad happen? Did they have a great childhood?\n"
                        " - What are their dreams and goals?\n"
                        " - What are they afraid of?"
                    ),
                    inline=False,
                )

                embed.add_field(
                    name="**How do they act?**",
                    value=(
                        " - Their past shapes how they behave.\n"
                        " - Did a bad experience make them mistrustful?\n"
                        " - Did a happy childhood make them optimistic?"
                    ),
                    inline=False,
                )

                try:

                    await user.send(embed=embed, view=BackstoryExample())

                except Exception as e:
                    pass

                await message.channel.send(embed=embed, view=BackstoryExample())

                self.replied_messages.add(message.id)
                return

            if any(whitelist in message.content.lower() for whitelist in ["whitelist"]):
                user = message.author

                try:
                    await user.send(
                        f"{user.mention}, Please Watch The Video Below For Whitelisting Process\nhttps://cdn.discordapp.com/attachments/1195302501797343243/1273306886728585420/Whitelist.mp4?ex=66c0c5f2&is=66bf7472&hm=437a8e1b02dfb3ef02f45cc827f513f024e5820483ba014515bccb716018e560&"
                    )

                except discord.Forbidden:
                    pass

                await message.channel.send(
                    f"{user.mention} Please Watch The Video Below For Whitelisting Process\nhttps://cdn.discordapp.com/attachments/1195302501797343243/1273306886728585420/Whitelist.mp4?ex=66c0c5f2&is=66bf7472&hm=437a8e1b02dfb3ef02f45cc827f513f024e5820483ba014515bccb716018e560&"
                )

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

            messages = await message.channel.history(
                limit=10, oldest_first=False
            ).flatten()
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

        except Exception as e:
            user_id = 727012870683885578
            user = self.bot.get_user(user_id)

            await user.send(
                f"### Error In Moderation.py\n### Error: {e}\n### Server: {message.guild.name}\n### Channel: {message.channel.name}\n### User: {message.author}\n### Message: {message.content}"
            )

    def create_embed(self, title, description):
        return discord.Embed(title=title, description=description, color=0xFF0000)


class IPButtons(discord.ui.View):
    def __init__(
        self,
        *items: Item,
        timeout: float | None = 180,
        disable_on_timeout: bool = False,
    ):
        super().__init__(*items, timeout=timeout, disable_on_timeout=disable_on_timeout)

    @discord.ui.button(label="Alternate IPs", style=discord.ButtonStyle.secondary)
    async def alternate_ips(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        embed = discord.Embed(
            title="Alternate IPs",
            description=(
                "**ALT IP 1 :** pre-01.gbnodes.host:25610\n"
                "**ALT IP 2 :** fallenrp.gbnodes.host"
            ),
            color=discord.Color.green(),
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Version", style=discord.ButtonStyle.secondary)
    async def version(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        embed = discord.Embed(
            title="Version",
            description="## 1.21",
            color=discord.Color.green(),
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)


class BackstoryExample(discord.ui.View):
    def __init__(
        self,
        *items: Item,
        timeout: float | None = 180,
        disable_on_timeout: bool = False,
    ):
        super().__init__(*items, timeout=timeout, disable_on_timeout=disable_on_timeout)

    @discord.ui.button(label="Backstory Example", style=discord.ButtonStyle.primary)
    async def backstory_example(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        
        embed = discord.Embed(
            title="Backstory Example",
            color=discord.Color.blue(),
        )

        embed.description = (
            "**Character **: A tough, mysterious detective.\n"
            "**Backstory **: Grew up in a rough neighbourhood, lost a close friend to crime, became a detective to fight for justice.\n\n"
        )

        embed.add_field (
            name="Important",
            value=(
                " * Your backstory doesn't have to be super long or complicated.\n"
                " * The most important thing is that it helps you understand your character better.\n"
                " * Have fun with it! You can be as creative as you want.\n\n"
            ),
            inline=False
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)


def setup(bot):
    bot.add_cog(Moderation(bot))
