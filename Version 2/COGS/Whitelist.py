import os
import random
import discord
import datetime
import mysql.connector as mysql
from discord.ext.pages import *
from discord.ext.bridge import BridgeSlashGroup
from discord.ext import commands, bridge, pages

from dotenv import *

load_dotenv()

# =================================================================================================== #

# Fixed Variables
ADMINS = [
    727012870683885578,
    437622938242514945,
    243042987922292738,
    664157606587138048,
    1188730953217097811,
    896411007797325824,
]

WHITELIST_CHANNEL = 1267512076222595122
CONSOLE_CHANNEL = 1263898954999922720
ERROR_CHANNEL = 1275759089024241797

# =================================================================================================== #


class Whitelist(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.connection, self.cursor = self.connect_to_database()

    def connect_to_database(self):
        try:
            connection = mysql.connect(
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASS"),
                database=os.getenv("DB_NAME"),
            )

            cursor = connection.cursor()
            print("[ + ] Whitelist COG : Connection Established")
            return connection, cursor

        except Exception as e:
            print(f"[ - ] Whitelist COG : Error : Connecting To Database : {e}")
            return None, None

    @bridge.bridge_group()
    async def wl(self, ctx):
        pass

    @wl.command(name="insert", description="Insert A User Into The Whitelist")
    async def insert(
        self, ctx, user: discord.User, username: str, gender: str, backstory: str
    ):
        if ctx.author.id not in ADMINS:
            await ctx.respond(
                "You Do Not Have Permission To Use This Command",
                ephemeral=True,
                delete_after=5,
            )
        else:
            try:
                self.cursor.execute(
                    "INSERT INTO Users (ID, Username, Gender, Backstory, Timestamp) VALUES (%s, %s, %s, %s, %s)",
                    (
                        user.id,
                        username,
                        gender,
                        backstory,
                        str(datetime.datetime.now()),
                    ),
                )
                self.connection.commit()

                embed = discord.Embed(
                    title="User Inserted",
                    description=f"User `{username}` Has Been Inserted Into The Database",
                    color=0xD5E4CF,
                )

                await ctx.respond(embed=embed, ephemeral=True)

            except Exception as e:
                print(f"[ - ] Whitelist COG : Error : {e}")
                await ctx.respond(
                    f"[ - ] Whitelist COG : Error : \n```{e}```",
                    ephemeral=True,
                    delete_after=5,
                )

                ErrorChannel = self.bot.get_channel(ERROR_CHANNEL)
                await ErrorChannel.send(f"[ - ] Whitelist COG : Error : \n```{e}```")

    @wl.command(name="add", description="Add a user to the whitelist")
    async def add(self, ctx, user: discord.User):
        if ctx.author.id not in ADMINS:
            await ctx.respond(
                "You Do Not Have Permission To Use This Command",
                ephemeral=True,
                delete_after=5,
            )
        else:
            try:
                self.cursor.execute("SELECT * FROM Users WHERE ID = %s", (user.id,))

                row = self.cursor.fetchone()
                if row:
                    username = row[1]

                    ConsoleChannel = self.bot.get_channel(CONSOLE_CHANNEL)
                    await ConsoleChannel.send(f"whitelist add {username}")

                    embed = discord.Embed(
                        title="User Whitelisted",
                        description=f"User `{username}` Has Been Whitelisted",
                        color=0xD5E4CF,
                    )

                    user_embed = discord.Embed(
                        title="Whitelist Application Accepted",
                        description=f"Your Whitelist Application Has Been Accepted. \n## Join Now : `play.fallensmp.xyz`",
                        color=0xD5E4CF,
                    )

                    User = self.bot.get_user(user.id)
                    await User.send(embed=user_embed)

                    await ctx.respond(embed=embed, ephemeral=True)
                else:
                    embed = discord.Embed(
                        title="User Not Found",
                        description=f"No Whitelist Application Found For **{user.display_name}**.",
                        color=discord.Color.red(),
                    )
                    await ctx.respond(embed=embed)

            except Exception as e:
                print(f"[ - ] Whitelist COG : Error : {e}")
                await ctx.respond(
                    f"[ - ] Whitelist COG : Error : \n```{e}```",
                    ephemeral=True,
                    delete_after=5,
                )

                ErrorChannel = self.bot.get_channel(ERROR_CHANNEL)
                await ErrorChannel.send(f"[ - ] Whitelist COG : Error : \n```{e}```")

    @wl.command(name="remove", description="Remove a user from the whitelist")
    async def remove(self, ctx, user: discord.User):
        if ctx.author.id not in ADMINS:
            await ctx.respond(
                "You Do Not Have Permission To Use This Command",
                ephemeral=True,
                delete_after=5,
            )
        else:
            try:
                self.cursor.execute("SELECT * FROM Users WHERE ID = %s", (user.id,))

                row = self.cursor.fetchone()
                if row:
                    username = row[1]

                    self.cursor.execute("DELETE FROM Users WHERE ID = %s", (user.id,))

                    ConsoleChannel = self.bot.get_channel(CONSOLE_CHANNEL)
                    await ConsoleChannel.send(f"whitelist remove {username}")

                    embed = discord.Embed(
                        title="User Removed",
                        description=f"User `{username}` Has Been Removed From The Whitelist",
                        color=0xFBEADC,
                    )

                    await ctx.respond(embed=embed, ephemeral=True)
                else:
                    embed = discord.Embed(
                        title="User Not Found",
                        description=f"No Whitelist Application Found For **{user.display_name}**.",
                        color=discord.Color.red(),
                    )
                    await ctx.respond(embed=embed)

            except Exception as e:
                print(f"[ - ] Whitelist COG : Error : {e}")
                await ctx.respond(
                    f"[ - ] Whitelist COG : Error : \n```{e}```",
                    ephemeral=True,
                    delete_after=5,
                )

                ErrorChannel = self.bot.get_channel(ERROR_CHANNEL)
                await ErrorChannel.send(f"[ - ] Whitelist COG : Error : \n```{e}```")

    @wl.command(name="view", description="View A User's Whitelist Application")
    async def view(self, ctx, user: discord.User):
        if user == None:
            user = ctx.author

        try:
            self.cursor.execute("SELECT * FROM Users WHERE ID = %s", (user.id,))

            row = self.cursor.fetchone()

            if row:
                username = row[1]

                embed = discord.Embed(
                    title="Player Information",
                    description=f"Details For **{user.display_name}**",
                    color=0xDDDDBD,
                )

                embed.add_field(
                    name="Discord User ID",
                    value=f"{row[0]}",
                    inline=False,
                )

                embed.add_field(name="Minecraft Username", value=row[1], inline=False)

                try:
                    avatar = user.avatar.url
                    embed.set_thumbnail(url=user.avatar.url)
                except Exception as e:
                    pass

                embed.set_footer(text=f"Fallen SMP | Joined On {row[4].split(' ')[0]}")

                await ctx.respond(
                    embed=embed,
                    view=View_Character_Info(user_id=user.id, user=user),
                )

            else:
                embed = discord.Embed(
                    title=":x: Player Data Not Found",
                    description="It Seems Like There Isn't Any Data For You. Make Sure To Submit The Whitelist Application.",
                    color=discord.Color.red(),
                )
                await ctx.respond(embed=embed, ephemeral=True)

        except Exception as e:
            print(f"[ - ] Whitelist COG : Error : {e}")
            await ctx.respond(
                f"[ - ] Whitelist COG : Error : \n```{e}```",
                ephemeral=True,
                delete_after=5,
            )

            ErrorChannel = self.bot.get_channel(ERROR_CHANNEL)
            await ErrorChannel.send(f"[ - ] Whitelist COG : Error : \n```{e}```")

    @wl.command(name="list", description="List All Whitelist Applications")
    async def list(self, ctx):
        try:
            self.cursor.execute("SELECT * FROM Users")
            rows = self.cursor.fetchall()

            if not rows:
                await ctx.respond("No Whitelist Applications Found", ephemeral=True)
                return

            members_per_page = 5
            pages_content = []

            for i in range(0, len(rows), members_per_page):
                members_on_page = rows[i : i + members_per_page]
                embed = discord.Embed(title="Whitelisted Members", color=0xC8E7E2)

                for index, member in enumerate(members_on_page, start=i + 1):
                    user_id = member[0]
                    username = member[1]

                    embed.add_field(
                        name=f"{index}. {username}",
                        value=f"User : <@{user_id}>",
                        inline=False,
                    )

                embed.set_footer(text=f"Total Players: {len(rows)} | Fallen SMP")
                pages_content.append(embed)

            pages = len(rows) // members_per_page + 1

            paginator = Paginator(
                pages=pages_content,
                show_indicator=True,
                use_default_buttons=False,
                disable_on_timeout=True,
                custom_buttons=[
                    PaginatorButton(
                        "first", label="<<", style=discord.ButtonStyle.green, row=1
                    ),
                    PaginatorButton("prev", label="<", style=discord.ButtonStyle.green),
                    PaginatorButton(
                        "page_indicator",
                        style=discord.ButtonStyle.gray,
                        disabled=True,
                        row=0,
                    ),
                    PaginatorButton(
                        f"⬜",
                        style=discord.ButtonStyle.gray,
                        disabled=True,
                        row=1,
                    ),
                    PaginatorButton("next", label=">", style=discord.ButtonStyle.green),
                    PaginatorButton(
                        "last", label=">>", style=discord.ButtonStyle.green, row=1
                    ),
                ],
            )

            await paginator.respond(ctx, ephemeral=False)

        except Exception as e:
            print(f"[ - ] Whitelist COG : Error : {e}")
            await ctx.respond(
                f"[ - ] Whitelist COG : Error : \n```{e}```",
                ephemeral=True,
                delete_after=5,
            )

            error_channel = self.bot.get_channel(ERROR_CHANNEL)
            await error_channel.send(f"[ - ] Whitelist COG : Error : \n```{e}```")

    @bridge.bridge_command(
        name="whitelist", description="Whitelist Application For Fallen SMP"
    )
    async def whitelist(self, ctx):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM Users WHERE ID = %s", (ctx.author.id,))

            row = cursor.fetchone()

            if row:
                embed = discord.Embed(
                    title="Application Already Submitted",
                    description="You Are Already WhiteListed. \nIf You Want To Update Your Application, Contact The Admins.",
                    color=0xF2D5CD,
                )

                await ctx.respond(embed=embed, ephemeral=True)

            else:
                embed = discord.Embed(
                    title="Whitelist Application",
                    description="Please Answer The Following Questions To Apply For Whitelist",
                    color=0xCDE7DF,
                )

                embed.add_field(
                    name="Server IP", value="play.fallensmp.xyz", inline=True
                )
                embed.add_field(name="Server Version", value="1.21", inline=True)

                embed.set_image(
                    url="https://media.discordapp.net/attachments/1258116175758364673/1266046626548678819/FALLEN_SMP.gif?ex=66a3b94d&is=66a267cd&hm=b80fdae6a297eeb179347003f57935b5edf601dfbb5433937e9cbb4a9f1493c5&=&width=1024&height=320"
                )

                await ctx.respond(
                    embed=embed,
                    view=WhitelistApplication(
                        interaction_user=ctx.author,
                        user=ctx.author,
                        bot=self.bot,
                    ),
                )

        except Exception as e:
            print(f"[ - ] Whitelist COG : Error : {e}")
            await ctx.respond(
                f"[ - ] Whitelist COG : Error : \n```{e}```",
                ephemeral=True,
                delete_after=5,
            )

            ErrorChannel = self.bot.get_channel(ERROR_CHANNEL)
            await ErrorChannel.send(f"[ - ] Whitelist COG : Error : \n```{e}```")


# =================================================================================================== #


class WhitelistApplication(discord.ui.View):
    def __init__(self, interaction_user: discord.User, bot: commands.Bot, user) -> None:
        super().__init__(timeout=None)
        self.interaction_user = interaction_user
        self.bot = bot

        self.user = user

    @discord.ui.button(label="Whitelist Form", style=discord.ButtonStyle.secondary)
    async def whitelist_form(self, button, interaction):

        if interaction.user.id != self.interaction_user.id:
            await interaction.response.send_message(
                "You Are Not Allowed To Use This Button", ephemeral=True
            )

        else:
            await interaction.response.send_modal(
                WhitelistModal(
                    title="Fallen SMP Whitelist Form",
                    bot=self.bot,
                    user=self.interaction_user,
                )
            )


# =================================================================================================== #


class WhitelistModal(discord.ui.Modal):
    def __init__(self, bot, user, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.user = user
        self.bot = bot

        self.qna = {
            "Role Earned by Killing Player Unwilling": "outlaw",
            "Where Is PVP Allowed": "pvp arena",
            "Can I Build Without Permission": "no",
            "Whom To Ask Permission From Before Building": ["duke", "admin"],
            "Who Has The Ultimate Authority": "emperor",
        }

        self.ques = random.choice(list(self.qna.keys()))

        self.add_item(
            discord.ui.InputText(
                label="Minecraft Username", placeholder="Enter Your Minecraft Username"
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
                style=discord.InputTextStyle.multiline,
            )
        )
        self.add_item(
            discord.ui.InputText(
                label="Agree To Follow Your Character Backstory ?",
                placeholder="Answer Yes or No",
            )
        )
        self.add_item(
            discord.ui.InputText(
                label=self.ques,
                placeholder="Read The Rules / Guide For Answer",
            )
        )

    async def callback(self, interaction: discord.Interaction):
        connection = mysql.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            database=os.getenv("DB_NAME"),
        )

        try:
            cursor = connection.cursor()

            character_backstory = self.children[2].value
            agree_backstory = self.children[3].value
            answer = self.children[4].value

            if agree_backstory.lower() != "yes":
                embed = discord.Embed(
                    title="Whitelist Form Not Submitted",
                    description="### Character Backstory Not Followed\nYou Must Agree To Follow Your Character Backstory",
                    color=discord.Color.red(),
                )

                await interaction.user.send(embed=embed)
                await interaction.response.send_message(
                    f"<@{interaction.user.id}>",
                    embed=embed,
                    ephemeral=True,
                )
                return

            if answer.lower() != self.qna[self.ques]:
                embed = discord.Embed(
                    title="Whitelist Form Not Submitted",
                    description="### Incorrect Answer\nYou Must Answer The Question Correctly",
                    color=discord.Color.red(),
                )

                await interaction.user.send(embed=embed)
                await interaction.response.send_message(
                    f"<@{interaction.user.id}>",
                    embed=embed,
                    ephemeral=True,
                )
                return

            if len(character_backstory) > 3000:
                embed = discord.Embed(
                    title="Whitelist Form Not Submitted",
                    description="### Character Backstory Too Long\nCharacter Backstory Should Be Below 3000 Characters",
                    color=discord.Color.red(),
                )

                await interaction.user.send(embed=embed)
                await interaction.response.send_message(
                    f"<@{interaction.user.id}>",
                    embed=embed,
                    ephemeral=True,
                )
                return

            if len(character_backstory) < 100 and self.user.id not in ADMINS:
                embed = discord.Embed(
                    title="Whitelist Form Not Submitted",
                    description="### Character Backstory Too Short\nCharacter Backstory Should Be Above 100 Characters",
                    color=discord.Color.red(),
                )

                await interaction.user.send(embed=embed)
                await interaction.response.send_message(
                    f"<@{interaction.user.id}>",
                    embed=embed,
                    ephemeral=True,
                )
                return

            cursor.execute(
                "INSERT INTO Users ( ID, Username, Gender, Backstory, Timestamp ) VALUES ( %s, %s, %s, %s, %s )",
                (
                    interaction.user.id,
                    self.children[0].value,
                    self.children[1].value,
                    self.children[2].value,
                    str(datetime.datetime.now()),
                ),
            )

            connection.commit()

            print(f"[ + ] Whitelist COG : User Inserted : {interaction.user.id}")

            embed = discord.Embed(
                title="Whitelist Form Submitted",
                description="### Your Whitelist Application Has Been Submitted",
                color=0x99B9B3,
            )

            try:
                await interaction.user.send(embed=embed)
            except Exception as e:
                pass

            await interaction.response.send_message(
                f"<@{interaction.user.id}>",
                embed=embed,
                ephemeral=True,
            )

            embed = discord.Embed(
                title=f"Whitelist Application From {interaction.user.display_name}({interaction.user.id})",
                description=f"Username : {self.children[0].value}\nCharacter Gender : {self.children[1].value}\n\nCharacter Backstory : {character_backstory}\n\nAgree To Follow Backstory : {agree_backstory}\n{self.ques} : {answer}",
                color=0x99B9B3,
            )

            WhitelistChannel = self.bot.get_channel(WHITELIST_CHANNEL)
            await WhitelistChannel.send(
                embed=embed,
                view=WhitelistButtons(interaction.user.id, self.user, self.bot),
            )

        except Exception as e:
            print(f"[ - ] Whitelist COG : Error : {e}")
            await interaction.response.send_message(
                f"[ - ] Whitelist COG : Error : \n```{e}```", ephemeral=True
            )


# =================================================================================================== #


class WhitelistButtons(discord.ui.View):
    def __init__(self, user_id, user, bot) -> None:
        super().__init__(timeout=None)
        self.user_id = user_id
        self.user = user
        self.bot = bot

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.success)
    async def accept_button_callback(self, button, interaction):

        if interaction.user.id not in ADMINS:
            await interaction.response.send_message(
                "You Are Not Allowed To Use This Button", ephemeral=True
            )

        else:

            connection = mysql.connect(
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASS"),
                database=os.getenv("DB_NAME"),
            )

            cursor = connection.cursor()
            cursor.execute("SELECT * FROM Users WHERE ID = %s", (self.user_id,))

            row = cursor.fetchone()

            if row:
                username = row[1]

                ConsoleChannel = self.bot.get_channel(CONSOLE_CHANNEL)
                await ConsoleChannel.send(f"whitelist add {self.user}")

                embed = discord.Embed(
                    title="User Whitelisted",
                    description=f"User `{username}` Has Been Whitelisted",
                    color=0xD5E4CF,
                )

                user_embed = discord.Embed(
                    title="Whitelist Application Accepted",
                    description=f"Your Whitelist Application Has Been Accepted. \n## Join Now : `play.fallensmp.xyz`",
                    color=0xD5E4CF,
                )

                try:
                    User = self.bot.get_user(self.user_id)
                    await User.send(embed=user_embed)
                except Exception as e:
                    pass

                await interaction.response.send_message(embed=embed, ephemeral=True)

            else:
                embed = discord.Embed(
                    title="User Not Found",
                    description=f"No Whitelist Application Found For **{self.user.display_name}**.",
                    color=discord.Color.red(),
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Reject", style=discord.ButtonStyle.danger)
    async def reject_button_callback(self, button, interaction):

        if interaction.user.id not in ADMINS:
            await interaction.response.send_message(
                "You Are Not Allowed To Use This Button", ephemeral=True
            )

        else:
            await interaction.response.send_modal(
                WhitelsitRejectModal(
                    title="Whitelist Application Rejection",
                    user=self.user,
                    bot=self.bot,
                )
            )


# =================================================================================================== #


class WhitelsitRejectModal(discord.ui.Modal):
    def __init__(self, bot, user, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.user = user

        self.add_item(
            discord.ui.InputText(
                label="Reason For Rejection",
                placeholder="Enter The Reason For Rejection",
                style=discord.InputTextStyle.multiline,
            )
        )

    async def callback(self, interaction: discord.Interaction):

        embed = discord.Embed(
            title="Whitelist Application Rejected",
            description="### Your Whitelist Application Has Been Rejected",
            color=0xFBEADC,
        )

        reason = self.children[0].value

        embed.add_field(
            name="Reason For Rejection",
            value=reason,
            inline=False,
        )

        try:
            await interaction.user.send(embed=embed)
        except Exception as e:
            pass

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True,
        )


# =================================================================================================== #


class View_Character_Info(discord.ui.View):
    def __init__(self, user_id, user) -> None:
        super().__init__(timeout=None)
        self.user_id = user_id
        self.user = user

    @discord.ui.button(label="View Character Info", style=discord.ButtonStyle.secondary)
    async def view_button_callback(self, button, interaction):

        connection = mysql.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            database=os.getenv("DB_NAME"),
        )

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Users WHERE ID = %s", (self.user_id,))

        row = cursor.fetchone()

        if row:
            embed = discord.Embed(
                title="Character Information",
                description=f"Character Gender : **{row[2]}**\n\nCharacter Backstory : **{row[3]}**",
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)


# =================================================================================================== #


def setup(bot: commands.Bot):
    bot.add_cog(Whitelist(bot))
