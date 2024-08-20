import discord
from discord.ext import commands


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="help", description="Sends Help Embed")
    async def help(self, ctx):
        embed = discord.Embed(
            title="Help", description="List of Commands", color=0x2F3136
        )

        rules = self.bot.get_command("rules")
        guide = self.bot.get_command("guide")
        status = self.bot.get_command("status")
        player = self.bot.get_command("playerinfo")
        ping = self.bot.get_command("ping")
        info = self.bot.get_command("info")

        embed.add_field(name="Info", value=info.mention, inline=True)
        embed.add_field(name="Ping", value=ping.mention, inline=True)
        embed.add_field(name="Rules", value=rules.mention, inline=True)
        embed.add_field(name="Guide", value=guide.mention, inline=True)
        embed.add_field(name="Status", value=status.mention, inline=True)
        embed.add_field(name="Player Info", value=player.mention, inline=True)

        await ctx.respond(embed=embed, view=CEmbed(self.bot))


class CEmbed(discord.ui.View):

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @discord.ui.select(
        placeholder="Choose A Help Category",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(label="Stocks", description="Stock Commands"),
            discord.SelectOption(label="Crypto", description="Crypto Commands"),
            discord.SelectOption(label="Whitelist", description="Whitelist Commands"),
        ],
    )
    async def callback(self, select, interaction):
        if select.values[0] == "Stocks":
            stock_embed = discord.Embed(
                title="Stocks", description="Stock Commands", color=0x2F3136
            )

            stock_quote = (
                self.bot.get_application_command("stock").subcommands[0].mention
            )

            stock_company = (
                self.bot.get_application_command("stock").subcommands[1].mention
            )

            stock_portfolio = (
                self.bot.get_application_command("stock").subcommands[2].mention
            )

            stock_sell = (
                self.bot.get_application_command("stock").subcommands[3].mention
            )

            stock_buy = self.bot.get_application_command("stock").subcommands[4].mention

            stock_news = (
                self.bot.get_application_command("stock").subcommands[5].mention
            )

            stock_embed.add_field(name="Buy", value=stock_buy, inline=False)
            stock_embed.add_field(name="Sell", value=stock_sell, inline=False)
            stock_embed.add_field(name="News", value=stock_news, inline=False)
            stock_embed.add_field(name="Quote", value=stock_quote, inline=False)
            stock_embed.add_field(name="Company", value=stock_company, inline=False)
            stock_embed.add_field(name="Portfolio", value=stock_portfolio, inline=False)

            await interaction.response.send_message(embed=stock_embed, ephemeral=True)

        elif select.values[0] == "Crypto":
            crypto_embed = discord.Embed(
                title="Crypto", description="Crypto Commands", color=0x2F3136
            )

            crypto_quote = (
                self.bot.get_application_command("crypto").subcommands[0].mention
            )

            crypto_portfolio = (
                self.bot.get_application_command("crypto").subcommands[1].mention
            )

            crypto_sell = (
                self.bot.get_application_command("crypto").subcommands[2].mention
            )

            crypto_buy = (
                self.bot.get_application_command("crypto").subcommands[3].mention
            )

            crypto_news = (
                self.bot.get_application_command("crypto").subcommands[4].mention
            )

            crypto_embed.add_field(name="Buy", value=crypto_buy, inline=False)
            crypto_embed.add_field(name="Sell", value=crypto_sell, inline=False)
            crypto_embed.add_field(name="News", value=crypto_news, inline=False)
            crypto_embed.add_field(name="Quote", value=crypto_quote, inline=False)
            crypto_embed.add_field(
                name="Portfolio", value=crypto_portfolio, inline=False
            )

            await interaction.response.send_message(embed=crypto_embed, ephemeral=True)

        elif select.values[0] == "Whitelist":
            wh_embed = discord.Embed(
                title="Whitelist", description="Whitelist Commands", color=0x2F3136
            )

            wh_delete = (
                self.bot.get_application_command("wl").subcommands[0].mention
            )

            wh_add = (
                self.bot.get_application_command("wl").subcommands[1].mention
            )

            wh_list = (
                self.bot.get_application_command("wl").subcommands[2].mention
            )

            wh_form = (
                self.bot.get_application_command("whitelist")
            )

            wh_embed.add_field(name="Add", value=wh_add, inline=False)
            wh_embed.add_field(name="List", value=wh_list, inline=False)
            wh_embed.add_field(name="Delete", value=wh_delete, inline=False)

            await interaction.response.send_message(embed=wh_embed, ephemeral=True)


def setup(bot):
    bot.add_cog(Help(bot))
