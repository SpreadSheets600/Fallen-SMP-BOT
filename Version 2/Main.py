import os
import time
import aiohttp
import datetime

import discord
import COGS.Whitelist
from COGS.Whitelist import *
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

intents = discord.Intents.all()
bot = bridge.Bot(command_prefix="FS!", intents=intents)

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
    print("[ + ] Collection Created with Initial Structure\n")

    collection.delete_one({"ID": 123456789012345678})

    print("[ + ] Sample Document Removed\n")

# =============================================================================== #

# Bot Events


@bot.event
async def on_ready():
    start_time = str(datetime.datetime.now()).split(" ")[1]
    up_time = datetime.datetime.now()
    bot.start_time = start_time
    bot.up_time = up_time

    print("-----------------------------------------")
    print(f"[ + ] Fallener Utilities")
    print(f"[ + ] BOT ID : {bot.user.id}")
    print(f"[ + ] Time : {start_time}")
    print("-----------------------------------------")
    await bot.change_presence(activity=discord.Game(name="Fallener Utilities"))

    bot.remove_command("help")

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

# =============================================================================== #

# Initialisation COGS

try:
    bot.load_extension("COGS.Whitelist")
    print("[ + ] Whitelist COG Loaded")
except Exception as e:
    print(f"[ - ] Failed to load Whitelist COG: {e}")

# =============================================================================== #

# Running The BOT

bot.run(os.getenv("TOKEN"))
