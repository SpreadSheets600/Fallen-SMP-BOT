import os
import json
import time
import random
import pymongo
import discord
import asyncio
import datetime
import traceback
from datetime import datetime
import mysql.connector as mysql
from pymongo import MongoClient
from discord.ext.pages import *
from mysql.connector import Error
from discord.ext.bridge import BridgeSlashGroup
from discord.ext import commands, bridge, pages

# =================================================================================================== #

from dotenv import *

load_dotenv()

# =================================================================================================== #

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
    1261684685235294250,
    1147935418508132423,
]

CONSOLE_CHANNEL = 1263898954999922720
ERROR_CHANNEL = 1275759089024241797

# =================================================================================================== #


def database_connection():
    try:
        connection = mysql.connect(
            host=os.getenv("STATZ_DB_HOST"),
            user=os.getenv("STATZ_DB_USER"),
            password=os.getenv("STATZ_DB_PASS"),
            database=os.getenv("STATZ_DB_NAME"),
        )
        print("[ + ] MySQL Connection Established")

        cursor = connection.cursor()

        return connection, cursor

    except Error as e:
        print(f"[ - ] Error Connecting To MySQL: {e}")
        return None


# =================================================================================================== #


class Player(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.connection, self.cursor = database_connection()

        self.mongo_client = MongoClient(os.getenv("MONGO_URI"))
        self.db = self.mongo_client["Users"]
        self.collection = self.db["UserData"]

    @bridge.bridge_group()
    async def pl(self, ctx):
        pass

    @pl.command(
        name="info",
        description="Get Information About A Player",
    )
    async def pl_info(self, ctx, player: discord.Member):
        await ctx.defer()

        if player == None:
            player = ctx.author

        try:
            document = self.collection.find_one({"ID": player.id})

            if document:
                username = document.get("Username")
                gender = document.get("Gender")
                backstory = document.get("Backstory")
                timestamp = document.get("Timestamp")

                embed = discord.Embed(
                    title="Player Information",
                    description=f"Details For **{player.display_name}**",
                    color=0xDDDDBD,
                )

                embed.add_field(
                    name="Discord User ID",
                    value=f"{document['ID']}",
                    inline=False,
                )

                embed.add_field(name="Minecraft Username", value=username, inline=False)

                try:
                    avatar = player.avatar.url
                    embed.set_thumbnail(url=player.avatar.url)
                except Exception as e:
                    pass

                embed.set_footer(
                    text=f"Fallen SMP | Joined On {timestamp.split(' ')[0]}"
                )

                await ctx.respond(
                    embed=embed,
                    view=View_Character_Info(
                        user_id=player.id,
                        user=player,
                        gender=gender,
                        backstory=backstory,
                    ),
                )

            else:
                embed = discord.Embed(
                    title=":x: Player Data Not Found",
                    description="It Seems Like There Isn't Any Data For You. Make Sure To Submit The Whitelist Application.",
                    color=discord.Color.red(),
                )
                await ctx.respond(embed=embed, ephemeral=True)

        except Exception as e:
            print(f"[ - ] Player COG : Error : {e}")
            await ctx.respond(
                f"[ - ] Player COG : Error : \n```{e}```",
                ephemeral=True,
                delete_after=5,
            )

            ErrorChannel = self.bot.get_channel(ERROR_CHANNEL)
            await ErrorChannel.send(f"[ - ] Player COG : Error : \n```{e}```")

    @pl.command(
        name="stats",
        description="Get Stats About A Player",
    )
    async def pl_stats(self, ctx, player: discord.Member):
        await ctx.defer()

        if player is None:
            player = ctx.author

        def convert_time(seconds):
            minutes = seconds // 60
            hours = minutes // 60
            days = hours // 24

            remaining_hours = hours % 24
            remaining_minutes = minutes % 60

            return days, remaining_hours, remaining_minutes

        try:
            document = self.collection.find_one({"ID": player.id})

            if document:
                username = document.get("Username")

                ConsoleChannel = self.bot.get_channel(CONSOLE_CHANNEL)
                await ConsoleChannel.send(f"zstats update {username}")

                get_uuid = f"SELECT uuid FROM zstat_player WHERE name = '{username}'"
                self.cursor.execute(get_uuid)

                uuid = self.cursor.fetchone()[0]
                self.cursor.nextset()

                stats_dict = {
                    "DAMAGE_TAKEN": 0,
                    "DEATHS": 0,
                    "FISH_CAUGHT": 0,
                    "ITEM_ENCHANTED": 0,
                    "MOB_KILLS": 0,
                    "TOTAL_WORLD_TIME": 0,
                    "RAID_WIN": 0,
                    "TRADED_WITH_VILLAGER": 0,
                    "z:shovel": 0,
                    "z:axe": 0,
                    "z:pickaxe": 0,
                    "z:sword": 0,
                    "z:bow": 0,
                    "z:mob_kind": 0,
                    "z:last_played": 0,
                    "z:mined": 0,
                    "z:crafted": 0,
                    "z:placed": 0,
                    "z:craft_kind": 0,
                    "BALANCE": 0,
                }

                for stat_name in stats_dict.keys():
                    query = f"SELECT val FROM zstat_stats WHERE uuid = '{uuid}' AND stat = '{stat_name}'"

                    self.cursor.execute(query)
                    result = self.cursor.fetchone()

                    if result:
                        stats_dict[stat_name] = result[0]

                embed = discord.Embed(
                    title="Player Statistics",
                    description=f"Stats For **{player.display_name}**",
                    color=0xDDDDBD,
                )

                embed.add_field(
                    name="Deaths",
                    value=f"{stats_dict['DEATHS']}",
                    inline=True,
                )

                embed.add_field(
                    name="Damage Taken",
                    value=f"{stats_dict['DAMAGE_TAKEN']}",
                    inline=True,
                )

                playtime = stats_dict["TOTAL_WORLD_TIME"]
                days, hours, minutes = convert_time(playtime)

                embed.add_field(
                    name=" Mob Killed",
                    value=f"{stats_dict['MOB_KILLS']}",
                    inline=True,
                )

                embed.add_field(
                    name="Mined Blocks",
                    value=f"{stats_dict['z:mined']}",
                    inline=True,
                )

                embed.add_field(
                    name="Crafted Items",
                    value=f"{stats_dict['z:crafted']}",
                    inline=True,
                )

                embed.add_field(
                    name="Placed Blocks",
                    value=f"{stats_dict['z:placed']}",
                    inline=True,
                )

                embed.add_field(
                    name="Total Play Time",
                    value=f"{days} Days, {hours} Hours, {minutes} Minutes",
                    inline=False,
                )

                embed.add_field(
                    name="Items Enchanted",
                    value=f"{stats_dict['ITEM_ENCHANTED']}",
                    inline=False,
                )

                last_played = stats_dict["z:last_played"]
                if last_played:
                    last_played_dt = datetime.utcfromtimestamp(last_played)
                    last_played_discord_ts = f"<t:{int(last_played)}:R>"

                    embed.add_field(
                        name="Last Played",
                        value=last_played_discord_ts,
                        inline=True,
                    )

                await ctx.respond(
                    embed=embed,
                    view=Additional_Statisitcs(
                        user_id=player.id,
                        user=player,
                        stats=stats_dict,
                        username=username,
                        bot=self.bot,
                    ),
                )

            else:
                embed = discord.Embed(
                    title=":x: Player Data Not Found",
                    description="It Seems Like There Isn't Any Data For You. Make Sure To Submit The Whitelist Application.",
                    color=discord.Color.red(),
                )
                await ctx.respond(embed=embed, ephemeral=True)

        except Exception as e:
            print(f"[ - ] Player COG : Error : {e}")
            await ctx.respond(
                f"[ - ] Player COG : Error : \n```{e}```",
                ephemeral=True,
                delete_after=5,
            )

            traceback.print_exc()


# =================================================================================================== #


class View_Character_Info(discord.ui.View):
    def __init__(self, user_id, user, gender, backstory) -> None:
        super().__init__(timeout=None)
        self.backstory = backstory
        self.user_id = user_id
        self.gender = gender
        self.user = user

        self.mongo_client = MongoClient(os.getenv("MONGO_URI"))
        self.db = self.mongo_client["Users"]
        self.collection = self.db["UserData"]

    @discord.ui.button(label="View Character Info", style=discord.ButtonStyle.secondary)
    async def view_button_callback(self, button, interaction):

        embed = discord.Embed(
            title="Character Information",
            description=f"Character Gender : **{self.gender}**\n\n**Character Backstory** : **{self.backstory}**",
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)


# =================================================================================================== #


class Additional_Statisitcs(discord.ui.View):
    def __init__(self, user_id, user, stats, username, bot) -> None:
        super().__init__(timeout=None)
        self.username = username
        self.user_id = user_id
        self.stats = stats
        self.user = user
        self.bot = bot

    @discord.ui.button(
        label="View Additional Stats", style=discord.ButtonStyle.secondary
    )
    async def view_button_callback(self, button, interaction):

        embed = discord.Embed(
            title="Additional Statistics",
            description=f"Additional Statistics {self.user.display_name}",
            color=0xDDDDBD,
        )

        embed.add_field(
            name="Fish Caught",
            value=f"{self.stats['FISH_CAUGHT']}",
            inline=True,
        )

        embed.add_field(
            name="Raid Wins",
            value=f"{self.stats['RAID_WIN']}",
            inline=True,
        )

        embed.add_field(
            name="Villager Trades",
            value=f"{self.stats['TRADED_WITH_VILLAGER']}",
            inline=True,
        )

        embed.add_field(
            name="Shovel Used",
            value=f"{self.stats['z:shovel']}",
            inline=True,
        )

        embed.add_field(
            name="Axe Used",
            value=f"{self.stats['z:axe']}",
            inline=True,
        )

        embed.add_field(
            name="Pickaxe Used",
            value=f"{self.stats['z:pickaxe']}",
            inline=True,
        )

        embed.add_field(
            name="Sword Used",
            value=f"{self.stats['z:sword']}",
            inline=True,
        )

        embed.add_field(
            name="Bow Used",
            value=f"{self.stats['z:bow']}",
            inline=True,
        )

        embed.add_field(
            name="Mobs Of Kinds",
            value=f"{self.stats['z:mob_kind']}",
            inline=True,
        )

        embed.add_field(
            name="Craft Kinds",
            value=f"{self.stats['z:craft_kind']}",
            inline=True,
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Balance", style=discord.ButtonStyle.secondary)
    async def balance_button_callback(self, button, interaction):

        await interaction.response.defer(ephemeral=True)
        msg_id = await interaction.followup.send("Fetching Balance...", ephemeral=True)

        chan_id = interaction.channel_id

        ConsoleChannel = self.bot.get_channel(CONSOLE_CHANNEL)
        sent_message = await ConsoleChannel.send(f"bal {self.username}")

        def check(message):
            return (
                message.channel.id == CONSOLE_CHANNEL
                and message.reference
                and message.reference.message_id == sent_message.id
            )

        try:
            message = await self.bot.wait_for("message", check=check, timeout=5.0)
        except asyncio.TimeoutError:
            await interaction.response.send_message(
                "Timeout : No Response Received.", ephemeral=True
            )
            return

        print(message.content)

        if message.content:

            msg = message.content.split(" ")

            balance_raw = msg[-1][1:]
            balance = balance_raw.replace(",", "")

            balance = int(balance)
            balance = round(balance)

            embed = discord.Embed(
                title="Balance",
                description=f"Balance Of {self.user.display_name}\n\n### Balance : $ {balance}",
                color=0xDDDDBD,
            )

            await interaction.followup.send(embed=embed, ephemeral=True)

        else:
            await interaction.followup.send(
                "Balance Could Not Be Fetched", ephemeral=True
            )


# =================================================================================================== #


def setup(bot):
    bot.add_cog(Player(bot))
