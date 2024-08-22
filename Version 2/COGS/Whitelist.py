import os
import random
import pymongo
import discord
import asyncio
import datetime
from pymongo import MongoClient
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
        self.mongo_client = MongoClient(os.getenv("MONGO_URI"))
        self.db = self.mongo_client["Users"]
        self.collection = self.db["UserData"]

        # self.bot.add_view(WhitelistButtons(user_id=0, user=None, bot=bot))
        # self.bot.add_view(WhitelistRejectModal(bot=bot, user=None))

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

                document = {
                    "ID": user.id,
                    "Username": username,
                    "Gender": gender,
                    "Backstory": backstory,
                    "Timestamp": datetime.datetime.now(),
                }

                self.collection.insert_one(document)

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

    @wl.command(name="search", description="Search For A User In The Whitelist", aliases=["s"])
    async def search(self, ctx, user):
        if ctx.author.id not in ADMINS:
            await ctx.respond(
                "You Do Not Have Permission To Use This Command",
                ephemeral=True,
                delete_after=5,
            )
        else:
            try:
                if user.isdigit():
                    user_id = int(user)
                    document = self.collection.find_one({"ID": user_id})

                    if document:
                        username = document.get("Username")

                        embed = discord.Embed(
                            title="User Found",
                            description=f"User `{username}` Found In The Whitelist",
                            color=0xD5E4CF,
                        )

                        await ctx.respond(embed=embed, ephemeral=True)
                    else:
                        embed = discord.Embed(
                            title="User Not Found",
                            description=f"No Whitelist Application Found For User ID `{user}`.",
                            color=discord.Color.red(),
                        )
                        await ctx.respond(embed=embed)
                else:
                    document = self.collection.find_one(
                        {"Username": {"$regex": f"^{user}$", "$options": "i"}}
                    )

                    if document:
                        user_id = document.get("ID")

                        embed = discord.Embed(
                            title="User Found",
                            description=f"User <@{user_id}> Found In The Whitelist",
                            color=0xD5E4CF,
                        )

                        await ctx.respond(embed=embed, ephemeral=True)
                    else:
                        embed = discord.Embed(
                            title="User Not Found",
                            description=f"No Whitelist Application Found For Minecraft Username `{user}`.",
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

    @wl.command(name="add", description="Add A User To The Whitelist")
    async def add(self, ctx, user: discord.User):
        if ctx.author.id not in ADMINS:
            await ctx.respond(
                "You Do Not Have Permission To Use This Command",
                ephemeral=True,
                delete_after=5,
            )
        else:
            try:
                document = self.collection.find_one({"ID": user.id})

                if document:
                    username = document.get("Username")

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

    @wl.command(name="remove", description="Remove A User From The Whitelist", aliases=["r", "del"])
    async def remove(self, ctx, user: discord.User):
        if ctx.author.id not in ADMINS:
            await ctx.respond(
                "You Do Not Have Permission To Use This Command",
                ephemeral=True,
                delete_after=5,
            )
        else:
            try:
                document = self.collection.find_one({"ID": user.id})

                if document:
                    username = document.get("Username")

                    self.collection.delete_one({"ID": user.id})

                    print(f"[ + ] Whitelist COG : User Removed : {user.id}")

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

        await ctx.defer()

        if user == None:
            user = ctx.author

        try:
            # Fetch user data from MongoDB
            document = self.collection.find_one({"ID": user.id})

            if document:
                username = document.get("Username")
                gender = document.get("Gender")
                backstory = document.get("Backstory")
                timestamp = document.get("Timestamp")

                embed = discord.Embed(
                    title="Player Information",
                    description=f"Details For **{user.display_name}**",
                    color=0xDDDDBD,
                )

                embed.add_field(
                    name="Discord User ID",
                    value=f"{document['ID']}",
                    inline=False,
                )

                embed.add_field(name="Minecraft Username", value=username, inline=False)

                try:
                    avatar = user.avatar.url
                    embed.set_thumbnail(url=user.avatar.url)
                except Exception as e:
                    pass

                embed.set_footer(
                    text=f"Fallen SMP | Joined On {timestamp.split(' ')[0]}"
                )

                await ctx.respond(
                    embed=embed,
                    view=View_Character_Info(
                        user_id=user.id, user=user, gender=gender, backstory=backstory
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
            rows = list(self.collection.find())

            if not rows:
                await ctx.respond("No Whitelist Applications Found", ephemeral=True)
                return

            members_per_page = 5
            pages_content = []

            for i in range(0, len(rows), members_per_page):
                members_on_page = rows[i : i + members_per_page]
                embed = discord.Embed(title="Whitelisted Members", color=0xC8E7E2)

                for index, member in enumerate(members_on_page, start=i + 1):
                    user_id = member.get("ID")
                    username = member.get("Username")

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
        name="whitelist", description="Whitelist Application For Fallen SMP", aliases=["wh"]
    )
    async def whitelist(self, ctx):
        try:
            document = self.collection.find_one({"ID": ctx.author.id})

            if document:
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

            await interaction.resonse.send_message(
                "You Are Not Allowed To Use This Button", ephemeral=True
            )

            message_id = interaction.message.id

            button.disabled = True
            await interaction.followup.edit_message(message_id=message_id, view=self)

        else:

            await interaction.response.send_modal(
                WhitelistModal(
                    title="Fallen SMP Whitelist Form",
                    user=self.interaction_user,
                    bot=self.bot,
                )
            )

            message_id = interaction.message.id

            self.disable_all_items()
            await interaction.followup.edit_message(message_id=message_id, view=self)


# =================================================================================================== #


class WhitelistModal(discord.ui.Modal):
    def __init__(self, bot, user, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.user = user
        self.bot = bot

        self.mongo_client = MongoClient(os.getenv("MONGO_URI"))
        self.db = self.mongo_client["Users"]
        self.collection = self.db["UserData"]

        self.qna = {
            "Role Earned by Killing Player Unwilling": "outlaw",
            "Where Is PVP Allowed": "pvp arena",
            "Can I Build Without Permission": "no",
            "Whom To Ask Permission From Before Building": "duke",
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

        await interaction.response.defer(ephemeral=True)

        try:

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
                await interaction.followup.send(
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
                await interaction.followup.send(
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
                await interaction.followup.send(
                    f"<@{interaction.user.id}>",
                    embed=embed,
                    ephemeral=True,
                )
                return

            if len(character_backstory) < 100:
                embed = discord.Embed(
                    title="Whitelist Form Not Submitted",
                    description="### Character Backstory Too Short\nCharacter Backstory Should Be Above 100 Characters",
                    color=discord.Color.red(),
                )

                await interaction.user.send(embed=embed)
                await interaction.followup.send(
                    f"<@{interaction.user.id}>",
                    embed=embed,
                    ephemeral=True,
                )
                return

            print(f"[ + ] Whitelist COG : User Inserted : {interaction.user.id}")

            embed = discord.Embed(
                title="Whitelist Form Submitted",
                description="### Your Whitelist Application Has Been Submitted\nPlease Wait For The Admins To Review Your Application",
                color=0x99B9B3,
            )

            try:
                user = self.bot.get_user(interaction.user.id)
                await user.send(embed=embed)
            except Exception as e:
                print(f"[ - ] Whitelist COG : Error : {e}")

            await interaction.followup.send(
                embed=embed,
                ephemeral=True,
            )

            embed = discord.Embed(
                title=f"Whitelist Application From {interaction.user.display_name} ({interaction.user.id})",
                description=f"Username : {self.children[0].value}\nCharacter Gender : {self.children[1].value}\n\n**Character Backstory** : {character_backstory}\n\nAgree To Follow Backstory : {agree_backstory}\n{self.ques} : {answer}",
                color=0x99B9B3,
            )

            WhitelistChannel = self.bot.get_channel(WHITELIST_CHANNEL)
            await WhitelistChannel.send(
                embed=embed,
                view=WhitelistButtons(interaction.user.id, self.user, main_embed=embed),
            )

            self.collection.insert_one(
                {
                    "ID": interaction.user.id,
                    "Username": self.children[0].value,
                    "Gender": self.children[1].value,
                    "Backstory": character_backstory,
                    "Timestamp": datetime.datetime.now().isoformat(),
                }
            )

        except Exception as e:
            print(f"[ - ] Whitelist COG : Error : {e}")
            await interaction.response.send_message(
                f"[ - ] Whitelist COG : Error : \n```{e}```", ephemeral=True
            )


# =================================================================================================== #


class WhitelistButtons(discord.ui.View):
    def __init__(
        self, user_id: int = None, user: discord.Member = None, main_embed=None
    ):
        super().__init__(timeout=None)
        self.main_embed = main_embed
        self.user_id = user_id
        self.user = user

        self.mongo_client = MongoClient(os.getenv("MONGO_URI"))
        self.db = self.mongo_client["Users"]
        self.collection = self.db["UserData"]

    @discord.ui.button(
        label="Accept", custom_id="accept", style=discord.ButtonStyle.success
    )
    async def accept_button_callback(self, button, interaction):

        if interaction.user.id not in ADMINS:
            await interaction.response.send_message(
                "You Are Not Allowed To Use This Button", ephemeral=True
            )

        else:

            document = self.collection.find_one({"ID": self.user_id})

            if document:
                username = document.get("Username")

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

                message_id = interaction.message.id

                self.disable_all_items()
                button.style = discord.ButtonStyle.secondary

                self.main_embed.add_field(
                    name="Whitelist Accepted By",
                    value=f"{interaction.user.display_name}",
                    inline=False,
                )

                await interaction.followup.edit_message(
                    embed=self.main_embed, message_id=message_id, view=self
                )

            else:
                embed = discord.Embed(
                    title="User Not Found",
                    description=f"No Whitelist Application Found For **{self.user.display_name}**.",
                    color=discord.Color.red(),
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)

                message_id = interaction.message.id

                self.disable_all_items()
                button.style = discord.ButtonStyle.secondary

                self.main_embed.add_field(
                    name="ERROR", value="User Not Found", inline=False
                )

                await interaction.followup.edit_message(
                    embed=self.main_embed, message_id=message_id, view=self
                )

    @discord.ui.button(
        label="Reject", custom_id="reject", style=discord.ButtonStyle.danger
    )
    async def reject_button_callback(self, button, interaction):

        if interaction.user.id not in ADMINS:
            await interaction.response.send_message(
                "You Are Not Allowed To Use This Button", ephemeral=True
            )

            message_id = interaction.message.id

            self.disable_all_items()
            button.style = discord.ButtonStyle.secondary
            await interaction.followup.edit_message(message_id=message_id, view=self)

        else:
            await interaction.response.send_modal(
                WhitelistRejectModal(
                    main_embed=self.main_embed,
                    mgs_id=interaction.message.id,
                    user=self.user,
                    bot=self.bot,
                )
            )

            message_id = interaction.message.id

            self.disable_all_items()
            button.style = discord.ButtonStyle.secondary

            self.main_embed.add_field(
                name="Whitelist Rejected By",
                value=f"{interaction.user.display_name}",
                inline=False,
            )

            self.main_embed.color = discord.Color.red()

            await interaction.followup.edit_message(
                embed=self.main_embed, message_id=message_id, view=self
            )


# =================================================================================================== #


class WhitelistRejectModal(discord.ui.Modal):
    def __init__(
        self,
        user: discord.Member,
        bot: commands.Bot,
        main_embed,
        mgs_id,
        *args,
        **kwargs,
    ):
        super().__init__(title="Whitelist Application Rejection")
        self.main_embed = main_embed
        self.msg_id = mgs_id
        self.user = user
        self.bot = bot

        self.mongo_client = MongoClient(os.getenv("MONGO_URI"))
        self.db = self.mongo_client["Users"]
        self.collection = self.db["UserData"]

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
            description=f"Your whitelist application has been rejected.\n**Reason:** {self.children[0].value}",
            color=discord.Color.red(),
        )

        try:
            await self.user.send(embed=embed)

        except Exception as e:
            pass

        embed = discord.Embed(
            title="Whitelist Application Rejected",
            description=f"Whitelist Application Rejected For {self.user.display_name}",
            color=discord.Color.red(),
        )

        embed.add_field(
            name="Reason For Rejection", value=self.children[0].value, inline=False
        )

        document = self.collection.find_one({"ID": self.user.id})

        if document:
            username = document.get("Username")

            self.collection.delete_one({"ID": self.user.id})

            ConsoleChannel = self.bot.get_channel(CONSOLE_CHANNEL)
            await ConsoleChannel.send(f"whitelist remove {username}")

            self.collection.delete_one({"ID": self.user.id})

            print(f"[ + ] Whitelist COG : User Removed : {self.user.id}")

        await interaction.respond(embed=embed)


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


@commands.Cog.listener()
async def on_ready(self):
    await self.bot.add_view(WhitelistButtons())
    await self.bot.add_view(WhitelistRejectModal())


def setup(bot):
    bot.add_cog(Whitelist(bot))
