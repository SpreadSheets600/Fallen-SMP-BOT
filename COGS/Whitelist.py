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

whitelist_channel_id = 1267512076222595122
console_channel_id = 1263898954999922720
logs_channel_id = 1267512076222595122


class Whitelist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    whitelist = SlashCommandGroup(name="whitelist", description="Whitelist Commands")

    @whitelist.command(name="delete", description="Delete User's Whitelist Application")
    async def del_whitelist(
        self, ctx: discord.ApplicationContext, member: discord.Member
    ):
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
                cursor.execute(
                    "DELETE FROM stocks WHERE user_id = ?", (str(member.id),)
                )
                conn.commit()

                embed = discord.Embed(
                    title="Whitelist Application Deleted",
                    description=f"Whitelist Application For **{member.display_name}** Has Been Deleted.",
                    color=discord.Color.green(),
                )
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
                "You don't have permission to use this command.", ephemeral=True
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
        if ctx.author.id in ADMINS:
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
            await ctx.respond(
                "You don't have permission to use this command.", ephemeral=True
            )

    @whitelist.command(name="view", description="Show All Whitelisted Members")
    async def show_whitelist(self, ctx: discord.ApplicationContext):
        if ctx.author.id in ADMINS:
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
                "You don't have permission to use this command.", ephemeral=True
            )

    @whitelist.command(name="form", description="Get Whitelisted On Fallen SMP")
    async def form(self, ctx: discord.ApplicationContext):
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
                view=WhitelistForm(interaction_user=ctx.user, bot=self.bot, user=ctx.author),
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

    @discord.ui.button(label="Whitelist Form")
    async def button_callback(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ) -> None:
        if interaction.user != self.interaction_user:
            await interaction.response.send_message(
                "You don't have permission to use this button.", ephemeral=True
            )
            return

        await interaction.response.send_modal(
            WhitelistModal(title="Fallen SMP Whitelist Form", bot=self.bot, user=self.interaction_user)
        )


class WhitelistModal(discord.ui.Modal):
    def __init__(self, bot, user, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.user = user

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
                style=discord.InputTextStyle.multiline,
            )
        )

    async def callback(self, interaction: discord.Interaction):

        conn = sqlite3.connect("User.db")

        try:
            if len(self.children[3].value) > 3000:

                user = self.bot.get_user(interaction.user.id)
                embed = discord.Embed(
                    title="Whitelist Form Not Sumbitted",
                    description="### Character Backstory Too Long\nCharacter Backstory Should Be Below 3000 Characters",
                    color=discord.Color.red(),
                )

                await user.send(embed=embed)

                await interaction.response.send_message(
                    f"<@{interaction.user.id}",
                    embed=embed,
                    ephemeral=True,
                )
                return

            if len(self.children[3].value) < 100:

                user = self.bot.get_user(interaction.user.id)
                embed = discord.Embed(
                    title="Whitelist Form Not Sumbitted",
                    description="### Character Backstory Too Short\nCharacter Backstory Should Be Above 100 Characters",
                    color=discord.Color.red(),
                )

                await user.send(embed=embed)

                await interaction.response.send_message(
                    f"<@{interaction.user.id}",
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
                        self.children[1].value,
                        self.children[2].value,
                        self.children[3].value,
                    ),
                )

                cursor.execute(
                    "INSERT INTO stocks (user_id) VALUES (?)",
                    (str(interaction.user.id),),
                )
                conn.commit()

                print("Application Submitted")

                embed = discord.Embed(
                    title=f"Whitelist Application From {interaction.user.display_name}",
                    description=f"Username : {self.children[0].value}\nCharacter Name : {self.children[1].value}\nCharacter Gender : {self.children[2].value}\n\nCharacter Backstory : {self.children[3].value}",
                    color=discord.Color.blue(),
                )

                logs_channel = self.bot.get_channel(logs_channel_id)
                await logs_channel.send(f"<@727012870683885578> <@437622938242514945> <@243042987922292738> <@664157606587138048> <@896411007797325824>",embed=embed)

                success_embed = discord.Embed(
                    title="Application Submitted",
                    description="Your Application Has Been Submitted. Please Wait For Approval.",
                    color=discord.Color.green(),
                )

                await interaction.response.send_message(
                    embed=success_embed, ephemeral=True
                )

        except Exception as e:
            error_message = f"An error occurred: {str(e)}\n{traceback.format_exc()}"
            error_channel = self.bot.get_channel(whitelist_channel_id)
            await error_channel.send(error_message)

        finally:
            conn.close()


def setup(bot):
    bot.add_cog(Whitelist(bot))
