import re
import discord
import sqlite3
from datetime import timedelta
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
                    value=("**IP :** play.fallensmp.xyz\n" "**PORT :** 25565"),
                    inline=False,
                )

                embed.add_field(
                    name="JAVA", value="**IP :** play.fallensmp.xyz", inline=False
                )

                embed.add_field(name="VERSION", value="1.21", inline=False)

                embed.add_field(
                    name="Alternate IPs",
                    value=(
                        "**ALT IP :** in4-b.potenfyr.in"
                    ),
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