import os
import time
import aiohttp

import discord
import COGS.Player
import COGS.Whitelist
from COGS.Player import *
from COGS.Whitelist import *
from datetime import datetime, timedelta
from discord.ext import commands, bridge
from discord.commands import SlashCommandGroup

import mysql.connector as mysql
from mysql.connector import Error

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# =================================================================================================== #

from dotenv import *

load_dotenv()

print("[ + ] Environment Variables Loaded")

# =================================================================================================== #


class MyBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.player_cog = None

    async def setup_hook(self):
        self.player_cog = Player(self)
        await self.add_cog(self.player_cog)


def get_prefix(bot, message):
    prefixes = ["FS!", "fs!"]
    return commands.when_mentioned_or(*prefixes)(bot, message)


intents = discord.Intents.all()
bot = bridge.Bot(command_prefix=get_prefix, intents=intents)

bot.remove_command("help")

# ============================================================================== #

# Database Connection


def connect_to_mongodb():
    try:
        mongo_client = MongoClient(os.getenv("MONGO_URI"))
        mongo_client.admin.command("ping")
        print("[ + ] MongoDB Connection Established")
        return mongo_client
    except ConnectionFailure as e:
        print(f"[ - ] Error Connecting to MongoDB: {e}")
        return None


mongo_client = connect_to_mongodb()

if mongo_client:
    db = mongo_client["Users"]
    collection = db["UserData"]

    sample_data = {
        "ID": 123456789012345678,
        "Username": "SampleUser",
        "Gender": "Male",
        "Backstory": "This is a sample backstory.",
        "Timestamp": "2024-08-22T12:00:00Z",
    }

    collection.insert_one(sample_data)
    print("[ + ] Collection Created with Initial Structure")

    collection.delete_one({"ID": 123456789012345678})

    print("[ + ] Sample Document Removed\n")

    db = mongo_client["Users"]
    collection = db["UserStocks"]

    sample_data = {
        "ID": 123456789012345678,
        "StocksAmount": {"AMD": 0,"INTC": 0, "MSFT": 0, "AAPL": 0, "GOOGL": 0},
        "StocksBuyPrice": {"AMD_P": 0,"INTC_P": 0, "MSFT_p": 0, "AAPL_P": 0, "GOOGL_p": 0},
        "Timestamp": "2024-08-22T12:00:00Z",
    }

    collection.insert_one(sample_data)
    print("[ + ] Collection Created with Initial Structure")

    collection.delete_one({"ID": 123456789012345678})

    print("[ + ] Sample Document Removed\n")

    db = mongo_client["Users"]
    collection = db["UserCrypto"]

    sample_data = {
        "ID": 123456789012345678,
        "CryptoAmount": {"BTC": 0,"ETH": 0, "BNB": 0, "SOL": 0, "AVAX": 0},
        "CryptoBuyPrice": {"BTC_P": 0,"ETH_P": 0, "BNB_P": 0, "SOL_P": 0, "AVAX_P": 0},
        "Timestamp": "2024-08-22T12:00:00Z",
    }

    collection.insert_one(sample_data)
    print("[ + ] Collection Created with Initial Structure")

    collection.delete_one({"ID": 123456789012345678})

    print("[ + ] Sample Document Removed\n")
    

# =============================================================================== #

# Bot Events


@bot.event
async def on_ready():
    start_time = str(datetime.now().strftime("%H:%M:%S"))
    up_time = datetime.now()
    bot.start_time = start_time
    bot.up_time = up_time

    print("-----------------------------------------")
    print(f"[ + ] Fallener Utilities")
    print(f"[ + ] BOT ID : {bot.user.id}")
    print(f"[ + ] Time : {start_time}")
    print("-----------------------------------------")
    await bot.change_presence(activity=discord.Game(name="Fallener Utilities"))


# =============================================================================== #

# Basic Commands


@bot.bridge_command(name="ping", description="Check The BOT's Response Time")
async def ping(ctx: discord.ApplicationContext):
    latency = bot.latency * 1000
    uptime = datetime.datetime.now() - bot.up_time

    uptime_seconds = uptime.total_seconds()
    uptime_str = str(datetime.timedelta(seconds=uptime_seconds)).split(".")[0]

    embed = discord.Embed(
        title=":ping_pong: _*Pong !*_",
        description=f"Uptime : {uptime_str}\nLatency : {latency:.2f} ms",
        color=0xFBF2EB,
    )

    await ctx.respond(embed=embed)


@bot.bridge_command(
    name="info",
    description="Get Bot Information",
)
async def info(ctx: discord.ApplicationContext):
    embed = discord.Embed(
        title=":information_source: Application Info",
        description="Minecraft utility Bot\nMainly For Fallen SMP",
        color=0xFBF2EB,
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
        value=f":calendar: `{bot.user.created_at.strftime('%Y-%m-%d %H:%M:%S')}`",
        inline=True,
    )

    embed.set_thumbnail(url=bot.user.avatar.url)
    await ctx.respond(embed=embed)


@bot.bridge_command(
    name="help",
    description="Get Commands List",
)
async def help(ctx: discord.ApplicationContext):
    await ctx.respond("SOHAM Hasn't Finished Writing This Yet")


@bot.event
async def on_slash_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandOnCooldown):
        await ctx.respond(
            f"This Command Is On Cooldown. Try Again In {error.retry_after:.2f} Seconds"
        )
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.respond("You Are Missing Required Arguments")
    elif isinstance(error, commands.errors.BadArgument):
        await ctx.respond("Bad Argument Provided")
    elif isinstance(error, commands.errors.CommandInvokeError):
        await ctx.respond("An Error Occurred While Executing The Command")
    elif isinstance(error, commands.errors.CommandNotFound):
        await ctx.respond("Command Not Found")
    elif isinstance(error, commands.errors.CheckFailure):
        await ctx.respond("You Do Not Have Permission To Use This Command")
    else:
        await ctx.respond("An Error Occurred")


@bot.event
async def on_bridge_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandOnCooldown):
        await ctx.respond(
            f"This Command Is On Cooldown. Try Again In {error.retry_after:.2f} Seconds"
        )
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.respond("You Are Missing Required Arguments")
    elif isinstance(error, commands.errors.BadArgument):
        await ctx.respond("Bad Argument Provided")
    elif isinstance(error, commands.errors.CommandInvokeError):
        await ctx.respond("An Error Occurred While Executing The Command")
    elif isinstance(error, commands.errors.CommandNotFound):
        await ctx.respond("Command Not Found")
    elif isinstance(error, commands.errors.CheckFailure):
        await ctx.respond("You Do Not Have Permission To Use This Command")
    else:
        await ctx.respond("An Error Occurred")

# =============================================================================== #

# Initialisation COGS

try:
    bot.load_extension("COGS.Whitelist")
    bot.load_extension("COGS.Player")
    bot.load_extension("COGS.Status")
    print("[ + ] COGs Loaded")
except Exception as e:
    print(f"[ - ] Failed To Load COGs : {e}")

# =============================================================================== #

# Running The BOT

bot.run(os.getenv("TOKEN"))
