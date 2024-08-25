import os
import json
import random
import pymongo
import discord
import asyncio
import finnhub
import datetime
from discord import option
from pymongo import MongoClient
from discord.ext.pages import *
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

    @bridge.bridge_group()
    async def stock(self, ctx):
        pass

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

        await ctx.defer(ephermal=True)

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
            print(f"[ - ] Whitelist COG : Error : {e}")
            await ctx.respond(
                f"[ - ] Whitelist COG : Error : \n```{e}```",
                ephemeral=True,
                delete_after=5,
            )
            ErrorChannel = self.bot.get_channel(ERROR_CHANNEL)
            await ErrorChannel.send(f"[ - ] Whitelist COG : Error : \n```{e}```")

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

        await ctx.defer(ephermal=True)

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
            print(f"[ - ] Whitelist COG : Error : {e}")
            await ctx.respond(
                f"[ - ] Whitelist COG : Error : \n```{e}```",
                ephemeral=True,
                delete_after=5,
            )
            ErrorChannel = self.bot.get_channel(ERROR_CHANNEL)
            await ErrorChannel.send(f"[ - ] Whitelist COG : Error : \n```{e}```")


    @stock.command(
        name="portfolio",
        description="Get User Portfolio",
    )
    async def portfolio(self, ctx):
        await ctx.defer(ephermal=True)

        try:
            document = self.collection.find_one({"ID": ctx.author.id})

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

            pnl = {
                "AMD": current_prices["AMD"] - stocks_buy_price["AMD_P"],
                "AAPL": current_prices["AAPL"] - stocks_buy_price["AAPL_P"],
                "INTC": current_prices["INTC"] - stocks_buy_price["INTC_P"],
                "GOOGL": current_prices["GOOGL"] - stocks_buy_price["GOOGL_P"],
                "MSFT": current_prices["MSFT"] - stocks_buy_price["MSFT_P"]
            }

            if document:
                stocks_amount = document["StocksAmount"]
                stocks_buy_price = document["StocksBuyPrice"]
                timestamp = document["Timestamp"]

                embed = discord.Embed(
                    title=f"{ctx.author.display_name}'s Portfolio",
                    description=f"Last Updated : {timestamp}",
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
                        f"${round(pnl['AMD'], 2)}\n"
                        f"${round(pnl['AAPL'], 2)}\n"
                        f"${round(pnl['INTC'], 2)}\n"
                        f"${round(pnl['GOOGL'], 2)}\n"
                        f"${round(pnl['MSFT'], 2)}"
                    ),
                    inline=True,
                )

                await ctx.respond(embed=embed, ephemeral=True)

            else:
                embed = discord.Embed(
                    title="{ctx.author.display_name}'s Portfolio",
                    description="You Don't Have Any Stocks",
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

    @stock.command(
        name="sell",
        description="Sell Stocks (Minectaft Economy)",
    )
    @option(
        "symbol",
        description="The Stock Symbol",
        choices=["AMD", "APPLE", "INTEL", "GOOGLE", "MICROSOFT"],
    )
    @option("quantity", description="The Quantity Of Stocks To Sell", type=int)
    async def sell(self, ctx, symbol: str, quantity: int):
        await ctx.defer(ephermal=True)

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
                price = quote.get("c", 0)
                total_price = price * quantity

                document = self.collection.find_one({"ID": ctx.author.id})
                if not document:

                    user_data = {
                        "ID": ctx.author.id,
                        "StocksAmount": {"AMD": 0, "AAPL": 0, "INTC": 0, "GOOGL": 0, "MSFT": 0},
                        "StocksBuyPrice": {"AMD_P": 0, "AAPL_P": 0, "INTC_P": 0, "GOOGL_P": 0, "MSFT_P": 0},
                        "Timestamp": "2024-08-22T12:00:00Z",
                    }

                current_amount = user_data["StocksAmount"].get(main_symbol, 0)
                user_data["StocksAmount"][main_symbol] = current_amount + quantity
                user_data["StocksBuyPrice"][f"{main_symbol}_P"] = price

                self.collection.update_one({"ID": ctx.author.id}, {"$set": user_data}, upsert=True)

        except Exception as e:
            pass