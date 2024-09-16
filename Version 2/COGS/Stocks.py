import os
import json
import random
import pymongo
import discord
import asyncio
import finnhub
import datetime
from discord import *
from pymongo import MongoClient
from discord.ext.pages import *
from discord.ext.bridge import *
from discord.commands import SlashCommandGroup
from discord.ext.bridge import BridgeSlashGroup
from discord.ext import commands, bridge, pages

# =================================================================================================== #

from dotenv import *

load_dotenv()

# =================================================================================================== #

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
    1261684685235294250,
    1147935418508132423,
]

CONSOLE_CHANNEL = 1263898954999922720
ERROR_CHANNEL = 1275759089024241797

# =================================================================================================== #


class Stocks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.mongo_client = MongoClient(os.getenv("MONGO_URI"))

        self.db = self.mongo_client["Users"]
        self.collection = self.db["UserStocks"]

        self.finnhub_client = finnhub.Client(api_key=os.getenv("FINNHUB_API_KEY"))
        self.track_message = 0

    def fetch_news(self, symbol):
        today = datetime.datetime.today()
        date = today.strftime("%Y-%m-%d")
        return self.finnhub_client.company_news(symbol, _from=date, to=date)

    stock = SlashCommandGroup(name="stock", description="Stock Commands")

    @stock.command(
        name="quote",
        description="Get The Current Price Of A Stock",
    )
    @option(
        "symbol",
        description="The Stock Symbol",
        choices=["AMD", "APPLE", "INTEL", "GOOGLE", "MICROSOFT"],
    )
    async def quote(self, ctx, symbol):

        await ctx.defer(ephemeral=True)

        valid_symbols = ["AMD", "APPLE", "INTEL", "GOOGLE", "MICROSOFT"]

        if symbol not in valid_symbols:
            embed = discord.Embed(
                title="Invalid Symbol",
                description="Please Enter A Valid Symbol",
                color=0xFF0000,
            )

            embed.add_field(
                name="Valid Symbols",
                value="AMD, APPLE, INTEL, GOOGLE, MICROSOFT",
                inline=True,
            )

            await ctx.respond(embed=embed, ephemeral=True)
            return

        symbols = {
            "AMD": "AMD",
            "APPLE": "AAPL",
            "INTEL": "INTC",
            "GOOGLE": "GOOGL",
            "MICROSOFT": "MSFT",
        }

        try:
            main_symbol = symbols[symbol]
        except Exception as e:
            main_symbol = symbol.upper()

        try:
            quote = self.finnhub_client.quote(symbol=main_symbol)

            if quote:
                embed = discord.Embed(
                    title=f"{symbol} Stock Quote",
                    description=f"### Current Price: ${quote['c']}",
                    color=0xD5E4CF,
                )

                await ctx.respond(embed=embed, ephemeral=True)

        except Exception as e:
            print(f"[ - ] Stocks COG : Error : {e}")
            await ctx.respond(
                f"[ - ] Stocks COG : Error : \n```{e}```",
                ephemeral=True,
                delete_after=5,
            )
            ErrorChannel = self.bot.get_channel(ERROR_CHANNEL)
            await ErrorChannel.send(f"[ - ] Stocks COG : Error : \n```{e}```")

    @stock.command(
        name="company",
        description="Get Company Information",
    )
    @option(
        "symbol",
        description="The Stock Symbol",
        choices=["AMD", "APPLE", "INTEL", "GOOGLE", "MICROSOFT"],
    )
    async def company(self, ctx, symbol):

        await ctx.defer(ephemeral=True)

        valid_symbols = ["AMD", "APPLE", "INTEL", "GOOGLE", "MICROSOFT"]

        if symbol not in valid_symbols:
            embed = discord.Embed(
                title="Invalid Symbol",
                description="Please Enter A Valid Symbol",
                color=0xFF0000,
            )

            embed.add_field(
                name="Valid Symbols",
                value="AMD, APPLE, INTEL, GOOGLE, MICROSOFT",
                inline=True,
            )

            await ctx.respond(embed=embed, ephemeral=True)
            return

        symbols = {
            "AMD": "AMD",
            "APPLE": "AAPL",
            "INTEL": "INTC",
            "GOOGLE": "GOOGL",
            "MICROSOFT": "MSFT",
        }

        try:
            main_symbol = symbols[symbol]
        except Exception as e:
            main_symbol = symbol.upper()

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

                await ctx.respond(embed=embed, ephemeral=True)

        except Exception as e:
            print(f"[ - ] Stocks COG : Error : {e}")
            await ctx.respond(
                f"[ - ] Stocks COG : Error : \n```{e}```",
                ephemeral=True,
                delete_after=5,
            )
            ErrorChannel = self.bot.get_channel(ERROR_CHANNEL)
            await ErrorChannel.send(f"[ - ] Stocks COG : Error : \n```{e}```")

    @stock.command(
        name="portfolio",
        description="Get User Portfolio",
    )
    async def portfolio(self, ctx, user: discord.Member=None):
        await ctx.defer(ephemeral=True)

        if user is None or ctx.author.id not in ADMINS:
            user = ctx.author


        try:
            document = self.collection.find_one({"ID": user.id})

            amd_current_price = self.finnhub_client.quote(symbol="AMD")["c"]
            apple_current_price = self.finnhub_client.quote(symbol="AAPL")["c"]
            intel_current_price = self.finnhub_client.quote(symbol="INTC")["c"]
            google_current_price = self.finnhub_client.quote(symbol="GOOGL")["c"]
            microsoft_current_price = self.finnhub_client.quote(symbol="MSFT")["c"]

            current_prices = {
                "AMD": amd_current_price,
                "AAPL": apple_current_price,
                "INTC": intel_current_price,
                "GOOGL": google_current_price,
                "MSFT": microsoft_current_price,
            }

            if document:
                timestamp = datetime.datetime.now().isoformat()
                stocks_amount = document["StocksAmount"]
                stocks_buy_price = document["StocksBuyPrice"]

                for keys in stocks_amount.keys():
                    if stocks_buy_price[f"{keys}_P"] == 0:
                        stocks_buy_price[f"{keys}_P"] = current_prices[keys]

                pnl = {
                    "AMD": current_prices["AMD"] - stocks_buy_price["AMD_P"],
                    "AAPL": current_prices["AAPL"] - stocks_buy_price["AAPL_P"],
                    "INTC": current_prices["INTC"] - stocks_buy_price["INTC_P"],
                    "GOOGL": current_prices["GOOGL"] - stocks_buy_price["GOOGL_P"],
                    "MSFT": current_prices["MSFT"] - stocks_buy_price["MSFT_P"],
                }

                parsed_timestamp = datetime.datetime.fromisoformat(timestamp)
                unix_timestamp = int(parsed_timestamp.timestamp())
                discord_timestamp = f"<t:{unix_timestamp}>"

                embed = discord.Embed(
                    title=f"{user.display_name} 's Portfolio",
                    description=f"Last Updated : {discord_timestamp}",
                    color=0xD5E4CF,
                )

                embed.add_field(
                    name="Stock",
                    value="AMD\nApple\nIntel\nGoogle\nMicrosoft",
                    inline=True,
                )
                embed.add_field(
                    name="Amount",
                    value=(
                        f"{stocks_amount['AMD']}\n"
                        f"{stocks_amount['AAPL']}\n"
                        f"{stocks_amount['INTC']}\n"
                        f"{stocks_amount['GOOGL']}\n"
                        f"{stocks_amount['MSFT']}"
                    ),
                    inline=True,
                )
                embed.add_field(
                    name="PNL",
                    value=(
                        f"$ {round(pnl['AMD'], 2)}\n"
                        f"$ {round(pnl['AAPL'], 2)}\n"
                        f"$ {round(pnl['INTC'], 2)}\n"
                        f"$ {round(pnl['GOOGL'], 2)}\n"
                        f"$ {round(pnl['MSFT'], 2)}"
                    ),
                    inline=True,
                )

                await ctx.respond(embed=embed, ephemeral=True)

            else:
                embed = discord.Embed(
                    title=f"{ctx.author.display_name}'s Portfolio",
                    description="You Don't Have Any Stocks",
                    color=0xD5E4CF,
                )

                await ctx.respond(embed=embed, ephemeral=True)

        except Exception as e:
            print(f"[ - ] Stocks COG : Error : {e}")
            await ctx.respond(
                f"[ - ] Stocks COG : Error : \n```{e}```",
                ephemeral=True,
                delete_after=5,
            )
            ErrorChannel = self.bot.get_channel(ERROR_CHANNEL)
            await ErrorChannel.send(f"[ - ] Stocks COG : Error : \n```{e}```")

    @stock.command(
        name="buy",
        description="Buy Stocks (Minecraft Economy)",
    )
    @option(
        "symbol",
        description="The Stock Symbol",
        choices=["AMD", "APPLE", "INTEL", "GOOGLE", "MICROSOFT"],
    )
    @option("quantity", description="The Quantity Of Stocks To Buy", type=int)
    async def buy(self, ctx, symbol: str, quantity: int):
        await ctx.defer(ephemeral=True)

        if symbol not in ["AMD", "APPLE", "INTEL", "GOOGLE", "MICROSOFT"]:
            embed = discord.Embed(
                title="Invalid Symbol",
                description="Please Enter A Valid Symbol",
                color=0xFF0000,
            )

            embed.add_field(
                name="Valid Symbols",
                value="AMD, APPLE, INTEL, GOOGLE, MICROSOFT",
                inline=True,
            )

            await ctx.respond(embed=embed, ephemeral=True)
            return

        symbols = {
            "AMD": "AMD",
            "APPLE": "AAPL",
            "INTEL": "INTC",
            "GOOGLE": "GOOGL",
            "MICROSOFT": "MSFT",
        }

        main_symbol = symbols.get(symbol, symbol.upper())

        try:
            quote = self.finnhub_client.quote(symbol=main_symbol)

            if not quote:
                embed = discord.Embed(
                    title="Stock Data Unavailable",
                    description="Could not retrieve stock information. Please try again later.",
                    color=0xFF0000,
                )
                return await ctx.respond(embed=embed, ephemeral=True)

            price = quote.get("c", 0)
            total_price = price * quantity

            document = self.collection.find_one({"ID": ctx.author.id})
            if not document:
                game_username = "default_username"
                user_data = {
                    "ID": ctx.author.id,
                    "Username": game_username,
                    "StocksAmount": {symbol: 0 for symbol in symbols.values()},
                    "StocksBuyPrice": {f"{symbol}_P": 0 for symbol in symbols.values()},
                    "Timestamp": "2024-08-22T12:00:00Z",
                }
            else:
                user_data = document

            current_amount = user_data["StocksAmount"].get(main_symbol, 0)
            user_data["StocksAmount"][main_symbol] = current_amount + quantity
            user_data["StocksBuyPrice"][f"{main_symbol}_P"] = price

            self.collection.update_one(
                {"ID": ctx.author.id}, {"$set": user_data}, upsert=True
            )

            console_channel = self.bot.get_channel(CONSOLE_CHANNEL)
            sent = await console_channel.send(
                f"eco take {user_data['Username']} {total_price}"
            )

            def check(m):
                return (
                    m.channel.id == console_channel.id
                    and m.author.id == 1270255175579471963
                )

            try:
                m = await self.bot.wait_for("message", check=check)

            except Exception as e:
                embed = discord.Embed(
                    title="Purchase Timeout",
                    description="Could not complete purchase. Please try again later.",
                    color=0xFF0000,
                )
                return await ctx.respond(embed=embed, ephemeral=True)

            if "Error:" in m.content.split(" "):
                embed = discord.Embed(
                    title="Purchase Unsuccessful",
                    description="### Insufficient Balance",
                    color=0xFF0000,
                )
                return await ctx.respond(embed=embed, ephemeral=True)

            if m.content:
                balance_raw = m.content.split(" ")[-1][1:]
                balance = balance_raw.split(".")[0]

                embed = discord.Embed(
                    title="Purchase Successful",
                    description=(
                        f"Successfully bought {quantity} {symbol} stocks\n"
                        f"### Total Price: $ {total_price}\n"
                        f"### New Balance: $ {balance}"
                    ),
                    color=0xD5E4CF,
                )
                await ctx.respond(embed=embed, ephemeral=True)

        except Exception as e:
            embed = discord.Embed(
                title="Error",
                description="An error occurred. Please try again later.",
                color=0xFF0000,
            )
            await ctx.respond(embed=embed, ephemeral=True)
            print(f"[ - ] Stocks COG : Error : {e}")

    @stock.command(
        name="sell",
        description="Sell Stocks (Minecraft Economy)",
    )
    @option(
        "symbol",
        description="The Stock Symbol",
        choices=["AMD", "APPLE", "INTEL", "GOOGLE", "MICROSOFT"],
    )
    @option("quantity", description="The Quantity Of Stocks To Sell", type=int)
    async def sell(self, ctx, symbol: str, quantity: int):
        await ctx.defer(ephemeral=True)

        if symbol not in ["AMD", "APPLE", "INTEL", "GOOGLE", "MICROSOFT"]:
            embed = discord.Embed(
                title="Invalid Symbol",
                description="Please Enter A Valid Symbol",
                color=0xFF0000,
            )

            embed.add_field(
                name="Valid Symbols",
                value="AMD, APPLE, INTEL, GOOGLE, MICROSOFT",
                inline=True,
            )

            await ctx.respond(embed=embed, ephemeral=True)
            return

        symbols = {
            "AMD": "AMD",
            "APPLE": "AAPL",
            "INTEL": "INTC",
            "GOOGLE": "GOOGL",
            "MICROSOFT": "MSFT",
        }

        main_symbol = symbols.get(symbol, symbol.upper())

        try:
            quote = self.finnhub_client.quote(symbol=main_symbol)

            if not quote:
                embed = discord.Embed(
                    title="Stock Data Unavailable",
                    description="Could Not Retrieve Stock Information. Please Try Again Later.",
                    color=0xFF0000,
                )
                return await ctx.respond(embed=embed, ephemeral=True)

            price = quote.get("c", 0)
            total_price = price * quantity

            document = self.collection.find_one({"ID": ctx.author.id})
            if not document:
                embed = discord.Embed(
                    title="No Stocks",
                    description="You Don't Have Any Stocks To Sell",
                    color=0xFF0000,
                )
                return await ctx.respond(embed=embed, ephemeral=True)

            current_amount = document["StocksAmount"].get(main_symbol, 0)
            if current_amount < quantity:
                embed = discord.Embed(
                    title="Insufficient Stocks",
                    description="You Don't Have Enough Stocks To Sell",
                    color=0xFF0000,
                )
                return await ctx.respond(embed=embed, ephemeral=True)

            user_data = document
            user_data["StocksAmount"][main_symbol] = current_amount - quantity

            self.collection.update_one(
                {"ID": ctx.author.id}, {"$set": user_data}, upsert=True
            )

            console_channel = self.bot.get_channel(CONSOLE_CHANNEL)
            sent = await console_channel.send(
                f"eco give {user_data['Username']} {total_price}"
            )

            def check(m):
                return (
                    m.channel.id == console_channel.id
                    and m.author.id == 1270255175579471963
                )

            try:
                m = await self.bot.wait_for("message", check=check)

            except Exception as e:
                embed = discord.Embed(
                    title="Sale Timeout",
                    description="Could Not Complete Sale. Please Try Again Later.",
                    color=0xFF0000,
                )
                return await ctx.respond(embed=embed, ephemeral=True)

            if m.content:
                balance_raw = m.content.split(" ")[-1][1:]
                balance = balance_raw.split(".")[0]

                embed = discord.Embed(
                    title="Sale Successful",
                    description=(
                        f"Successfully Sold {quantity} {symbol} Stocks\n"
                        f"### Total Price: $ {total_price}\n"
                        f"### New Balance: $ {balance}"
                    ),
                    color=0xD5E4CF,
                )
                await ctx.respond(embed=embed, ephemeral=True)

        except Exception as e:
            embed = discord.Embed(
                title="Error",
                description="An Error Occurred. Please Try Again Later.",
                color=0xFF0000,
            )
            await ctx.respond(embed=embed, ephemeral=True)
            print(f"[ - ] Stocks COG : Error : {e}")


def setup(bot):
    bot.add_cog(Stocks(bot))
