import os
import discord
import datetime
import mysql.connector as mysql
from discord.ext import commands, bridge
from discord.ext.bridge import BridgeSlashGroup

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
        if member == None:
            member = ctx.author

        try:
            self.cursor.execute("SELECT * FROM Users WHERE ID = %s", (user.id,))

            row = self.cursor.fetchone()

            if row:
                username = row[1]

                embed = discord.Embed(
                    title="Player Information",
                    description=f"Details For **{member.display_name}**",
                    color=0xDDDDBD,
                )

                embed.add_field(
                    name="Discord User ID",
                    value=f"{row[0]}\n({str(member.display_name)})",
                    inline=False,
                )

                embed.add_field(name="Minecraft Username", value=row[1], inline=False)

                try:
                    avatar = member.avatar.url
                    embed.set_thumbnail(url=member.avatar.url)
                except Exception as e:
                    pass

                embed.set_footer(text=f"Fallen SMP | Joined On {row[6]}")

                await ctx.respond(
                    embed=embed,
                    view=View_Character_Info(user_id=member.id, user=member),
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
                description=f"Character Name : **{row[1]}**\nCharacter Gender : **{row[2]}**\n\nCharacter Backstory : **{row[3]}**",
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)

def setup(bot: commands.Bot):
    bot.add_cog(Whitelist(bot))
