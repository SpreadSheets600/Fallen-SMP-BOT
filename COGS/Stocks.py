import re
import time
import sqlite3
import discord
import finnhub
import asyncio
import datetime
import traceback
from discord import option
from discord.ext import commands
from discord.commands import SlashCommandGroup


class Stocks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect("User.db")
        self.finnhub_client = finnhub.Client(
            api_key="cqnpr21r01qo8864oasgcqnpr21r01qo8864oat0"
        )
        self.console_channel_id = 1263898954999922720
        self.price = 0
        self.symbol = ""
        self.balance = 0
        self.user_id = 0
        self.quantity = 0
        self.buy_price = 0
        self.channel_id = 0

    def reset_purchase_details(self):
        self.price = 0
        self.symbol = ""
        self.balance = 0
        self.user_id = 0
        self.quantity = 0
        self.buy_price = 0
        self.channel_id = 0

    def fetch_news(self, symbol):
        today = datetime.datetime.today()
        date = today.strftime("%Y-%m-%d")
        return self.finnhub_client.company_news(symbol, _from=date, to=date)

    stock = SlashCommandGroup(
        name="stock",
        description="Stocks Commands Group",
    )

    crypto = SlashCommandGroup(
        name="crypto",
        description="Crypto Commands Group",
    )

    @stock.command(
        name="quote",
        description="Get Quote of a Stock",
    )
    @option(
        "symbol",
        description="Stock Symbol",
        choices=["AMD", "APPLE", "INTEL", "MICROSOFT", "GOOGLE"],
    )
    async def quote(self, ctx, symbol: str):

        await ctx.defer()

        symbols = {
            "AMD": "AMD",
            "APPLE": "AAPL",
            "INTEL": "INTC",
            "MICROSOFT": "MSFT",
            "TCS": "TCS",
            "GOOGLE": "GOOGL",
        }

        main_symbol = symbols[symbol]

        try:
            quote = self.finnhub_client.quote(symbol=main_symbol)

            if quote:
                embed = discord.Embed(
                    title=f"{symbol.upper()} Stock Quote",
                    description=f"## Current Price: ${quote['c']}",
                    color=discord.Color.green(),
                )

                await ctx.respond(embed=embed)
        except Exception as e:
            await ctx.respond(str(e), ephemeral=True)

    @stock.command(
        name="company",
        description="Get Stock Company Information",
    )
    @option(
        "symbol",
        description="Stock Symbol",
        choices=["AMD", "APPLE", "INTEL", "MICROSOFT", "GOOGLE"],
    )
    async def company(self, ctx, symbol: str):
        await ctx.defer()

        symbols = {
            "AMD": "AMD",
            "APPLE": "AAPL",
            "INTEL": "INTC",
            "MICROSOFT": "MSFT",
            "TCS": "TCS",
            "GOOGLE": "GOOGL",
        }

        main_symbol = symbols[symbol]

        try:
            company = self.finnhub_client.company_profile2(symbol=main_symbol)

            if company:
                name = company.get("name", "N/A")
                ipo = company.get("ipo", "N/A")
                industry = company.get("finnhubIndustry", "N/A")
                market_cap = company.get("marketCapitalization", "N/A")
                country = company.get("country", "N/A")
                shares_outstanding = company.get("shareOutstanding", "N/A")
                logo = company.get("logo", "")
                weburl = company.get("weburl", "")

                embed = discord.Embed(
                    title=f"{symbol.upper()} Company Information",
                    description=(
                        f"### Name: {name}\n\n"
                        f"### IPO: {ipo}\n\n"
                        f"### Country: {country}\n"
                        f"### Industry: {industry}\n"
                        f"### Share Outstanding: {shares_outstanding}"
                        f"### Market Capitalization: {market_cap}\n"
                    ),
                    color=discord.Color.green(),
                )

                if logo:
                    embed.set_thumbnail(url=logo)
                if weburl:
                    embed.url = weburl

                await ctx.respond(embed=embed)
        except Exception as e:
            await ctx.respond(str(e), ephemeral=True)

    @stock.command(
        name="portfolio",
        description="Get User Portfolio",
    )
    async def portfolio(self, ctx):
        await ctx.defer()

        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                SELECT * FROM stocks WHERE user_id = ?
                """,
                (str(ctx.author.id),),
            )

            row = cursor.fetchone()

            if row:
                user = row[1]

                amd = row[2]
                amd_price = row[3]
                intel = row[4]
                intel_price = row[5]
                microsoft = row[6]
                microsoft_price = row[7]
                apple = row[8]
                apple_price = row[9]
                google = row[10]
                google_price = row[11]

                amd_current_price = self.finnhub_client.quote(symbol="AMD")["c"]
                intel_current_price = self.finnhub_client.quote(symbol="INTC")["c"]
                microsoft_current_price = self.finnhub_client.quote(symbol="MSFT")["c"]
                apple_current_price = self.finnhub_client.quote(symbol="AAPL")["c"]
                google_current_price = self.finnhub_client.quote(symbol="GOOGL")["c"]

                amd_pnl = 0 if amd_price == 0 else (amd_current_price - amd_price) * amd
                intel_pnl = (
                    0
                    if intel_price == 0
                    else (intel_current_price - intel_price) * intel
                )
                microsoft_pnl = (
                    0
                    if microsoft_price == 0
                    else (microsoft_current_price - microsoft_price) * microsoft
                )
                apple_pnl = (
                    0
                    if apple_price == 0
                    else (apple_current_price - apple_price) * apple
                )
                google_pnl = (
                    0
                    if google_price == 0
                    else (google_current_price - google_price) * google
                )

                display_name = ctx.author.display_name

                stock_embed = discord.Embed(
                    title=f"{display_name}'s Stock Portfolio",
                    color=discord.Color.green(),
                )
                stock_embed.add_field(
                    name="Stock",
                    value="AMD\nApple\nIntel\nGoogle\nMicrosoft",
                    inline=True,
                )
                stock_embed.add_field(
                    name="Amount",
                    value=f"{amd}\n{apple}\n{intel}\n{google}\n{microsoft}",
                    inline=True,
                )
                stock_embed.add_field(
                    name="PNL",
                    value=(
                        f"{amd_pnl}\n{apple_pnl}\n{intel_pnl}\n{google_pnl}\n{microsoft_pnl}"
                    ),
                    inline=True,
                )

                await ctx.respond(embed=stock_embed)
            else:
                await ctx.respond("No Portfolio Found", ephemeral=True)
        except Exception as e:
            await ctx.respond(str(e), ephemeral=True)
            traceback.print_exc()

    @stock.command(
        name="sell",
        description="Sell Stocks (Minecraft Economy)",
    )
    @option(
        "symbol",
        description="Stock Symbol",
        choices=["AMD", "APPLE", "INTEL", "MICROSOFT", "GOOGLE"],
    )
    @option(
        "quantity",
        description="Quantity Of Stocks",
        type=int,
    )
    async def sell(self, ctx, symbol: str, quantity: int):
        await ctx.defer()

        symbols = {
            "AMD": "AMD",
            "INTEL": "INTC",
            "APPLE": "AAPL",
            "GOOGLE": "GOOGL",
            "MICROSOFT": "MSFT",
        }

        main_symbol = symbols[symbol]

        try:
            quote = self.finnhub_client.quote(symbol=main_symbol)

            if quote:
                price = quote.get("c", 0)
                total_price = price * quantity

                cursor = self.conn.cursor()
                cursor.execute(
                    f"""
                    SELECT {main_symbol} FROM stocks WHERE user_id = ?
                    """,
                    (str(ctx.author.id),),
                )

                row = cursor.fetchone()

                if row:

                    stock = row[0]

                    cursor.execute(
                        """
                    SELECT * FROM user_data WHERE discord_user_id = ?
                    """,
                        (str(ctx.author.id),),
                    )

                    row = cursor.fetchone()

                    if row:
                        user = row[2]

                    if stock >= quantity:
                        console_channel = self.bot.get_channel(self.console_channel_id)
                        await console_channel.send(f"eco give {user} {total_price}")

                        await ctx.respond(
                            "Sell Successful, Confirmation On Its Way!", ephemeral=True
                        )

                        self.buy_price = price
                        self.price = total_price
                        self.quantity = quantity
                        self.symbol = main_symbol
                        self.user_id = ctx.author.id
                        self.channel_id = ctx.channel.id

                    else:
                        await ctx.respond(
                            "You Don't Have Enough Stocks To Sell", ephemeral=True
                        )

                else:
                    await ctx.respond(
                        "You Don't Have Enough Stocks To Sell", ephemeral=True
                    )

        except Exception as e:
            await ctx.respond(str(e), ephemeral=True)
            traceback.print_exc()

    @stock.command(
        name="buy",
        description="Buy Stocks (Minecraft Economy)",
    )
    @option(
        "symbol",
        description="Stock Symbol",
        choices=["AMD", "APPLE", "INTEL", "MICROSOFT", "GOOGLE"],
    )
    @option(
        "quantity",
        description="Quantity Of Stocks",
        type=int,
    )
    async def buy(self, ctx, symbol: str, quantity: int):
        await ctx.defer()

        symbols = {
            "AMD": "AMD",
            "APPLE": "AAPL",
            "INTEL": "INTC",
            "MICROSOFT": "MSFT",
            "TCS": "TCS",
            "GOOGLE": "GOOGL",
        }

        main_symbol = symbols[symbol]

        try:
            quote = self.finnhub_client.quote(symbol=main_symbol)

            if quote:
                price = quote.get("c", 0)
                total_price = price * quantity

                cursor = self.conn.cursor()
                cursor.execute(
                    """
                    SELECT * FROM user_data WHERE discord_user_id = ?
                    """,
                    (str(ctx.author.id),),
                )

                row = cursor.fetchone()

                if row:
                    user = row[2]

                console_channel = self.bot.get_channel(self.console_channel_id)
                await console_channel.send(f"eco take {user} {total_price}")

                await ctx.respond(
                    "Purchase Successful, Confirmation On Its Way!", ephemeral=True
                )

                self.buy_price = price
                self.price = total_price
                self.quantity = quantity
                self.symbol = main_symbol
                self.user_id = ctx.author.id
                self.channel_id = ctx.channel.id

        except Exception as e:
            await ctx.respond(str(e), ephemeral=True)
            traceback.print_exc()

    @stock.command(
        name="news",
        description="Get News Of A Particular Stock",
    )
    @option(
        "symbol",
        description="Stock Symbol",
        choices=["AMD", "APPLE", "INTEL", "MICROSOFT", "GOOGLE"],
    )
    async def news(self, ctx, symbol: str):

        await ctx.defer()

        symbols = {
            "AMD": "AMD",
            "APPLE": "AAPL",
            "INTEL": "INTC",
            "MICROSOFT": "MSFT",
            "TCS": "TCS",
            "GOOGLE": "GOOGL",
        }

        symbol = symbols[symbol]

        try:
            news = self.fetch_news(symbol)

            if news:
                news_list = news
                view = NewsPagination(news_list)
                await ctx.respond(embed=view.children[0].embed, view=view)
        except Exception as e:
            await ctx.respond(str(e), ephemeral=True)

    @crypto.command(
        name="quote",
        description="Get Quote Of A Crypto",
    )
    @option(
        "symbol",
        description="Crypto Symbol",
        choices=["ETH-USD", "BTC-USD", "BNB-USD", "SOL-USD", "AVAX-USD"],
    )
    async def quote(self, ctx, symbol: str):

        await ctx.defer()

        try:
            quote = self.finnhub_client.quote(symbol=symbol)

            if quote:
                embed = discord.Embed(
                    title=f"{symbol.upper()} Crypto Quote",
                    description=f"## Current Price : ${quote['c']}",
                    color=discord.Color.green(),
                )

                await ctx.respond(embed=embed)
        except Exception as e:
            await ctx.respond(str(e), ephemeral=True)

    @crypto.command(
        name="portfolio",
        description="Get User Crypto Portfolio",
    )
    async def portfolio(self, ctx):

        await ctx.defer()

        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                SELECT * FROM stocks WHERE user_id = ?
                """,
                (str(ctx.author.id),),
            )

            row = cursor.fetchone()

            if row:
                user = row[1]

                eth = row[12]
                eth_price = row[13]
                btc = row[14]
                btc_price = row[15]
                bnb = row[16]
                bnb_price = row[17]
                avax = row[18]
                avax_price = row[19]
                sol = row[20]
                sol_price = row[21]

                eth_current_price = self.finnhub_client.quote(symbol="ETH-USD")["c"]
                btc_current_price = self.finnhub_client.quote(symbol="BTC-USD")["c"]
                bnb_current_price = self.finnhub_client.quote(symbol="BNB-USD")["c"]
                avax_current_price = self.finnhub_client.quote(symbol="AVAX-USD")["c"]
                sol_current_price = self.finnhub_client.quote(symbol="SOL-USD")["c"]

                eth_pnl = 0 if eth_price == 0 else (eth_current_price - eth_price) * eth
                btc_pnl = 0 if btc_price == 0 else (btc_current_price - btc_price) * btc
                bnb_pnl = 0 if bnb_price == 0 else (bnb_current_price - bnb_price) * bnb
                avax_pnl = (
                    0 if avax_price == 0 else (avax_current_price - avax_price) * avax
                )
                sol_pnl = 0 if sol_price == 0 else (sol_current_price - sol_price) * sol

                display_name = ctx.author.display_name

                crypto_embed = discord.Embed(
                    title=f"{display_name}'s Crypto Portfolio",
                    color=discord.Color.green(),
                )
                crypto_embed.add_field(
                    name="Crypto",
                    value="ETH\nBTC\nBNB\nSOL\nAVAX",
                    inline=True,
                )
                crypto_embed.add_field(
                    name="Amount",
                    value=f"{eth}\n{btc}\n{bnb}\n{sol}\n{avax}",
                    inline=True,
                )
                crypto_embed.add_field(
                    name="PNL",
                    value=(f"{eth_pnl}\n{btc_pnl}\n{bnb_pnl}\n{sol_pnl}\n{avax_pnl}"),
                    inline=True,
                )

                await ctx.respond(embeds=crypto_embed)
            else:
                await ctx.respond("No Portfolio Found", ephemeral=True)
        except Exception as e:
            await ctx.respond(str(e), ephemeral=True)
            traceback.print_exc()

    @crypto.command(
        name="sell",
        description="Sell Crypto (Minecraft Economy)",
    )
    @option(
        "symbol",
        description="Crypto Symbol",
        choices=["ETH-USD", "BTC-USD", "BNB-USD", "SOL-USD", "AVAX-USD"],
    )
    @option(
        "quantity",
        description="Quantity Of Crypto",
        type=int,
    )
    async def sell(self, ctx, symbol: str, quantity: int):

        await ctx.defer()

        try:
            quote = self.finnhub_client.quote(symbol=symbol)

            if quote:
                price = quote.get("c", 0)
                total_price = price * quantity

                cursor = self.conn.cursor()
                cursor.execute(
                    f"""
                    SELECT {symbol} FROM stocks WHERE user_id = ?
                    """,
                    (str(ctx.author.id),),
                )

                row = cursor.fetchone()

                if row:

                    crypto = row[0]

                    cursor.execute(
                        """
                    SELECT * FROM user_data WHERE discord_user_id = ?
                    """,
                        (str(ctx.author.id),),
                    )

                    row = cursor.fetchone()

                    if row:
                        user = row[2]

                    if crypto >= quantity:
                        console_channel = self.bot.get_channel(self.console_channel_id)
                        await console_channel.send(f"eco give {user} {total_price}")

                        await ctx.respond(
                            "Sell Successful, Confirmation On Its Way!", ephemeral=True
                        )

                        self.symbol = symbol
                        self.buy_price = price
                        self.price = total_price
                        self.quantity = quantity
                        self.user_id = ctx.author.id
                        self.channel_id = ctx.channel.id

                    else:
                        await ctx.respond(
                            "You Don't Have Enough Crypto To Sell", ephemeral=True
                        )

                else:
                    await ctx.respond(
                        "You Don't Have Enough Crypto To Sell", ephemeral=True
                    )

        except Exception as e:
            await ctx.respond(str(e), ephemeral=True)
            traceback.print_exc()

    @crypto.command(
        name="buy",
        description="Buy Crypto (Minecraft Economy)",
    )
    @option(
        "symbol",
        description="Crypto Symbol",
        choices=["ETH-USD", "BTC-USD", "BNB-USD", "SOL-USD", "AVAX-USD"],
    )
    @option(
        "quantity",
        description="Quantity Of Crypto",
        type=int,
    )
    async def buy(self, ctx, symbol: str, quantity: int):

        await ctx.defer()

        try:
            quote = self.finnhub_client.quote(symbol=symbol)

            if quote:
                price = quote.get("c", 0)
                total_price = price * quantity

                cursor = self.conn.cursor()
                cursor.execute(
                    """
                    SELECT * FROM user_data WHERE discord_user_id = ?
                    """,
                    (str(ctx.author.id),),
                )

                row = cursor.fetchone()

                if row:
                    user = row[2]

                console_channel = self.bot.get_channel(self.console_channel_id)
                await console_channel.send(f"eco take {user} {total_price}")

                await ctx.respond(
                    "Purchase Successful, Confirmation On Its Way!", ephemeral=True
                )

                self.symbol = symbol
                self.buy_price = price
                self.price = total_price
                self.quantity = quantity
                self.user_id = ctx.author.id
                self.channel_id = ctx.channel.id

        except Exception as e:
            await ctx.respond(str(e), ephemeral=True)
            traceback.print_exc()

    @crypto.command(
        name="news",
        description="Get News Of A Particular Crypto",
    )
    @option(
        "symbol",
        description="Crypto Symbol",
        choices=["ETH-USD", "BTC-USD", "BNB-USD", "SOL-USD", "AVAX-USD"],
    )
    async def news(self, ctx, symbol: str):

        await ctx.defer()

        try:
            news = self.fetch_news(symbol)

            if news:
                news_list = news
                view = NewsPagination(news_list)
                await ctx.respond(embed=view.children[0].embed, view=view)
        except Exception as e:
            await ctx.respond(str(e), ephemeral=True)

    async def balance_check(self, user_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                SELECT * FROM user_data WHERE discord_user_id = ?
                """,
                (str(user_id),),
            )

            row = cursor.fetchone()

            if row:
                user = row[2]

                console_channel = self.bot.get_channel(self.console_channel_id)
                await console_channel.send(f"balance {user}")

        except Exception as e:
            print(e)
            traceback.print_exc()

    @commands.slash_command(
        name="balance",
        description="Get User Balance",
    )
    async def balance(self, ctx):
        await ctx.defer()

        await self.balance_check(ctx.author.id)
        await asyncio.sleep(3)

        if self.balance:
            embed = discord.Embed(
                title="User Balance",
                description=f"## Balance : {self.balance}",
                color=discord.Color.green(),
            )
            await ctx.respond(embed=embed)
        else:
            await ctx.respond("Unable To Retrieve Balance\nPlease Try Again Later", ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == 1268581485871501354:
            broken = message.content.split(" ")

            if len(broken) > 6:

                if broken[4] in ["added", "taken"]:
                    try:
                        cursor = self.conn.cursor()
                        balance = broken[-1]

                        if broken[4] == "taken":
                            cursor.execute(
                                f"""
                                UPDATE stocks
                                SET {self.symbol} = {self.symbol} + ?,
                                    {self.symbol}_price = ?
                                WHERE user_id = ?
                                """,
                                (self.quantity, self.buy_price, self.user_id),
                            )

                            embed = discord.Embed(
                                title="Stock Purchase Confirmation",
                                description=f"Stocks Purchased: {self.quantity}\nTotal Price: {self.price}\nBalance: {balance}",
                                color=discord.Color.green(),
                            )

                        elif broken[4] == "added":
                            cursor.execute(
                                f"""
                                UPDATE stocks
                                SET {self.symbol} = {self.symbol} - ?,
                                    {self.symbol}_price = ?
                                WHERE user_id = ?
                                """,
                                (self.quantity, self.buy_price, self.user_id),
                            )

                            embed = discord.Embed(
                                title="Stock Sell Confirmation",
                                description=f"Stocks Sold: {self.quantity}\nTotal Price: {self.price}\nBalance: {balance}",
                                color=discord.Color.red(),
                            )

                        self.conn.commit()
                        send_channel = self.bot.get_channel(self.channel_id)
                        await send_channel.send(embed=embed)
                        self.reset_purchase_details()

                    except Exception as e:
                        pass

            if broken[3] == "Balance":
                self.balance = broken[-1]

class NewsPagination(discord.ui.View):
    def __init__(self, news_list):
        super().__init__(timeout=60)
        self.news_list = news_list
        self.index = 0
        self.update_button_states()
        self.children[0].embed = self.create_embed()

    def create_embed(self):
        news = self.news_list[self.index]
        embed = discord.Embed(
            title=news["headline"],
            description=news["summary"],
            url=news["url"],
            color=0x2F3136,
        )
        if "image" in news:
            embed.set_image(url=news["image"])
        embed.set_footer(text=f"Source: {news['source']}")
        return embed

    async def update_message(self, interaction):
        self.update_button_states()
        embed = self.create_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    def update_button_states(self):
        self.previous_button.disabled = self.index == 0
        self.next_button.disabled = self.index >= len(self.news_list) - 1

    @discord.ui.button(label="◀", style=discord.ButtonStyle.primary, disabled=False)
    async def previous_button(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        if self.index > 0:
            self.index -= 1
            await self.update_message(interaction)

    @discord.ui.button(label="▶", style=discord.ButtonStyle.primary, disabled=False)
    async def next_button(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        if self.index < len(self.news_list) - 1:
            self.index += 1
            await self.update_message(interaction)


def setup(bot):
    bot.add_cog(Stocks(bot))
