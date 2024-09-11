import time
import discord
import datetime
from discord.ext import commands

LOG_CHANNEL_ID = 1275759089024241797


class CommandLogger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_application_command(self, ctx: discord.ApplicationContext):
        log_channel = self.bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            user = ctx.user
            command = ctx.command
            current_time = int(time.time())

            embed = discord.Embed(
                title="Slash Command Executed",
                description=(
                    f"**User :** {user.mention} ( `{user.id}` )\n\n"
                    f"**Command :** `{command}`\n"
                    f"**Channel :** {ctx.channel.mention}\n\n"
                    f"**Time :** <t:{current_time}:F>"
                ),
                color=discord.Color.blue(),
            )

        if user.avatar.url:
            embed.set_thumbnail(url=user.avatar.url)

        else:
            pass

        await log_channel.send(embed=embed)


def setup(bot):
    bot.add_cog(CommandLogger(bot))
