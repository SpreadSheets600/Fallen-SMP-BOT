import random
import discord
import sqlite3
import traceback
from discord.ext import commands
from discord.commands import SlashCommandGroup, option

ADMINS = [
    727012870683885578,
    437622938242514945,
    243042987922292738,
    664157606587138048,
    1188730953217097811,
    896411007797325824,
]

MODS = [
    1261684685235294250,
    1147935418508132423,
]

whitelist_channel_id = 1267512076222595122
console_channel_id = 1263898954999922720
logs_channel_id = 1267512076222595122

Whitelist_ids = {}


class Whitelist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    whitelist = SlashCommandGroup(name="whitelist", description="Whitelist Commands")

    @whitelist.command(name="delete", description="Delete User's Whitelist Application")
    async def del_whitelist(
        self, ctx: discord.ApplicationContext, member: discord.Member, reason: str
    ):
        if ctx.author.id in ADMINS or ctx.author.id in MODS:
            conn = sqlite3.connect("User.db")
            cursor = conn.cursor()

            cursor.execute(
                "SELECT * FROM user_data WHERE discord_user_id = ?", (str(member.id),)
            )
            row = cursor.fetchone()

            if row:

                console_channel = self.bot.get_channel(console_channel_id)
                await console_channel.send(f"whitelist remove {row[2]}")

                cursor.execute(
                    "DELETE FROM user_data WHERE discord_user_id = ?", (str(member.id),)
                )
                cursor.execute(
                    "DELETE FROM stocks WHERE user_id = ?", (str(member.id),)
                )
                conn.commit()

                if reason == None:
                    reason = "No Reason Provided"

                if Whitelist_ids[member.id] != None:

                    message_id = Whitelist_ids[member.id]
                    channel = self.bot.get_channel(logs_channel_id)
                    message = await channel.fetch_message(message_id)

                    await message.delete()
                    del Whitelist_ids[member.id]

                embed = discord.Embed(
                    title="Whitelist Application Deleted",
                    description=f"Whitelist Application For **{member.display_name}** Has Been Deleted.",
                    color=discord.Color.green(),
                )

                embed.add_field(name="Reason", value=reason, inline=False)

                user_embed = discord.Embed(
                    title="Whitelist Application Deleted",
                    description=f"Your Whitelist Application Has Been Deleted By Admin.\nReason : {reason}",
                    color=discord.Color.red(),
                )

                user = self.bot.get_user(member.id)
                await user.send(embed=user_embed)

                await message.channel.send(embed=embed)

            else:
                embed = discord.Embed(
                    title="User Not Found",
                    description=f"No Whitelist Application Found For **{member.display_name}**.",
                    color=discord.Color.red(),
                )

            conn.close()
            await ctx.respond(embed=embed)

        else:
            await ctx.respond(
                "You Don't Have Permission To Use This Command.", ephemeral=True
            )

    @whitelist.command(name="help", description="Get Video Help For Whitelisting")
    async def help_whitelist(self, ctx: discord.ApplicationContext):

        await ctx.respond(
            "https://cdn.discordapp.com/attachments/1195302501797343243/1273306886728585420/Whitelist.mp4?ex=66be22f2&is=66bcd172&hm=da9c1be57bef3638a6f7720b5bd4883ccf208017fe839f0f04d2affabdc4f60f&"
        )

    @whitelist.command(name="add", description="Add User To Whitelist")
    @option(
        "type",
        description="Choose The Whitelist Type",
        choices=["java", "bedrock"],
    )
    async def add_whitelist(
        self, ctx: discord.ApplicationContext, member: discord.Member, type: str
    ):
        if ctx.author.id in ADMINS or ctx.author.id in MODS:
            conn = sqlite3.connect("User.db")
            cursor = conn.cursor()

            cursor.execute(
                "SELECT * FROM user_data WHERE discord_user_id = ?", (member.id,)
            )
            row = cursor.fetchone()
            conn.close()

            if row:
                character_name = row[2]

                console_channel = self.bot.get_channel(console_channel_id)
                if type == "java":
                    await console_channel.send(f"whitelist add {character_name}")
                elif type == "bedrock":
                    await console_channel.send(f"fwhitelist add {character_name}")

                embed = discord.Embed(
                    title="Whitelist Added",
                    description=f"Whitelist For **{member.display_name}** has been accepted.",
                    color=discord.Color.green(),
                )

                user_embed = discord.Embed(
                    title="Whitelist Application Accepted",
                    description=f"Your Whitelist Application Has Been Accepted. \n## Join Now : `play.fallensmp.xyz`",
                    color=discord.Color.green(),
                )

                user = self.bot.get_user(member.id)
                await user.send(embed=user_embed)

                if Whitelist_ids[member.id] != None:

                    message_id = Whitelist_ids[member.id]
                    channel = self.bot.get_channel(logs_channel_id)
                    message = await channel.fetch_message(message_id)

                    await message.add_reaction("✅")

                await ctx.respond(embed=embed)
            else:
                embed = discord.Embed(
                    title="User Not Found",
                    description=f"No Whitelist Application Found For **{member.display_name}**.",
                    color=discord.Color.red(),
                )
                await ctx.respond(embed=embed)
        else:
            await ctx.respond(
                "You Don't Have Permission To Use This Command", ephemeral=True
            )

    @whitelist.command(name="view", description="Show All Whitelisted Members")
    async def show_whitelist(self, ctx: discord.ApplicationContext):
        if ctx.author.id in ADMINS or ctx.author.id in MODS:
            conn = sqlite3.connect("User.db")
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM user_data")
            rows = cursor.fetchall()
            conn.close()

            if rows:
                embeds = []
                embed = discord.Embed(
                    title="Whitelisted Members",
                    description="List Of Whitelisted Members",
                    color=discord.Color.blue(),
                )

                for i, row in enumerate(rows):
                    if i > 0 and i % 5 == 0:
                        embeds.append(embed)
                        embed = discord.Embed(
                            title="Whitelisted Members (Continued)",
                            color=discord.Color.blue(),
                        )

                    member = ctx.guild.get_member(int(row[1]))
                    if member:
                        embed.add_field(
                            name=f"{row[0]}. {member.display_name} ({member.id})",
                            value=f"Minecraft Username: {row[2]}",
                            inline=False,
                        )

                embeds.append(embed)
            else:
                embed = discord.Embed(
                    title="No Whitelisted Members",
                    description="There Are No Whitelisted Members.",
                    color=discord.Color.red(),
                )
                embeds = [embed]

            view = WhitelistView(embeds)
            await ctx.respond(embed=embeds[0], view=view)
        else:
            await ctx.respond(
                "You Don't Have Permission To Use This Command.", ephemeral=True
            )

    @commands.slash_command(name="whitelist", description="Get Whitelisted On Fallen SMP")
    async def whitelist(self, ctx: discord.ApplicationContext):
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
            embed.add_field(name="Server Version", value="1.21", inline=True)

            embed.set_image(
                url="https://media.discordapp.net/attachments/1258116175758364673/1266046626548678819/FALLEN_SMP.gif?ex=66a3b94d&is=66a267cd&hm=b80fdae6a297eeb179347003f57935b5edf601dfbb5433937e9cbb4a9f1493c5&=&width=1024&height=320"
            )

            await ctx.respond(
                embed=embed,
                view=WhitelistForm(
                    interaction_user=ctx.user, bot=self.bot, user=ctx.author
                ),
                ephemeral=True,
            )

        conn.close()


class WhitelistView(discord.ui.View):
    def __init__(self, embeds):
        super().__init__()
        self.embeds = embeds
        self.current_page = 0

    @discord.ui.button(label="◀", style=discord.ButtonStyle.primary)
    async def previous_page(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(
                embed=self.embeds[self.current_page], view=self
            )
        else:
            await interaction.response.send_message("No Previus Page", ephemeral=True)

    @discord.ui.button(label="▶", style=discord.ButtonStyle.primary)
    async def next_page(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        if self.current_page < len(self.embeds) - 1:
            self.current_page += 1
            await interaction.response.edit_message(
                embed=self.embeds[self.current_page], view=self
            )
        else:
            await interaction.response.send_message("No Next Page", ephemeral=True)


class WhitelistForm(discord.ui.View):
    def __init__(self, interaction_user: discord.User, bot: commands.Bot, user) -> None:
        super().__init__(timeout=None)
        self.interaction_user = interaction_user
        self.bot = bot

    @discord.ui.button(label="Java Whitelist", style=discord.ButtonStyle.secondary)
    async def java_button_callback(self, button, interaction):

        if interaction.user == self.interaction_user:
            await interaction.response.send_modal(
                WhitelistModal(
                    title="Fallen SMP Whitelist Form",
                    bot=self.bot,
                    user=self.interaction_user,
                    client="Java",
                )
            )

        self.disable_all_items()

    @discord.ui.button(label="Bedrock Whitelist", style=discord.ButtonStyle.secondary)
    async def bedrock_button_callback(self, button, interaction):

        if interaction.user == self.interaction_user:
            await interaction.response.send_modal(
                WhitelistModal(
                    title="Fallen SMP Whitelist Form",
                    bot=self.bot,
                    user=self.interaction_user,
                    client="Bedrock / PE",
                )
            )

        self.disable_all_items()


class WhitelistModal(discord.ui.Modal):
    def __init__(self, bot, user, client, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.user = user
        self.client = client

        self.whitelist_ids = Whitelist_ids
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

        qna = {
            "Role Earned by Killing Player Unwilling": "Outlaw",
            "Where Is PVP Allowed": "PVP Arena",
            "Can I Build Without Permission": "No",
            "Whom To Ask Permission From Before Building": ["Duke", "Admin"],
            "Who Has The Ultimate Authority": "Emperor",
        }

        conn = sqlite3.connect("User.db")

        try:
            agree_backstory = self.children[3].value.lower()
            roles_answer = self.children[4].value.lower()
            character_backstory = self.children[2].value

            if agree_backstory != "yes":
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

            correct_answer = self.qna[self.ques]

            if roles_answer not in correct_answer:
                embed = discord.Embed(
                    title="Whitelist Form Not Submitted",
                    description="### Answer Not Correct\nYou Must Answer Correctly To The Question",
                    color=discord.Color.red(),
                )

                await interaction.user.send(embed=embed)
                await interaction.response.send_message(
                    f"<@{interaction.user.id}>",
                    embed=embed,
                    ephemeral=True,
                )
                return

            elif len(character_backstory) > 3000:
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

            elif len(character_backstory) < 100:
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

            cursor = conn.cursor()

            data = cursor.execute(
                "SELECT * FROM user_data WHERE discord_user_id = ?",
                (str(interaction.user.id),),
            ).fetchone()

            if data:
                embed = discord.Embed(
                    title="Application Already Submitted",
                    description="If You Messed Up Your Application, Contact <@727012870683885578> Or <@664157606587138048>",
                    color=discord.Color.green(),
                )

                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            else:
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
                        self.children[0].value,
                        self.children[1].value,
                        character_backstory,
                    ),
                )

                cursor.execute(
                    "INSERT INTO stocks (user_id) VALUES (?)",
                    (str(interaction.user.id),),
                )
                conn.commit()

                print("Application Submitted")

                embed = discord.Embed(
                    title=f"Whitelist Application From {interaction.user.display_name}({interaction.user.id})",
                    description=f"**Client** : {self.client}\nUsername : {self.children[0].value}\nCharacter Gender : {self.children[1].value}\n\nCharacter Backstory : {character_backstory}\n\nAgree To Follow Backstory : {agree_backstory}\n{self.ques} : {roles_answer}",
                    color=discord.Color.blue(),
                )

                logs_channel = self.bot.get_channel(logs_channel_id)
                msg = await logs_channel.send(
                    f"<@727012870683885578> <@437622938242514945> <@243042987922292738> <@664157606587138048> <@896411007797325824> <@1147935418508132423> <@1261684685235294250>",
                    embed=embed,
                )

                self.whitelist_ids[interaction.user.id] = msg.id

                console_channel = self.bot.get_channel(console_channel_id)
                await console_channel.send(
                    f"msg rudropro Admins In The Game - New Whitelist Application Just Arrived"
                )

                success_embed = discord.Embed(
                    title="Application Submitted",
                    description="Your Application Has Been Submitted. Please Wait For Approval.",
                    color=discord.Color.green(),
                )

                await interaction.user.send(embed=success_embed)
                await interaction.response.send_message(
                    embed=success_embed, ephemeral=True
                )

        except Exception as e:
            error_message = f"An Error Occurred: {str(e)}\n{traceback.format_exc()}"
            error_channel = self.bot.get_channel(whitelist_channel_id)
            await error_channel.send(error_message)

        finally:
            conn.close()


def setup(bot):
    bot.add_cog(Whitelist(bot))
