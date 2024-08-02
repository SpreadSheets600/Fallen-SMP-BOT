import logging
import discord
import asyncio
import datetime
import paramiko
import warnings
from discord.ext import commands
from cryptography.utils import CryptographyDeprecationWarning

warnings.filterwarnings(
    "ignore", category=CryptographyDeprecationWarning, module="paramiko"
)

logging.basicConfig(level=logging.INFO)

intents = discord.Intents.all()
bot = discord.Bot(intents=intents)

ADMINS = [
    727012870683885578,
    437622938242514945,
    243042987922292738,
    664157606587138048,
    1188730953217097811,
    896411007797325824,
]

SFTP_Channel_ID = 1267512160540426390

SFTP_HOST = "pre-01.gbnodes.host"
SFTP_USER = "bl_8262.1ab56acd"
SFTP_PORT = 2222

SFTP_PASSWORD = "i^g@z4g2bn9"
LOG_FILE_PATH = "/logs/latest.log"

sftp_client = None
transport = None


async def send_to_discord(message):
    channel = bot.get_channel(SFTP_Channel_ID)
    if channel:
        await channel.send(message)
    else:
        logging.error(f"Channel ID : {SFTP_Channel_ID} ")


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
    async for line in follow_sftp(sftp_client, LOG_FILE_PATH):
        await send_to_discord(line)


async def connect_sftp():
    global sftp_client, transport

    while True:
        try:
            transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
            transport.connect(username=SFTP_USER, password=SFTP_PASSWORD)
            sftp_client = paramiko.SFTPClient.from_transport(transport)
            logging.info("Connected To SFTP - Loaded LOG File")
            await read_and_send_logs()

        except (
            paramiko.AuthenticationException,
            paramiko.SSHException,
            FileNotFoundError,
        ) as e:
            logging.error(f"Connection Error: {e}. Reconnecting In 1 Minute ...")
            await asyncio.sleep(60)
        except Exception as e:
            logging.error(f"Unexpected Error: {e}. Reconnecting In 1 Minute ...")
            await asyncio.sleep(60)
        finally:
            if sftp_client:
                sftp_client.close()
            if transport:
                transport.close()


async def monitor_connection():
    global sftp_client, transport

    while True:
        await asyncio.sleep(60)
        if not sftp_client or sftp_client.sock.closed:
            logging.warning("Lost Connection To SFTP. Reconnecting ...")
            if sftp_client:
                sftp_client.close()
            if transport:
                transport.close()
            await connect_sftp()


@bot.event
async def on_ready():
    start_time = datetime.datetime.now()
    bot.start_time = start_time

    print("-----------------------------")
    print("--- + Fallener SFTP + ---")
    print("-----------------------------")
    await bot.change_presence(activity=discord.Game(name="With Utilities"))

    bot.loop.create_task(connect_sftp())
    bot.loop.create_task(monitor_connection())


@bot.slash_command(
    name="ping",
    description="Check Bot's Latency & Uptime",
)
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


@bot.slash_command(
    name="info",
    description="Get Bot Information",
)
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


@bot.slash_command(name="reconnect", description="Reconnects To The Server SFTP")
async def reconnect(ctx):
    if ctx.author.id in ADMINS:
        await ctx.defer()
        global sftp_client, transport

        if sftp_client:
            sftp_client.close()
        if transport:
            transport.close()

        embed = discord.Embed(
            title="Server SFTP",
            description="SFTP Have Been Reconnected",
            color=discord.Color.green(),
        )

        await ctx.followup.send(embed=embed)
        await connect_sftp()
    else:
        await ctx.respond("Laude Ye Tereliye Nehi Hai :F", ephemeral=True)


bot.run("MTI2ODU4MTQ4NTg3MTUwMTM1NA.GNWFSy.8h9dd3OnwQWfyqmAeXk37OyyVgt1EXWuDz2T40")
