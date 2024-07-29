import os
import base64
import sqlite3
import asyncio
import logging
import discord
import aiohttp
import warnings
import paramiko
import datetime
from io import BytesIO
from discord import option
from discord.ext import commands
from cryptography.utils import CryptographyDeprecationWarning

warnings.filterwarnings(
    "ignore", category=CryptographyDeprecationWarning, module="paramiko"
)

logging.basicConfig(level=logging.INFO)

intents = discord.Intents.all()
bot = discord.Bot(intents=intents)

DISCORD_CHANNEL_ID = 1267512160540426390

whitelist_channel_id = 1267512076222595122
console_channel_id = 1263898954999922720
log_channel_id = 1267512160540426390

SFTP_HOST = "pre-01.gbnodes.host"
SFTP_USER = "bl_8262.1ab56acd"
SFTP_PORT = 2222

SFTP_PASSWORD = "i^g@z4g2bn9"
LOG_FILE_PATH = "/logs/latest.log"

ADMINS = [
    727012870683885578,
    437622938242514945,
    243042987922292738,
    664157606587138048,
    1188730953217097811,
]

conn = sqlite3.connect("User.db")
cursor = conn.cursor()

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS user_data (
    id INTEGER PRIMARY KEY,
    discord_user_id TEXT,
    minecraft_username TEXT,
    character_name TEXT,
    character_gender TEXT,
    character_backstory TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
"""
)

API_URL = "https://api.mcsrvstat.us/3/gh-r9.glacierhosting.org:35564"


async def send_to_discord(message):
    channel = bot.get_channel(DISCORD_CHANNEL_ID)
    if channel:
        await channel.send(message)
    else:
        logging.error(f"Channel ID : {DISCORD_CHANNEL_ID} ")


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

    try:
        transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
        transport.connect(username=SFTP_USER, password=SFTP_PASSWORD)
        sftp_client = paramiko.SFTPClient.from_transport(transport)
        logging.info("Connected To SFTP - Loaded LOG File")
        await read_and_send_logs()
    except paramiko.AuthenticationException as e:
        logging.error(f"Authentication Failed : {e}")
    except paramiko.SSHException as e:
        logging.error(f"SSH Error : {e}")
    except FileNotFoundError as e:
        logging.error(f"File Not Found : {e}")
    except Exception as e:
        logging.error(f"Failed To Send Logs : {e}")
    finally:
        if sftp_client:
            sftp_client.close()
        if transport:
            transport.close()


@bot.event
async def on_ready():

    start_time = datetime.datetime.now()
    bot.start_time = start_time

    print("-----------------------------")
    print("--- + SOHAM's Utilities + ---")
    print("-----------------------------")
    await bot.change_presence(activity=discord.Game(name="With Utilities"))

    await connect_sftp()


@bot.slash_command(
    name="help",
    description="Get Help About Commands",
)
async def help(ctx: discord.ApplicationContext):

    status = bot.get_application_command("status")
    ping = bot.get_application_command("ping")
    info = bot.get_application_command("info")
    rules = bot.get_application_command("rules")
    guide = bot.get_application_command("guide")
    whitelist = bot.get_application_command("whitelist")
    playerinfo = bot.get_application_command("playerinfo")

    embed = discord.Embed(
        title=":question: Help",
        description="List Of Commands Available",
        color=0x2F3136,
    )

    embed.add_field(
        name=f"{status.mention}",
        value="Get Minecraft Server Status",
        inline=False,
    )
    embed.add_field(
        name=f"{ping.mention}",
        value="Check Bot's Latency & Uptime",
        inline=False,
    )
    embed.add_field(
        name=f"{info.mention}",
        value="Get Bot Information",
        inline=False,
    )
    embed.add_field(
        name=f"{rules.mention}",
        value="Get Server Rules",
        inline=False,
    )
    embed.add_field(
        name=f"{guide.mention}",
        value="Get Server Guide",
        inline=False,
    )
    embed.add_field(
        name=f"{whitelist.mention}",
        value="Get WhiteListed On Fallen SMP",
        inline=False,
    )
    embed.add_field(
        name=f"{playerinfo.mention}",
        value="Get Your Player Info",
        inline=False,
    )

    reconnect = bot.get_application_command("reconnect")
    del_whitelist = bot.get_application_command("del_whitelist")
    add_whitelist = bot.get_application_command("add_whitelist")
    show_whitelist = bot.get_application_command("show_whitelist")

    admin_embed = discord.Embed(
        title=":gear: Admin Commands",
        description="List Of Admin Commands Available",
        color=0x2F3136,
    )

    admin_embed.add_field(
        name=f"{reconnect.mention}",
        value="Reconnects To The Server SFTP",
        inline=False,
    )
    admin_embed.add_field(
        name=f"{del_whitelist.mention}",
        value="Delete User's Whitelist Application",
        inline=False,
    )
    admin_embed.add_field(
        name=f"{add_whitelist.mention}",
        value="Add User To Whitelist",
        inline=False,
    )
    admin_embed.add_field(
        name=f"{show_whitelist.mention}",
        value="Show all whitelisted members",
        inline=False,
    )

    await ctx.respond(embed=embed)
    if ctx.author.id in [1188730953217097811, 664157606587138048, 727012870683885578]:
        await ctx.followup.send(embed=admin_embed)


@bot.slash_command(
    name="rules",
    description="Get Server Rules",
)
async def rules(ctx: discord.ApplicationContext):

    rules = """
        ### 1. Refrain from Unnecessary PvP
> If you want to engage in PvP, arrange it with others and ensure everyone agrees. Unplanned PvP can disrupt the game experience.

### 2. Roleplay as Your Character
> Since this is a roleplay server, you must act as your character described in your character story. This enhances the immersive experience for everyone.

### 3. Value Your Life In Game As Much As In Real Life 
> Treat your in-game life with care and caution, just as you would in reality. This rule ensures a more realistic and engaging gameplay experience.

### 4. No Chat Toxicity
> Toxic behaviour in chat is strictly prohibited. Maintain a respectful and positive environment for all players.

### 5. No Stealing
> Stealing from other players is not allowed. Engaging in theft can lead to being labelled as an outlaw and facing consequences.

### 6. Obey Orders from Duke, King, and Emperor
> You must follow the orders issued by the Duke, King, and Emperor. This maintains the hierarchical structure and order within the server.

### 7. Building Permissions Required
> To build a house, you must obtain permission from the Duke. This ensures organized and planned development within the server.
"""

    embed = discord.Embed(
        title=":scroll: Server Rules",
        description=rules,
        color=0x2F3136,
    )

    embed.set_image(
        url="https://media.discordapp.net/attachments/1258116175758364673/1266046626548678819/FALLEN_SMP.gif?ex=66a8ff4d&is=66a7adcd&hm=f11beaedcee762a32204c87a07d89c4faa2c2d64611ae0c62eea9d4ccf23e3d6&=&width=1024&height=320"
    )

    await ctx.respond(embed=embed, ephemeral=True)


@bot.slash_command(
    name="guide",
    description="Get Server Guide",
)
async def guide(ctx: discord.ApplicationContext):

    embed = discord.Embed(
        title=":book: Server Guide",
        description="Choose A Guide Topic",
        color=0x2F3136,
    )

    await ctx.respond(embed=embed, view=Guide_Menu())


class Guide_Menu(discord.ui.View):
    @discord.ui.select(
        placeholder="Guide Menu",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                label="Basic Roles Info", description="Learn About Server Roles"
            ),
            discord.SelectOption(
                label="How To Get Whitelisted",
                description="Learn about Whitelisting Process",
            ),
        ],
    )
    async def select_callback(self, select, interaction):

        if select.values[0] == "Basic Roles Info":
            guide_1 = """
## What Are The Roles in the Server?

Since the server is in its early phase, it has only a few roles:

1. **Citizen**
   - **Description**: The basic role given to everyone. Citizens focus on building their houses and farming, with the goal of becoming a merchant.
   - **Responsibilities**: Building homes, farming, and community participation.

2. **Merchant**
   - **Description**: The sole businesspeople of the server. You need at least two days of gameplay time to apply for this role.
   - **Responsibilities**: Setting up shops and selling items.

3. **Duke**
   - **Description**: The direct subordinate to the King, holding significant power. Dukes assign the merchant role to citizens and address their issues.
   - **Responsibilities**: Assigning merchant roles, resolving citizen issues, placing bounties, and issuing soft bans for rule violations.
   - **Requirements**: At least one week of gameplay time to apply.

4. **King**
   - **Description**: The highest role in the server, overseeing matters of high importance and assigning the Duke role to merchants.
   - **Responsibilities**: Managing high-level issues and maintaining order.
   - **Selection**: Kings are elected at the beginning of every month.
"""

            embed = discord.Embed(
                title=":book: Server Guide",
                description=guide_1,
                color=0x2F3136,
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)

        elif select.values[0] == "How To Get Whitelisted":
            guide_2 = """
    ## How to Get Whitelisted ?

To get whitelisted, follow these steps:

1. **Use the Command**: Enter the command `/whitelist` <@1264849548334071828> in the chat.
2. **Fill Out the Form**: This command will prompt a form that you need to complete. The form will ask for details such as your in-game name, your reason for joining, and any other relevant information.
3. **Wait for Review**: Once you have submitted the form, it will be reviewed by the moderators.
4. **Approval**: If your application is approved, the moderators will add you to the whitelist, allowing you to join the server.

**Additional Information**:
- **Be Patient**: The review process may take some time, so please be patient.
- **Accuracy**: Ensure that all the information you provide in the form is accurate and truthful to increase your chances of being approved.
- **Follow-Up**: If you haven't received a response after a reasonable amount of time, you may politely inquire about the status of your application with the moderators ( I know no one will follow this, so just ping <@727012870683885578> Or <@664157606587138048> ).
"""

            embed = discord.Embed(
                title=":book: Server Guide",
                description=guide_2,
                color=0x2F3136,
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.slash_command(
    name="status",
    description="Get Minecraft Server Status",
)
async def status(ctx: discord.ApplicationContext):

    await ctx.defer()

    async with aiohttp.ClientSession() as session:
        async with session.get(API_URL) as response:
            if response.status == 200:
                data = await response.json()
                if data.get("online"):
                    embed = discord.Embed(
                        title=":green_circle: ONLINE",
                        color=0x2F3136,
                    )

                    embed.set_author(name="Fallen SMP")

                    embed.add_field(
                        name="PLAYERS",
                        value=f"{data['players']['online']}/{data['players']['max']}",
                        inline=True,
                    )
                    embed.add_field(name="VERSION", value=data["version"], inline=True)
                    embed.add_field(
                        name="SOFTWARE", value=data["software"], inline=True
                    )

                    embed.add_field(
                        name="SERVER ADDRESS",
                        value="IP : `play.fallensmp.xyz`",
                        inline=False,
                    )
                    embed.add_field(
                        name="WEBSITE", value=f"https://fallensmp.xyz", inline=False
                    )

                    motd_lines = data.get("motd", {}).get("clean", [""])[0:2]
                    stripped_motd_lines = [line.strip() for line in motd_lines]
                    centered_motd = "\n".join(
                        f"{line.center(40)}" for line in stripped_motd_lines
                    )
                    formatted_motd = f"```\n{centered_motd}\n```"

                    embed.add_field(name="MOTD", value=formatted_motd, inline=False)

                    icon_base64 = data.get("icon")
                    if icon_base64:
                        image_data = base64.b64decode(icon_base64.split(",")[1])
                        image = BytesIO(image_data)
                        image.seek(0)
                        file = discord.File(image, filename="ICON.png")

                    embed.set_thumbnail(url="attachment://ICON.png")

                    await ctx.respond(embed=embed, file=file, view=View_Players(data))

                else:
                    embed = discord.Embed(
                        title=":red_circle: OFFLINE",
                        color=0x2F3136,
                    )

                    embed.set_author(name="Fallen SMP")

                    embed.add_field(
                        name="PLAYERS",
                        value=f"{data['players']['online']}/{data['players']['max']}",
                        inline=True,
                    )
                    embed.add_field(name="VERSION", value=data["version"], inline=True)
                    embed.add_field(
                        name="SOFTWARE", value=data["software"], inline=True
                    )

                    embed.add_field(
                        name="SERVER ADDRESS",
                        value="IP : `play.fallensmp.xyz`",
                        inline=False,
                    )
                    embed.add_field(
                        name="WEBSITE", value=f"https://fallensmp.xyz", inline=False
                    )

                    await ctx.respond(embed=embed)


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


@bot.slash_command(name="playerinfo", description="Get Your Player Info")
async def playerinfo(ctx: discord.ApplicationContext):

    conn = sqlite3.connect("User.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM user_data WHERE discord_user_id = ?", (str(ctx.author.id),)
    )
    rows = cursor.fetchall()

    if rows:
        row = rows[0]
        embed = discord.Embed(
            title="Player Information",
            description=f"Details for **{ctx.author.display_name}** \n :id: Application ID : {row[0]}",
            color=discord.Color.green(),
        )

        embed.add_field(
            name="Discord User ID",
            value=f"{row[1]}({str(ctx.author.display_name)})",
            inline=False,
        )
        embed.add_field(name="Minecraft Username", value=row[2], inline=False)

        embed.set_thumbnail(url=ctx.author.avatar.url)
        embed.set_footer(text=f"Fallen SMP | Joined On {row[6]}")

        await ctx.respond(embed=embed, view=View_Character_Info(ctx.author.id))
    else:
        embed = discord.Embed(
            title=":x: Player Data Not Found",
            description="It Seems Like There Isn't Any Data For You. Make Sure To Submit The Whitelist Application.",
            color=discord.Color.red(),
        )
        await ctx.respond(embed=embed, ephemeral=True)

    conn.close()


@bot.slash_command(
    name="del_whitelist", description="Delete User's Whitelist Application"
)
async def del_whitelist(ctx: discord.ApplicationContext, member: discord.Member):

    if ctx.author.id in ADMINS:

        conn = sqlite3.connect("User.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM user_data WHERE discord_user_id = ?", (str(member.id),)
        )
        row = cursor.fetchone()

        if row:
            cursor.execute(
                "DELETE FROM user_data WHERE discord_user_id = ?", (str(member.id),)
            )
            conn.commit()
            conn.close()

            embed = discord.Embed(
                title="Whitelist Application Deleted",
                description=f"Whitelist Application For **{member.display_name}** Has Been Deleted.",
                color=discord.Color.green(),
            )
        else:
            conn.close()
            embed = discord.Embed(
                title="User Not Found",
                description=f"No Whitelist Application Found For **{member.display_name}**.",
                color=discord.Color.red(),
            )

        await ctx.respond(embed=embed)

    else:
        await ctx.respond("Laude Ye Tereliye Nehi Hai :F", ephemeral=True)


@bot.slash_command(name="add_whitelist", description="Add User To Whitelist")
@option(
    "type",
    description="Choose The Whitelist Type",
    choices=["java", "bedrock"],
)
async def add_whitelist(
    ctx: discord.ApplicationContext, member: discord.Member, type: str
):

    if ctx.author.id in ADMINS:

        conn = sqlite3.connect("User.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM user_data WHERE discord_id = ?", (member.id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            character_name = row[2]

            if type == "java":
                console_channel = bot.get_channel(console_channel_id)
                await console_channel.send(f"whitelist add {character_name}")

            elif type == "bedrock":
                console_channel = bot.get_channel(console_channel_id)
                await console_channel.send(f"fwhitelist add {character_name}")

            embed = discord.Embed(
                title="Whitelist Added",
                description=f"Whitelist for **{member.display_name}** has been accepted.",
                color=discord.Color.green(),
            )

            await ctx.respond(embed=embed)

        else:
            embed = discord.Embed(
                title="User Not Found",
                description=f"No Whitelist Application Found For **{member.display_name}**.",
                color=discord.Color.red(),
            )

            await ctx.respond(embed=embed)

    else:
        await ctx.respond("Laude Ye Tereliye Nehi Hai :F", ephemeral=True)


@bot.slash_command(name="show_whitelist", description="Show all whitelisted members")
async def show_whitelist(ctx: discord.ApplicationContext):

    if ctx.author.id in ADMINS:

        conn = sqlite3.connect("User.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM user_data")
        rows = cursor.fetchall()
        conn.close()

        if rows:
            embed = discord.Embed(
                title="Whitelisted Members",
                description="List Of Whitelisted Members",
                color=discord.Color.blue(),
            )

            for row in rows:
                member = ctx.guild.get_member(int(row[1]))
                if member:
                    embed.add_field(
                        name=f"{row[0]}. {member.display_name} ({member.id})",
                        value=f"Minecraft Username: {row[2]}",
                        inline=False,
                    )
        else:
            embed = discord.Embed(
                title="No Whitelisted Members",
                description="There Are No Whitelisted Members.",
                color=discord.Color.red(),
            )

        await ctx.respond(embed=embed)

    else:
        await ctx.respond("Laude Ye Tereliye Nehi Hai :F", ephemeral=True)


@bot.slash_command(name="whitelist", description="Get WhiteListed On Fallen SMP")
async def whitelist(ctx):

    conn = sqlite3.connect("User.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM user_data WHERE discord_user_id = ?", (str(ctx.author.id),)
    )
    row = cursor.fetchone()

    if row:
        embed = discord.Embed(
            title=":white_check_mark: Already Whitelisted",
            description="You Are Already Whitelisted On Fallen SMP.\n** If U Messed Up Ur Application, Contact <@979191620610170950> Or <@664157606587138048>**",
            color=discord.Color.green(),
        )
        await ctx.respond(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(
            title="Whitelist Application",
            description="Please Fill Out The Form By Clicking The Button Below",
            color=discord.Color.green(),
        )
        embed.add_field(name="Server IP", value="play.fallensmp.xyz", inline=True)
        embed.add_field(name="Server Version", value="1.21.1", inline=True)

        embed.set_image(
            url="https://media.discordapp.net/attachments/1258116175758364673/1266046626548678819/FALLEN_SMP.gif?ex=66a3b94d&is=66a267cd&hm=b80fdae6a297eeb179347003f57935b5edf601dfbb5433937e9cbb4a9f1493c5&=&width=1024&height=320"
        )

        await ctx.respond(
            embed=embed,
            view=Whitelist_View(interaction_user=ctx.user),
            ephemeral=True,
        )

    conn.close()


class View_Character_Info(discord.ui.View):
    def __init__(self, user_id) -> None:
        super().__init__(timeout=None)
        self.user_id = user_id

    @discord.ui.button(label="View Character Info", style=discord.ButtonStyle.secondary)
    async def view_button_callback(self, button, interaction):

        conn = sqlite3.connect("User.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM user_data WHERE discord_user_id = ?", (str(self.user_id),)
        )
        row = cursor.fetchone()

        if row:
            embed = discord.Embed(
                title="Character Information",
                description=f"Character For **{interaction.user.display_name}**",
                color=discord.Color.green(),
            )

            embed.add_field(name="Character Name", value=row[3], inline=True)
            embed.add_field(name="Character Gender", value=row[4], inline=True)
            embed.add_field(name="Character Backstory", value=row[5], inline=False)

            embed.set_thumbnail(url=interaction.user.avatar.url)
            embed.set_footer(text=f"Fallen SMP | Joined on {row[6]}")

            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                title=":x: Player Data Not Found",
                description="It Seems Like There Isn't Any Data For You. Make Sure To Sumbit The Whitelist Application.",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

        conn.close()


class View_Players(discord.ui.View):
    def __init__(self, data) -> None:
        super().__init__(timeout=None)

        self.data = data

    @discord.ui.button(label="View Players", style=discord.ButtonStyle.secondary)
    async def view_button_callback(self, button, interaction):

        players_list = self.data.get("players", {}).get("list", [])
        player_names = [player.get("name") for player in players_list]

        columns = 3
        player_names_formatted = ""
        for i, name in enumerate(player_names):
            player_names_formatted += f"• {name} "
            if (i + 1) % columns == 0:
                player_names_formatted += "\n"

        embed = discord.Embed(
            title=":busts_in_silhouette: Players Online",
            description=f"{player_names_formatted if player_names else 'No Players Online'}",
            color=0x2F3136,
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)


class Whitelist_View(discord.ui.View):
    def __init__(self, interaction_user) -> None:
        super().__init__(timeout=None)

        self.interaction_user = interaction_user

    @discord.ui.button(label="Whitelist Form")
    async def button_callback(self, button, interaction):

        if interaction.user != self.interaction_user:
            await interaction.response.send_message(
                "Laude Ye Tereliye Nehi Hai :F", ephemeral=True
            )
            return

        await interaction.response.send_modal(
            Whitelist(title="Fallen SMP Whitelist Form")
        )


class Whitelist(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add_item(
            discord.ui.InputText(
                label="Minecraft Username", placeholder="Enter Your Minecraft Username"
            )
        )
        self.add_item(
            discord.ui.InputText(
                label="Character Name", placeholder="Enter Your Server Character Name"
            )
        )
        self.add_item(
            discord.ui.InputText(
                label="Character Gender", placeholder="Enter Your Character Gender"
            )
        )
        self.add_item(
            discord.ui.InputText(
                label="Character Backstory",
                placeholder="Write Your Character BackStory",
                style=discord.InputTextStyle.long,
            )
        )

    async def callback(self, interaction: discord.Interaction):
        conn = sqlite3.connect("User.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO user_data (
                discord_user_id,
                minecraft_username,
                character_name,
                character_gender,
                character_backstory
            ) VALUES (?, ?, ?, ?, ?)
        """,
            (
                str(interaction.user.id),
                self.children[0].value,
                self.children[1].value,
                self.children[2].value,
                self.children[3].value,
            ),
        )

        print("Data Inserted")

        conn.commit()
        conn.close()

        embed = discord.Embed(
            title=f"Application of {interaction.user.display_name}",
            description=f"** Username **: {self.children[0].value}\n** Character Name **: {self.children[1].value}\n** Character Gender **: {self.children[2].value}\n\n** Character Backstory **: {self.children[3].value}",
        )

        embed.set_image(
            url="https://media.discordapp.net/attachments/1258116175758364673/1266046626548678819/FALLEN_SMP.gif?ex=66a3b94d&is=66a267cd&hm=b80fdae6a297eeb179347003f57935b5edf601dfbb5433937e9cbb4a9f1493c5&=&width=1024&height=320"
        )

        await interaction.response.send_message(embeds=[embed])

        log_embed = discord.Embed(
            title=f"Whitelist Application Of {interaction.user}",
            description=f"** Username **: {self.children[0].value}\n** Character Name **: {self.children[1].value}\n** Character Gender **: {self.children[2].value}\n\n** Character Backstory **: {self.children[3].value}",
        )

        whitelist_channel = bot.get_channel(whitelist_channel_id)
        await whitelist_channel.send(
            "<@727012870683885578> <@437622938242514945> <@664157606587138048> <@813064731782938624> <@1188730953217097811>",
            embed=log_embed,
        )


class Whitelist_Buttons(discord.ui.View):
    def __init__(self, user, interaction_user) -> None:
        super().__init__(timeout=None)

        self.user = user
        self.interaction_user = interaction_user

    @discord.ui.button(label="Java Whitelist", style=discord.ButtonStyle.secondary)
    async def java_button_callback(self, button, interaction):

        if interaction.user == self.interaction_user:
            await interaction.response.send_message(
                "Please Wait For The Admin To Review Your Application", ephemeral=True
            )

    @discord.ui.button(label="Bedrock Whitelist", style=discord.ButtonStyle.secondary)
    async def bedrock_button_callback(self, button, interaction):

        if interaction.user == self.interaction_user:
            await interaction.response.send_message(
                "Please Wait For The Admin To Review Your Application", ephemeral=True
            )


bot.run("MTI2NDg0OTU0ODMzNDA3MTgyOA.GojSjB.uz_CDm0PgyiB-BvHGiaXOuGhtw4Ux4PuuHuv-c")
