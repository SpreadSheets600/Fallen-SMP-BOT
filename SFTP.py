import time
import pysftp
import asyncio
import discord
import datetime
from discord.ext import commands

HOST_NAME = "pre-01.gbnodes.host"
USERNAME = "bl_8262.1ab56acd"
PASSWORD = "i^g@z4g2bn9"
PORT = 2222

LOG_FILE_PATH = "/logs/latest.log"
LOG_CHANNEL_ID = 1267512160540426390

intents = discord.Intents.all()
bot = discord.Bot(intents=intents)

sftp_client = None


async def send_to_discord(line):
    channel = bot.get_channel(LOG_CHANNEL_ID)
    await channel.send(f"{line}")


async def follow_sftp(sftp, logfile_path):
    with sftp.open(logfile_path, "r") as logfile:
        logfile.seek(0, 2)
        while True:
            line = logfile.readline()
            if not line:
                await asyncio.sleep(0.1)
                continue
            yield line.strip()


async def read_and_send_logs():
    global sftp_client
    while True:
        try:
            async for line in follow_sftp(sftp_client, LOG_FILE_PATH):
                await send_to_discord(line)
        except Exception as e:
            print(f"Connection Lost : {e}")
            user_id = 727012870683885578
            user = bot.get_user(user_id)
            if user:
                await user.send(f"Connection Lost : {e}")
            await asyncio.sleep(120)
            await reconnect_sftp()


async def reconnect_sftp():
    global sftp_client
    while True:
        try:
            cnopts = pysftp.CnOpts()
            cnopts.hostkeys = None
            sftp_client = pysftp.Connection(
                host=HOST_NAME,
                username=USERNAME,
                password=PASSWORD,
                port=PORT,
                cnopts=cnopts,
            )

            bot.loop.create_task(read_and_send_logs())

            user_id = 727012870683885578
            user = bot.get_user(user_id)

            if user:
                await user.send("Reconnected To SFTP Server")

            break
        except Exception as e:
            print(f"Reconnection Attempt Failed : {e}")
            user_id = 727012870683885578
            user = bot.get_user(user_id)
            if user:
                await user.send(f"Reconnection Attempt Failed : {e}")
            await asyncio.sleep(120)


@bot.event
async def on_ready():
    global sftp_client
    start_time = datetime.datetime.now()
    bot.start_time = start_time
    print("-----------------------------")
    print("--- + Fallener SFTP + ---")
    print("-----------------------------")
    await bot.change_presence(activity=discord.Game(name="With SFTP"))
    try:
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        sftp_client = pysftp.Connection(
            host=HOST_NAME,
            username=USERNAME,
            password=PASSWORD,
            port=PORT,
            cnopts=cnopts,
        )

        user_id = 727012870683885578
        user = bot.get_user(user_id)

        if user:
            await user.send("Connected To SFTP Server")

        bot.loop.create_task(read_and_send_logs())
    except Exception as e:
        print(f"Taar Kaath Diya : {e}")
        await reconnect_sftp()


@bot.slash_command(name="reconnect", description="Reconnect to SFTP Server")
async def reconnect(ctx):
    await reconnect_sftp()
    await ctx.respond("Reconnected To SFTP Server")


@bot.slash_command(name="ping", description="Check Bot's Latency & Uptime")
async def ping(ctx: discord.ApplicationContext):
    latency = bot.latency * 1000
    uptime = datetime.datetime.now() - bot.start_time
    uptime_seconds = uptime.total_seconds()
    uptime_str = str(datetime.timedelta(seconds=uptime_seconds)).split(".")[0]
    embed = discord.Embed(
        title=":ping_pong: _*Pong !*_",
        description=f"Uptime : {uptime_str}\nLatency : {latency:.2f} ms",
        color=0x2F3136,
    )
    await ctx.respond(embed=embed)


@bot.slash_command(name="info", description="Get Bot Information")
async def info(ctx: discord.ApplicationContext):
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
        value=f":calendar: `{bot.user.created_at.strftime('%Y-%m-%d %H:%M:%S')}`",
        inline=True,
    )
    embed.set_thumbnail(url=bot.user.avatar.url)
    await ctx.respond(embed=embed)


bot.run("MTI2ODU4MTQ4NTg3MTUwMTM1NA.GNWFSy.8h9dd3OnwQWfyqmAeXk37OyyVgt1EXWuDz2T40")
