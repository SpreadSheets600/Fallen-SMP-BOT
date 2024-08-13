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
        self.name = ""
        self.price = 0
        self.symbol = ""
        self.balance = 0
        self.user_id = 0
        self.quantity = 0
        self.buy_price = 0
        self.channel_id = 0
        self.track_message = 0

    def reset_purchase_details(self):
        self.name = ""
        self.price = 0
        self.symbol = ""
        self.balance = 0
        self.user_id = 0
        self.quantity = 0
        self.buy_price = 0
        self.channel_id = 0
        self.track_message = 0

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

        await ctx.defer(ephemeral=True)

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
            await ctx.respond(
                f"```{str(e)}```\n```{traceback.print_exc()}```\nYou Should probably Report This To <@727012870683885578>",
                ephemeral=True,
            )

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
        await ctx.defer(ephemeral=True)

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
            await ctx.respond(
                f"```{str(e)}```\n```{traceback.print_exc()}```\nYou Should probably Report This To <@727012870683885578>",
                ephemeral=True,
            )

    @stock.command(
        name="portfolio",
        description="Get User Portfolio",
    )
    async def portfolio(self, ctx):
        await ctx.defer(ephemeral=True)

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
                        f"{round(amd_pnl)}\n{round(apple_pnl)}\n{round(intel_pnl)}\n{round(google_pnl)}\n{round(microsoft_pnl)}"
                    ),
                    inline=True,
                )

                await ctx.respond(embed=stock_embed)
            else:
                await ctx.respond("No Portfolio Found", ephemeral=True)
        except Exception as e:
            await ctx.respond(
                f"```{str(e)}```\n```{traceback.print_exc()}```\nYou Should probably Report This To <@727012870683885578>",
                ephemeral=True,
            )
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
        await ctx.defer(ephemeral=True)

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
                        msg = await console_channel.send(
                            f"eco give {user} {total_price}"
                        )

                        await ctx.respond(
                            "Sell Successful, Confirmation On Its Way!", ephemeral=True
                        )

                        self.track_message = msg.id
                        self.name = ctx.author.display_name
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
            await ctx.respond(
                f"```{str(e)}```\n```{traceback.print_exc()}```\nYou Should probably Report This To <@727012870683885578>",
                ephemeral=True,
            )
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
        await ctx.defer(ephemeral=True)

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
                msg = await console_channel.send(f"eco take {user} {total_price}")

                await ctx.respond(
                    "Purchase Successful, Confirmation On Its Way!", ephemeral=True
                )

                self.track_message = msg.id
                self.name = ctx.author.display_name
                self.buy_price = price
                self.price = total_price
                self.quantity = quantity
                self.symbol = main_symbol
                self.user_id = ctx.author.id
                self.channel_id = ctx.channel.id

        except Exception as e:
            await ctx.respond(
                f"```{str(e)}```\n```{traceback.print_exc()}```\nYou Should probably Report This To <@727012870683885578>",
                ephemeral=True,
            )
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

        await ctx.defer(ephemeral=True)

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
            await ctx.respond(
                f"```{str(e)}```\n```{traceback.print_exc()}```\nYou Should probably Report This To <@727012870683885578>",
                ephemeral=True,
            )

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

        await ctx.defer(ephemeral=True)

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
            await ctx.respond(
                f"```{str(e)}```\n```{traceback.print_exc()}```\nYou Should probably Report This To <@727012870683885578>",
                ephemeral=True,
            )

    @crypto.command(
        name="portfolio",
        description="Get User Crypto Portfolio",
    )
    async def portfolio(self, ctx):

        await ctx.defer(ephemeral=True)

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
                    value=(
                        f"{round(eth_pnl)}\n{round(btc_pnl)}\n{round(bnb_pnl)}\n{round(sol_pnl)}\n{round(avax_pnl)}"
                    ),
                    inline=True,
                )

                await ctx.respond(embed=crypto_embed)
            else:
                await ctx.respond("No Portfolio Found", ephemeral=True)
        except Exception as e:
            await ctx.respond(
                f"```{str(e)}```\n```{traceback.print_exc()}```\nYou Should probably Report This To <@727012870683885578>",
                ephemeral=True,
            )
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

        await ctx.defer(ephemeral=True)

        try:
            quote = self.finnhub_client.quote(symbol=symbol)

            if quote:
                price = quote.get("c", 0)
                total_price = price * quantity

                symbol = symbol.split("-")[0]

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
                        msg = await console_channel.send(
                            f"eco give {user} {total_price}"
                        )

                        await ctx.respond(
                            "Sell Successful, Confirmation On Its Way!", ephemeral=True
                        )

                        self.track_message = msg.id
                        self.name = ctx.author.display_name
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
            await ctx.respond(
                f"```{str(e)}```\n```{traceback.print_exc()}```\nYou Should probably Report This To <@727012870683885578>",
                ephemeral=True,
            )
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

        await ctx.defer(ephemeral=True)

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
                msg = await console_channel.send(f"eco take {user} {total_price}")

                await ctx.respond(
                    "Purchase Successful, Confirmation On Its Way!", ephemeral=True
                )

                self.track_message = msg.id
                self.name = ctx.author.display_name
                self.symbol = symbol
                self.buy_price = price
                self.price = total_price
                self.quantity = quantity
                self.user_id = ctx.author.id
                self.channel_id = ctx.channel.id

        except Exception as e:
            await ctx.resond(
                f"```{str(e)}```\n```{traceback.print_exc()}```\nYou Should probably Report This To <@727012870683885578>",
                ephemeral=True,
            )
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

        await ctx.defer(ephemeral=True)

        try:
            news = self.fetch_news(symbol)

            if news:
                news_list = news
                view = NewsPagination(news_list)
                await ctx.respond(embed=view.children[0].embed, view=view)
        except Exception as e:
            await ctx.respond(
                f"```{str(e)}```\n```{traceback.print_exc()}```\nYou Should probably Report This To <@727012870683885578>",
                ephemeral=True,
            )

    balance = SlashCommandGroup(
        name="balance",
        description="Balance Commands Group",
    )

    @balance.command(
        name="view",
        description="Get User Balance",
    )
    async def balance_view(self, ctx):
        await ctx.defer(ephemeral=True)

        try:
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
                msg = await console_channel.send(f"balance {user}")

                await ctx.respond(
                    "Balance Fetch Successful, Transcript On Its Way!", ephemeral=True
                )

                self.track_message = msg.id
                self.channel_id = ctx.channel.id
                self.name = ctx.author.display_name

        except Exception as e:
            await ctx.respond(
                f"```{str(e)}```\n```{traceback.print_exc()}```\nYou Should probably Report This To <@727012870683885578>",
                ephemeral=True,
            )

    @commands.slash_command(
        name="top",
        description="Get Top Balances In The Server",
    )
    async def topbalance(self, ctx):
        await ctx.defer(ephemeral=True)

        try:
            cosole_channel = self.bot.get_channel(self.console_channel_id)
            msg = await cosole_channel.send("balancetop")

            await ctx.respond(
                "Top Balances Fetch Successful, Transcript On Its Way!", ephemeral=True
            )

            self.track_message = msg.id
            self.channel_id = ctx.channel.id

        except Exception as e:
            await ctx.respond(
                f"```{str(e)}```\n```{traceback.print_exc()}```\nYou Should probably Report This To <@727012870683885578>"
            )

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == 1270255175579471963:

            try:
                if message.reference.message_id == self.track_message:

                    if message.content.startswith("Ordering") or message.content.startswith("Top"):

                        embed = discord.Embed(
                            title="Server Top Balances",
                            description="Displaying Top Balances In The Server\nExcludes Balance From <@727012870683885578> ( SpreadSheets )",
                            color=discord.Color.green(),
                        )

                        broken = message.content.split("\n")

                        users = []
                        not_needed_bal = 0

                        server_total_raw = broken[3].split(" ")[-1].replace(",", "")[1:]
                        server_total = float(server_total_raw)

                        for i in range(4, len(broken) - 1):
                            user_line = broken[i]
                            user_data = user_line.split(" ")

                            if user_data[1] == "SpreadSheets,":
                                bal_idc = float(user_data[-1].replace(",", "")[1:])
                                not_needed_bal += bal_idc
                                continue

                            if user_data[1] == "[":
                                user_id = user_data[3].strip("~[]")
                                user_balance = float(user_data[-1].replace(",", "")[1:])
                            else:
                                user_id = user_data[1].strip("~[]")
                                user_balance = float(user_data[-1].replace(",", "")[1:])

                            users.append((user_id, user_balance))

                        server_total -= not_needed_bal

                        cursor = self.conn.cursor()
                        cursor.execute("SELECT * FROM user_data")
                        rows = cursor.fetchall()

                        for user_id, user_balance in users:
                            discord_user_id = None

                            for row in rows:
                                if row[3].lower() == user_id[0:len(user_id)-1].lower() or row[2].lower() == user_id[0:len(user_id)-1].lower():
                                    discord_user_id = row[1]

                            if discord_user_id is None:
                                embed.add_field(
                                    name=f"{user_id[0:len(user_id)-1]}",
                                    value=f"Balance: ${user_balance:,}",
                                    inline=False,
                                )
                            else:
                                embed.add_field(
                                    name=f"{user_id[0:len(user_id)-1]}",
                                    value=f"User: <@{discord_user_id}>\nBalance: ${user_balance:,}",
                                    inline=False,
                                )

                        embed.set_footer(text=f"Server Total: ${round(server_total):,}")

                        send_channel = self.bot.get_channel(self.channel_id)
                        await send_channel.send(embed=embed)

                    else:
                        broken = message.content.split(" ")

                        if len(broken) > 4:

                            if broken[1] in ["added", "taken"]:

                                try:
                                    cursor = self.conn.cursor()
                                    balance = broken[-1]

                                    if broken[1] == "taken":

                                        if self.symbol in [
                                            "ETH-USD",
                                            "BTC-USD",
                                            "BNB-USD",
                                            "SOL-USD",
                                            "AVAX-USD",
                                        ]:

                                            cursor.execute(
                                                f"""
                                                UPDATE stocks
                                                SET {self.symbol.split("-")[0]} = {self.symbol.split("-")[0]} + ?,
                                                    {self.symbol.split("-")[0]}_price = ?
                                                WHERE user_id = ?
                                                """,
                                                (
                                                    self.quantity,
                                                    self.buy_price,
                                                    self.user_id,
                                                ),
                                            )

                                            embed = discord.Embed(
                                                title=f"Crypto Purchased Report",
                                                description=f"Account: {self.name}\n\nCrypto Purchased: {self.quantity}\nTotal Price: {round(self.price)}\nBalance: {balance}",
                                                color=discord.Color.green(),
                                            )

                                        else:

                                            cursor.execute(
                                                f"""
                                                UPDATE stocks
                                                SET {self.symbol} = {self.symbol} + ?,
                                                    {self.symbol}_price = ?
                                                WHERE user_id = ?
                                                """,
                                                (
                                                    self.quantity,
                                                    self.buy_price,
                                                    self.user_id,
                                                ),
                                            )

                                            embed = discord.Embed(
                                                title=f"Stock Purchased Report",
                                                description=f"Account: {self.name}\n\nStocks Purchased : {self.quantity}\nTotal Price : {round(self.price)}\nBalance : {balance}",
                                                color=discord.Color.green(),
                                            )

                                    elif broken[1] == "added":
                                        cursor.execute(
                                            f"""
                                            UPDATE stocks
                                            SET {self.symbol} = {self.symbol} - ?,
                                                {self.symbol}_price = ?
                                            WHERE user_id = ?
                                            """,
                                            (self.quantity, 0, self.user_id),
                                        )

                                        embed = discord.Embed(
                                            title=f"Stock Sold Report",
                                            description=f"Account: {self.name}\n\nStocks Sold : {self.quantity}\nTotal Price: {round(self.price)}\nBalance Left : {balance}",
                                            color=discord.Color.red(),
                                        )

                                    self.conn.commit()
                                    send_channel = self.bot.get_channel(self.channel_id)
                                    await send_channel.send(embed=embed)
                                    self.reset_purchase_details()

                                except Exception as e:
                                    send_channel = self.bot.get_channel(self.channel_id)
                                    await send_channel.send(
                                        f"```{str(e)}```\n```{traceback.print_exc()}```\nYou Should probably Report This To <@727012870683885578>",
                                        ephemeral=True,
                                    )

                        if len(broken) > 3:

                            if broken[0] == "Balance":
                                self.balance = broken[-1]

                                if self.balance:
                                    embed = discord.Embed(
                                        title=f"Balance Transcript",
                                        description=f"### Account: {self.name}\n### Balance: {self.balance}",
                                        color=discord.Color.green(),
                                    )

                                    send_channel = self.bot.get_channel(self.channel_id)
                                    await send_channel.send(embed=embed)

                                else:

                                    embed = discord.Embed(
                                        title="Unable To Fetch Balance",
                                        description=f"### Please Try Again Later",
                                        color=discord.Color.green(),
                                    )

                                    self.reset_purchase_details()
                                    send_channel = self.bot.get_channel(self.channel_id)
                                    await send_channel.send(embed=embed)

            except Exception as e:
                pass


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
