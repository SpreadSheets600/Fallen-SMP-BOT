import os
import json
import random
import pymongo
import discord
import asyncio
import datetime
from datetime import datetime
from discord.commands import *
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

MODS = [
    1273283762624663625,
    1147935418508132423,
]

WHITELIST_CHANNEL = 1267512076222595122
CONSOLE_CHANNEL = 1263898954999922720
ERROR_CHANNEL = 1275759089024241797

COOLDOWN_ACTIVE = False
COOLDOWN = 30

# =================================================================================================== #


class Whitelist(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.mongo_client = MongoClient(os.getenv("MONGO_URI"))
        self.db = self.mongo_client["Users"]
        self.collection = self.db["UserData"]

        try:
            with open("BLOCKED.json", "r") as f:
                self.blocked = json.load(f)
        except Exception as e:
            with open("BLOCKED.json", "w") as f:
                json.dump([], f)
                self.blocked = []

        async def set_cooldown():
            global COOLDOWN_ACTIVE
            COOLDOWN_ACTIVE = True
            await asyncio.sleep(COOLDOWN)
            COOLDOWN_ACTIVE = False

    wl = SlashCommandGroup(name="wl", description="Whitelist Commands")

    @wl.command(name="insert", description="Insert A User Into The Whitelist")
    async def insert(
        self, ctx, user: discord.User, username: str, gender: str, backstory: str
    ):
        await ctx.defer(ephemeral=True)

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
                    "Timestamp": datetime.now(),
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

    @wl.command(
        name="search", description="Search For A User In The Whitelist", aliases=["s"]
    )
    async def search(self, ctx, user):
        await ctx.defer(ephemeral=True)

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
        await ctx.defer(ephemeral=True)

        if ctx.author.id not in ADMINS and ctx.author.id not in MODS:
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

                    embed.add_field(
                        name="Main Server",
                        value="[Join Now](https://discord.gg/2GWK7NjYek)",
                        inline=False,
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

    @wl.command(
        name="remove",
        description="Remove A User From The Whitelist",
        aliases=["r", "del"],
    )
    async def remove(self, ctx, user: discord.User):
        await ctx.defer(ephemeral=True)

        if ctx.author.id not in ADMINS and ctx.author.id not in MODS:
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

    @wl.command(name="list", description="List All Whitelist Applications")
    async def list(self, ctx):
        await ctx.defer(ephemeral=True)

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

    @commands.slash_command(
        name="whitelist",
        description="Whitelist Application For Fallen SMP",
        aliases=["wh"],
    )
    async def whitelist(self, ctx):
        await ctx.defer(ephemeral=True)

        try:
            document = self.collection.find_one({"ID": ctx.author.id})

            with open("BLOCKED.json", "r") as f:
                self.blocked = json.load(f)

                blocked_data = self.blocked["Blocked"]

            if ctx.author.id in blocked_data:
                embed = discord.Embed(
                    title="Application Blocked",
                    description="You Have Been Blocked From Submitting The Application. \nIf You Think This Is A Mistake, Contact The Admins.",
                    color=0xF2D5CD,
                )

                await ctx.respond(embed=embed, ephemeral=True)

            elif document:
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

    @commands.slash_command(
        name="guide",
        description="Guide For Fallen SMP",
        aliases=["g"],
    )
    async def guide(self, ctx):
        await ctx.defer(ephemeral=True)

        embed = discord.Embed(
            title=":book: Server Guide",
            description="Choose A Guide Topic \n\n**Basic Roles Info** : Learn About Server Roles\n**How To Get Whitelisted** : Learn about Whitelisting Process\n**How To Write A Backstory** : Learn about Writing Character Backstory",
            color=0x2F3136,
        )

        await ctx.respond(embed=embed, view=GuideMenu())

    @commands.slash_command(
        name="rules",
        description="Rules For Fallen SMP",
        aliases=["r"],
    )
    async def rules(self, ctx):
        await ctx.defer(ephemeral=True)

        rules = """
            1. **Refrain from Unnecessary PvP**
            > If you want to engage in PvP, arrange it with others and ensure everyone agrees. Unplanned PvP can disrupt the game experience.

            2. **Roleplay as Your Character**
            > Since this is a roleplay server, you must act as your character described in your character story. This enhances the immersive experience for everyone.

            3. **Value Your Life In Game As Much As In Real Life** 
            > Treat your in-game life with care and caution, just as you would in reality. This rule ensures a more realistic and engaging gameplay experience.

            4. **No Chat Toxicity**
            > Toxic behaviour in chat is strictly prohibited. Maintain a respectful and positive environment for all players.

            5. **No Stealing**
            > Stealing from other players is not allowed. Engaging in theft can lead to being labelled as an outlaw and facing consequences.

            6. **Obey Orders from Duke, King, and Emperor**
            > You must follow the orders issued by the Duke, King, and Emperor. This maintains the hierarchical structure and order within the server.

            7. **Building Permissions Required**
            > To build a house, you must obtain permission from the Duke. This ensures organized and planned development within the server.
            """

        embed = discord.Embed(
            title="Server Rules",
            description=rules,
            color=0x2F3136,
        )

        await ctx.respond(embed=embed)


# =================================================================================================== #


class WhitelistApplication(discord.ui.View):
    def __init__(self, interaction_user: discord.User, bot: commands.Bot, user) -> None:
        super().__init__(timeout=None)
        self.interaction_user = interaction_user
        self.bot = bot

        self.user = user

        button_support = discord.ui.Button(
            label="Main Server",
            style=discord.ButtonStyle.url,
            url="https://discord.gg/2GWK7NjYek",
        )
        self.add_item(button_support)

    @discord.ui.button(label="Guide", style=discord.ButtonStyle.secondary)
    async def guide_button_callback(self, button, interaction):
        await interaction.response.defer(ephemeral=True)

        if interaction.user.id != self.interaction_user.id:

            await interaction.folloup.send(
                "You Are Not Allowed To Use This Button", ephemeral=True
            )

        else:
            embed = discord.Embed(
                title=":book: Server Guide",
                description="Choose A Guide Topic \n\n**Basic Roles Info** : Learn About Server Roles\n**How To Get Whitelisted** : Learn about Whitelisting Process\n**How To Write A Backstory** : Learn about Writing Character Backstory",
                color=0x2F3136,
            )

            await interaction.folloup.send(
                embed=embed, ephemeral=True, view=GuideMenu()
            )

    @discord.ui.button(label="Rules", style=discord.ButtonStyle.secondary)
    async def rule_button_callback(self, button, interaction):
        await interaction.response.defer(ephemeral=True)

        if interaction.user.id != self.interaction_user.id:

            await interaction.folloup.send(
                "You Are Not Allowed To Use This Button", ephemeral=True
            )

        else:

            rules = """
                1. **Refrain from Unnecessary PvP**
                > If you want to engage in PvP, arrange it with others and ensure everyone agrees. Unplanned PvP can disrupt the game experience.

                2. **Roleplay as Your Character**
                > Since this is a roleplay server, you must act as your character described in your character story. This enhances the immersive experience for everyone.

                3. **Value Your Life In Game As Much As In Real Life** 
                > Treat your in-game life with care and caution, just as you would in reality. This rule ensures a more realistic and engaging gameplay experience.

                4. **No Chat Toxicity**
                > Toxic behaviour in chat is strictly prohibited. Maintain a respectful and positive environment for all players.

                5. **No Stealing**
                > Stealing from other players is not allowed. Engaging in theft can lead to being labelled as an outlaw and facing consequences.

                6. **Obey Orders from Duke, King, and Emperor**
                > You must follow the orders issued by the Duke, King, and Emperor. This maintains the hierarchical structure and order within the server.

                7. **Building Permissions Required**
                > To build a house, you must obtain permission from the Duke. This ensures organized and planned development within the server.
                """

            embed = discord.Embed(
                title="Server Rules",
                description=rules,
                color=0x2F3136,
            )

            await interaction.folloup.send(embed=embed, ephemeral=True)

    @discord.ui.button(label="Form", style=discord.ButtonStyle.secondary)
    async def whitelist_form(self, button, interaction):

        if interaction.user.id != self.interaction_user.id:

            await interaction.response.send_message(
                "You Are Not Allowed To Use This Button", ephemeral=True
            )

        else:

            try:
                await interaction.response.send_modal(
                    WhitelistModal(
                        title="Fallen SMP Whitelist Form",
                        user=self.interaction_user,
                        bot=self.bot,
                    )
                )

                message_id = interaction.message.id
                button.disabled = True
                await interaction.followup.edit_message(
                    message_id=message_id, view=self
                )

            except Exception as e:
                await interaction.response.send_message(
                    "Please Try Again, The Form Expired", ephemeral=True
                )


# =================================================================================================== #
class GuideMenu(discord.ui.View):
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
                description="Learn About Whitelisting Process",
            ),
            discord.SelectOption(
                label="How To Write A Backstory",
                description="Learn About Writing Character Backstory",
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


# =================================================================================================== #
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


# =================================================================================================== #


class WhitelistModal(discord.ui.Modal):
    def __init__(self, bot, user, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.user = user
        self.bot = bot

        self.mongo_client = MongoClient(os.getenv("MONGO_URI"))
        self.db = self.mongo_client["Users"]

        self.collection = self.db["UserData"]
        self.stocks = self.db["UserStocks"]
        self.crypto = self.db["UserCrypto"]

        self.qna = {
            "Role Earned by Killing Player Unwilling": "outlaw",
            "Where Is PVP Allowed": ["pvp arena", "arena"],
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
        global COOLDOWN_ACTIVE

        try:
            await interaction.response.defer(ephemeral=True)

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

            if isinstance(self.qna[self.ques], list):
                if answer.lower() not in self.qna[self.ques]:
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
                "<@727012870683885578> <@1188730953217097811> <@664157606587138048> <@896411007797325824> <@437622938242514945> <@1147935418508132423> <@1273283762624663625>",
                embed=embed,
                view=WhitelistButtons(
                    interaction.user.id, self.user, self.bot, main_embed=embed
                ),
            )

            if not COOLDOWN_ACTIVE:
                COOLDOWN_ACTIVE = True
                asyncio.create_task(
                    self.handle_cooldown_and_insert(interaction, character_backstory)
                )

        except Exception as e:
            print(f"[ - ] Whitelist COG : Error : {e}")

    async def handle_cooldown_and_insert(self, interaction, character_backstory):
        global COOLDOWN_ACTIVE

        self.collection.insert_one(
            {
                "ID": interaction.user.id,
                "Username": self.children[0].value,
                "Gender": self.children[1].value,
                "Backstory": character_backstory,
                "Timestamp": datetime.now().isoformat(),
            }
        )

        self.stocks.insert_one(
            {
                "ID": interaction.user.id,
                "Username": self.children[0].value,
                "StocksAmount": {
                    "AMD": 0,
                    "INTC": 0,
                    "MSFT": 0,
                    "AAPL": 0,
                    "GOOGL": 0,
                },
                "StocksBuyPrice": {
                    "AMD_P": 0,
                    "INTC_P": 0,
                    "MSFT_p": 0,
                    "AAPL_P": 0,
                    "GOOGL_p": 0,
                },
                "Timestamp": datetime.now().isoformat(),
            }
        )

        self.crypto.insert_one(
            {
                "ID": interaction.user.id,
                "Username": self.children[0].value,
                "CryptoAmount": {"BTC": 0, "ETH": 0, "BNB": 0, "SOL": 0, "AVAX": 0},
                "CryptoBuyPrice": {
                    "BTC_P": 0,
                    "ETH_P": 0,
                    "BNB_p": 0,
                    "SOL_P": 0,
                    "AVAX_p": 0,
                },
                "Timestamp": datetime.now().isoformat(),
            }
        )

        print(f"[ + ] Whitelist COG : User Inserted : {interaction.user.id}")

        COOLDOWN_ACTIVE = False


# =================================================================================================== #


class WhitelistButtons(discord.ui.View):
    def __init__(
        self,
        user_id: int = None,
        user: discord.Member = None,
        bot=None,
        main_embed=None,
    ):
        super().__init__(timeout=None)
        self.main_embed = main_embed
        self.user_id = user_id
        self.user = user
        self.bot = bot

        self.mongo_client = MongoClient(os.getenv("MONGO_URI"))
        self.db = self.mongo_client["Users"]
        self.collection = self.db["UserData"]

    @discord.ui.button(
        label="Accept", custom_id="accept", style=discord.ButtonStyle.success
    )
    async def accept_button_callback(self, button, interaction):
        global COOLDOWN_ACTIVE
        if COOLDOWN_ACTIVE:
            await interaction.response.send_message(
                "Please Wait For The Cooldown To End\nBot Is Performing DB Operations\nBot Is Performing DB Operations", ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)

        if interaction.user.id not in ADMINS and interaction.user.id not in MODS:
            await interaction.response.send_message(
                "You Are Not Allowed To Use This Button", ephemeral=True
            )
            return

        await interaction.followup.send(
            "Accepting User Application - Adding Data .....", ephemeral=True
        )

        document = self.collection.find_one({"ID": self.user_id})

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

            try:
                User = self.bot.get_user(self.user_id)
                await User.send(embed=user_embed)
            except Exception as e:
                print(f"Failed to send DM to user {self.user_id}: {e}")

            await interaction.followup.send(embed=embed, ephemeral=True)

            message_id = interaction.message.id

            self.disable_all_items()
            button.style = discord.ButtonStyle.secondary

            self.main_embed.add_field(
                name="Whitelist Accepted By",
                value=f"{interaction.user.display_name}",
                inline=False,
            )

            await interaction.message.edit(embed=self.main_embed, view=self)

        else:
            embed = discord.Embed(
                title="User Not Found",
                description=f"No Whitelist Application Found For **{self.user.display_name}**.",
                color=discord.Color.red(),
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

            message_id = interaction.message.id

            self.disable_all_items()
            button.style = discord.ButtonStyle.secondary
            await interaction.message.edit(embed=self.main_embed, view=self)

    @discord.ui.button(
        label="Reject", custom_id="reject", style=discord.ButtonStyle.danger
    )
    async def reject_button_callback(self, button, interaction):
        global COOLDOWN_ACTIVE
        if COOLDOWN_ACTIVE:
            await interaction.response.send_message(
                "Please Wait For The Cooldown To End\nBot Is Performing DB Operations", ephemeral=True
            )
            return

        if interaction.user.id not in ADMINS and interaction.user.id not in MODS:
            await interaction.response.send_message(
                "You Are Not Allowed To Use This Button", ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)

        await interaction.followup.send(
            "Rejecting User Application - Deleting Data .....", ephemeral=True
        )

        embed = discord.Embed(
            title="Whitelist Application Rejected",
            description=f"Your Whitelist Application Has Been Rejected By {interaction.user.display_name}\n\nPlease Check The Application Again",
            color=0xFBEADC,
        )

        embed.add_field(
            name="Possible Reasons",
            value="1. Incorrect Backstory\n    Please Follow The Criteria ( See Guide Point 3 )\n\n2. Existing Backstory\n    Please Write A New Backstory, Current One Is Already Used",
            inline=False,
        )

        user = self.bot.get_user(self.user_id)

        try:
            await user.send(embed=embed)
        except Exception as e:
            print(f"Failed to send DM to user {self.user_id}: {e}")

        message_id = interaction.message.id

        self.main_embed.add_field(
            name="Whitelist Rejected By",
            value=f"{interaction.user.display_name}",
            inline=False,
        )

        self.main_embed.color = discord.Color.red()

        document = self.collection.find_one({"ID": self.user.id})

        if document:
            username = document.get("Username")
            self.collection.delete_one({"ID": self.user.id})

            ConsoleChannel = self.bot.get_channel(CONSOLE_CHANNEL)
            await ConsoleChannel.send(f"whitelist remove {username}")

            print(f"[ + ] Whitelist COG : User Removed : {self.user.id}")

        self.disable_all_items()
        button.style = discord.ButtonStyle.secondary

        await interaction.message.edit(embed=self.main_embed, view=self)

    @discord.ui.button(
        label="Block", custom_id="block", style=discord.ButtonStyle.danger
    )
    async def block_button_callback(self, button, interaction):
        global COOLDOWN_ACTIVE
        if COOLDOWN_ACTIVE:
            await interaction.response.send_message(
                "Please Wait For The Cooldown To End\nBot Is Performing DB Operations", ephemeral=True
            )
            return

        if interaction.user.id not in ADMINS and interaction.user.id not in MODS:
            await interaction.response.send_message(
                "You Are Not Allowed To Use This Button", ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)

        await interaction.followup.send(
            "Blocking User - Deleting Data .....", ephemeral=True
        )

        with open("BLOCKED.json", "r") as f:
            data = json.load(f)

        if "Blocked" not in data or not isinstance(data["Blocked"], list):
            data["Blocked"] = []

        print(f"[ + ] Whitelist COG : User Blocked : {self.user_id}")
        data["Blocked"].append(self.user_id)

        with open("BLOCKED.json", "w") as f:
            json.dump(data, f, indent=4)

        embed = discord.Embed(
            title="User Blocked",
            description=f"User `{self.user.display_name}` Has Been Blocked From Submitting The Application",
            color=0xFBEADC,
        )

        document = self.collection.find_one({"ID": self.user.id})

        if document:
            username = document.get("Username")
            self.collection.delete_one({"ID": self.user.id})

        user = self.bot.get_user(self.user_id)
        try:
            await user.send(embed=embed)
        except Exception as e:
            print(f"Failed to send DM to user {self.user_id}: {e}")

        await interaction.followup.send(embed=embed, ephemeral=True)

        message_id = interaction.message.id

        self.disable_all_items()
        button.style = discord.ButtonStyle.secondary

        self.main_embed.add_field(
            name="User Blocked By",
            value=f"{interaction.user.display_name}",
            inline=False,
        )

        await interaction.message.edit(embed=self.main_embed, view=self)


# =================================================================================================== #


@commands.Cog.listener()
async def on_ready(self):
    await self.bot.add_view(WhitelistButtons())
    await self.bot.add_view(WhitelistApplication())


def setup(bot):
    bot.add_cog(Whitelist(bot))
