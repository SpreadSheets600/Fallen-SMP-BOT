import os
import json
import base64
import discord
import aiohttp
import datetime
import traceback
from io import BytesIO
from discord.ext import bridge
from mcstatus import JavaServer
from discord.ext import commands, tasks
from COGS.Whitelist import COOLDOWN_ACTIVE
from discord.ext.bridge import BridgeSlashGroup

STATUS_FILE = "ServerStatus.json"
ERROR_CHANNEL = 1275759089024241797

if os.path.exists(STATUS_FILE):
    with open(STATUS_FILE, "r") as f:
        data = json.load(f)
        status_message_ids = data.get("status_message_ids", [])
        status_channel_ids = data.get("status_channel_ids", [])
else:
    status_message_ids = []
    status_channel_ids = []


def get_server_status(host, port=25565):
    server = JavaServer.lookup(f"{host}:{port}")
    server_direct = JavaServer(host=host, port=port)

    try:
        status = server.status()
        player_count = status.players.online
        motd = status.description
        latency = status.latency

        try:
            query = server.query()
            player_list = query.players.names
            map_name = query.map
            version = query.software.version
        except Exception:
            player_list = []
            map_name = "Unknown"
            version = "Unknown"

        return server_direct.status()

    except Exception:
        return {"online": False}


async def get_website_status(url):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=10) as response:
                latency = response.elapsed.total_seconds() * 1000
                if response.status == 200:
                    return {"online": True, "latency": latency}
                else:
                    return {"online": False}
        except aiohttp.ClientError:
            return {"online": False}


class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_status.start()

        global COOLDOWN_ACTIVE
        self.COOLDOWN_ACTIVE = COOLDOWN_ACTIVE

        print("[ + ] Status COG : COOLDOWN STATUS : ", self.COOLDOWN_ACTIVE)

    @commands.slash_command(
        name="status",
        description="Get The Status Of A Minecraft Server",
    )
    async def status(self, ctx):
        await ctx.defer(ephemeral=True)

        server_info = get_server_status(host="pre-01.gbnodes.host", port=25610)

        if server_info:
            embed = discord.Embed(
                title=":green_circle: server Status - Online", color=0x00FF00
            )
            embed.description = "|---------------------|\n|    **Fallen SMP** - **1.21.x**   |\n|    **Uncharted Territory**    |\n|---------------------|"
            embed.set_author(name="FALLEN SMP")
            embed.add_field(
                name="Players", value=server_info.players.online, inline=True
            )
            embed.add_field(
                name="Version",
                value=server_info.version.name.split(" ")[1],
                inline=True,
            )
            embed.add_field(
                name="Software",
                value=server_info.version.name.split(" ")[0],
                inline=True,
            )
            embed.add_field(
                name="Latency", value=f"{server_info.latency:.2f} ms", inline=True
            )
            embed.add_field(
                name="Server IP", value="IP : `play.fallensmp.xyz`", inline=False
            )
            embed.add_field(
                name="Server Website", value="https://fallensmp.xyz", inline=False
            )

            icon_base64 = server_info.icon
            if icon_base64:
                image_data = base64.b64decode(icon_base64.split(",")[1])
                image = BytesIO(image_data)
                image.seek(0)
                file = discord.File(image, filename="ICON.png")
                embed.set_thumbnail(url="attachment://ICON.png")

            embed.set_footer(text=f"Last Updated ")
            embed.timestamp = datetime.datetime.now()

            await ctx.send(embed=embed, file=file)
        else:
            embed = discord.Embed(
                title=":red_circle: Server Status - Offline", color=0xFF0000
            )
            embed.description = "|---------------------|\n|    **Fallen SMP** - **1.21.x**   |\n|    **Uncharted Territory**    |\n|---------------------|"
            embed.set_author(name="FALLEN SMP")
            embed.add_field(name="Players", value="0", inline=True)
            embed.add_field(name="Version", value="Unknown", inline=True)
            embed.add_field(name="Software", value="Unknown", inline=True)
            embed.add_field(name="Latency", value="Unknown", inline=True)
            embed.add_field(
                name="Server IP", value="IP : `play.fallensmp.xyz`", inline=False
            )
            embed.add_field(
                name="Server Website", value="https://fallensmp.xyz", inline=False
            )

            await ctx.send(embed=embed)

    @commands.slash_command(
        name="permstatus",
        description="Get The Permanent Status Of A Minecraft Server",
    )
    async def permstatus(self, ctx):
        await ctx.defer(ephemeral=True)

        if ctx.author.id != 727012870683885578:
            await ctx.send("Right Now This Command Is Only Available To SOHAM")
        else:
            status_message = await ctx.send(
                "Setting Up The Permanent Status Message .... "
            )

            status_message_ids.append(status_message.id)
            status_channel_ids.append(status_message.channel.id)

            with open(STATUS_FILE, "w") as f:
                json.dump(
                    {
                        "status_message_ids": status_message_ids,
                        "status_channel_ids": status_channel_ids,
                    },
                    f,
                )
            await status_message.add_reaction("✅")
            await self.update_status()

    @tasks.loop(seconds=60)
    async def update_status(self):
        if COOLDOWN_ACTIVE:
            print("[ - ] Status COG : Cooldown Active")
            return
        
        for message_id, channel_id in zip(status_message_ids, status_channel_ids):
            channel = self.bot.get_channel(channel_id)

            if channel is None:
                continue

            try:
                message = await channel.fetch_message(message_id)
                server_info = get_server_status(host="in4-b.potenfyr.in", port=25565)

                if server_info:
                    embed = discord.Embed(
                        title=":green_circle: Server Status - Online", color=0x00FF00
                    )
                    embed.description = "|---------------------|\n|    **Fallen SMP** - **1.21.x**   |\n|    **Uncharted Territory**    |\n|---------------------|"
                    embed.set_author(name="FALLEN SMP")

                    try:
                        embed.add_field(
                            name="Players",
                            value=server_info.players.online,
                            inline=True,
                        )
                    except Exception:
                        embed.add_field(name="Players", value="--", inline=True)

                    try:
                        embed.add_field(
                            name="Version",
                            value=server_info.version.name.split(" ")[1],
                            inline=True,
                        )
                    except Exception:
                        embed.add_field(
                            name="Version",
                            value="1.21",
                            inline=True,
                        )
                    
                    try:
                        embed.add_field(
                            name="Software",
                            value=server_info.version.name.split(" ")[0],
                            inline=True,
                        )
                    except Exception:
                        embed.add_field(
                            name="Software",
                            value="Paper",
                            inline=True,
                        )

                    try:
                        embed.add_field(
                            name="Latency",
                            value=f"{server_info.latency:.2f} ms",
                            inline=True,
                        )
                    except Exception:
                        embed.add_field(
                            name="Latency",
                            value="--",
                            inline=True,
                        )

                    embed.add_field(
                        name="Server IP",
                        value="IP : `play.fallensmp.xyz`",
                        inline=False,
                    )
                    embed.add_field(
                        name="Server Website",
                        value="https://fallensmp.xyz",
                        inline=False,
                    )

                    try:
                        icon_base64 = server_info.icon

                        if icon_base64:
                            image_data = base64.b64decode(icon_base64.split(",")[1])
                            image = BytesIO(image_data)
                            image.seek(0)
                            file = discord.File(image, filename="ICON.png")
                            embed.set_thumbnail(url="attachment://ICON.png")

                    except Exception:
                        pass

                    embed.set_footer(text=f"Updates Every 60 Seconds | Last Updated ")
                    embed.timestamp = datetime.datetime.now()

                    if icon_base64:
                        await message.edit(content="", embed=embed, file=file)

                    else:
                        await message.edit(content="", embed=embed)
                else:
                    embed = discord.Embed(
                        title=":red_circle: Server Status - Offline", color=0xFF0000
                    )
                    embed.description = "|---------------------|\n|    **Fallen SMP** - **1.21.x**   |\n|    **Uncharted Territory**    |\n|---------------------|"
                    embed.set_author(name="FALLEN SMP")
                    embed.add_field(name="Players", value="0", inline=True)
                    embed.add_field(name="Version", value="Unknown", inline=True)
                    embed.add_field(name="Software", value="Unknown", inline=True)
                    embed.add_field(name="Latency", value="Unknown", inline=True)
                    embed.add_field(
                        name="Server IP",
                        value="IP : `play.fallensmp.xyz`",
                        inline=False,
                    )
                    embed.add_field(
                        name="Server Website",
                        value="https://fallensmp.xyz",
                        inline=False,
                    )

                    await message.edit(content="", embed=embed)

            except Exception as e:
                print(f"[ - ] Status COG : Error : {e}")
                traceback.print_exc()

    @commands.Cog.listener()
    async def on_ready(self):
        print("[ + ] Status COG : OnReady")
        if not self.update_status.is_running():
            self.update_status.start()

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.id == 727012870683885578:
            if reaction.emoji == "✅":
                await reaction.message.remove_reaction("✅", user)
                await reaction.message.add_reaction("✅")
                await self.update_status()


def setup(bot):
    bot.add_cog(Status(bot))
