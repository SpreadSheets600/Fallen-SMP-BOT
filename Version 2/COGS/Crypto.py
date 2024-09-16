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

CONSOL_CHANNEL = 1263898954999922720
ERROR_CHANNEL = 1275759089024241797

# =================================================================================================== #


class Crypto(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.mongo_client = MongoClient(os.getenv("MONGO_URI"))

        self.db = self.mongo_client["Users"]
        self.collection = self.db["UserCrypto"]

        self.finnhub_client = finnhub.Client(api_key=os.getenv("FINNHUB_API_KEY"))

    def fetch_news(self, symbol):
        today = datetime.datetime.today()
        date = today.strftime("%Y-%m-%d")
        return self.finnhub_client.company_news(symbol, _from=date, to=date)

    crypto = SlashCommandGroup(name="crypto", description="Crypto Commands")

    @crypto.command(
        name="quote",
        description="Get The Current Price Of A Crypto",
    )
    @option(
        "symbol",
        description="The Crypto Symbol",
        choices=["BTC", "ETH", "BNB", "SOL", "AVAX"],
    )
    async def quote(self, ctx, symbol):

        await ctx.defer(ephemeral=True)

        valid_symbols = ["BTC", "ETH", "BNB", "SOL", "AVAX"]

        if symbol not in valid_symbols:
            embed = discord.Embed(
                title="Invalid Symbol",
                description="Please Enter A Valid Symbol",
                color=0xFF0000,
            )

            embed.add_field(
                name="Valid Symbols",
                value="BTC, ETH, BNB, SOL, AVAX",
                inline=True,
            )

            await ctx.respond(embed=embed, ephemeral=True)
            return

        symbols = {
            "BTC": "BTC-USD",
            "ETH": "ETH-USD",
            "BNB": "BNB-USD",
            "SOL": "SOL-USD",
            "AVAX": "AVAX-USD",
        }

        try:
            main_symbol = symbols[symbol]
        except Exception as e:
            main_symbol = symbol.upper()

        try:
            quote = self.finnhub_client.quote(symbol=main_symbol)

            if quote:
                embed = discord.Embed(
                    title=f"{symbol} Crypto Quote",
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

    @crypto.command(
        name="portfolio",
        description="Get User Portfolio",
    )
    async def portfolio(self, ctx, user: discord.Member = None):
        await ctx.defer(ephemeral=True)

        if user is None or ctx.author.id not in ADMINS:
            user = ctx.author

        try:
            document = self.collection.find_one({"ID": user.id})

            ETH_current_price = self.finnhub_client.quote(symbol="ETH-USD")["c"]
            BTC_current_price = self.finnhub_client.quote(symbol="BTC-USD")["c"]
            BNB_current_price = self.finnhub_client.quote(symbol="BNB-USD")["c"]
            SOL_current_price = self.finnhub_client.quote(symbol="SOL-USD")["c"]
            AVAX_current_price = self.finnhub_client.quote(symbol="AVAX-USD")["c"]

            current_prices = {
                "ETH": ETH_current_price,
                "BTC": BTC_current_price,
                "BNB": BNB_current_price,
                "SOL": SOL_current_price,
                "AVAX": AVAX_current_price,
            }

            if document:
                stocks_amount = document["CryptoAmount"]
                stocks_buy_price = document["CryptoBuyPrice"]
                timestamp = datetime.datetime.now().isoformat()

                for keys in stocks_amount.keys():
                    if stocks_buy_price[f"{keys}_P"] == 0:
                        stocks_buy_price[f"{keys}_P"] = current_prices[keys]

                pnl = {
                    "ETH": current_prices["ETH"] - stocks_buy_price["ETH_P"],
                    "BTC": current_prices["BTC"] - stocks_buy_price["BTC_P"],
                    "BNB": current_prices["BNB"] - stocks_buy_price["BNB_P"],
                    "SOL": current_prices["SOL"] - stocks_buy_price["SOL_P"],
                    "AVAX": current_prices["AVAX"] - stocks_buy_price["AVAX_P"],
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
                    name="Crypto",
                    value="ETH\nBTC\nBNB\nSOL\nAVAX",
                    inline=True,
                )
                embed.add_field(
                    name="Amount",
                    value=(
                        f"{stocks_amount['ETH']}\n"
                        f"{stocks_amount['BTC']}\n"
                        f"{stocks_amount['BNB']}\n"
                        f"{stocks_amount['SOL']}\n"
                        f"{stocks_amount['AVAX']}"
                    ),
                    inline=True,
                )
                embed.add_field(
                    name="PNL",
                    value=(
                        f"$ {round(pnl['ETH'], 2)}\n"
                        f"$ {round(pnl['BTC'], 2)}\n"
                        f"$ {round(pnl['BNB'], 2)}\n"
                        f"$ {round(pnl['SOL'], 2)}\n"
                        f"$ {round(pnl['AVAX'], 2)}"
                    ),
                    inline=True,
                )

                await ctx.respond(embed=embed, ephemeral=True)

            else:
                embed = discord.Embed(
                    title=f"{ctx.author.display_name}'s Portfolio",
                    description="You Don't Have Any Crypto",
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

    @crypto.command(
        name="buy",
        description="Buy Crypto (Minecraft Economy)",
    )
    @option(
        "symbol",
        description="The Crypto Symbol",
        choices=["BTC", "ETH", "BNB", "SOL", "AVAX"],
    )
    @option("quantity", description="The Quantity Of Crypto To Buy", type=int)
    async def buy(self, ctx, symbol: str, quantity: int):
        await ctx.defer(ephemeral=True)

        if symbol not in ["BTC", "ETH", "BNB", "SOL", "AVAX"]:
            embed = discord.Embed(
                title="Invalid Symbol",
                description="Please Enter A Valid Symbol",
                color=0xFF0000,
            )

            embed.add_field(
                name="Valid Symbols",
                value="ETH, BTC, BNB, SOL, AVAX",
                inline=True,
            )

            await ctx.respond(embed=embed, ephemeral=True)
            return

        symbols = {
            "ETH": "ETH-USD",
            "BTC": "BTC-USD",
            "BNB": "BNB-USD",
            "SOL": "SOL-USD",
            "AVAX": "AVAX-USD",
        }

        main_symbol = symbols.get(symbol, symbol.upper())

        try:
            quote = self.finnhub_client.quote(symbol=main_symbol)

            if not quote:
                embed = discord.Embed(
                    title="Crypto Data Unavailable",
                    description="Could Not Retrieve Crypto Information. Please Try Again Later.",
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
                    "CryptoAmount": {symbol: 0 for symbol in symbols.values()},
                    "CryptoBuyPrice": {f"{symbol}_P": 0 for symbol in symbols.values()},
                    "Timestamp": "2024-08-22T12:00:00Z",
                }
            else:
                user_data = document

            current_amount = user_data["CryptoAmount"].get(main_symbol, 0)
            user_data["CryptoAmount"][main_symbol] = current_amount + quantity
            user_data["CryptoBuyPrice"][f"{main_symbol}_P"] = price

            self.collection.update_one(
                {"ID": ctx.author.id}, {"$set": user_data}, upsert=True
            )

            conSOL_channel = self.bot.get_channel(CONSOL_CHANNEL)
            sent = await conSOL_channel.send(
                f"eco take {user_data['Username']} {total_price}"
            )

            def check(m):
                return (
                    m.channel.id == conSOL_channel.id
                    and m.author.id == 1270255175579471963
                )

            try:
                m = await self.bot.wait_for("message", check=check)

            except Exception as e:
                embed = discord.Embed(
                    title="Purchase Timeout",
                    description="Could Not Complete Purchase. Please Try Again Later.",
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
                        f"Successfully bought {quantity} {symbol} Crypto\n"
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
            print(f"[ - ] Crypto COG : Error : {e}")

    @crypto.command(
        name="sell",
        description="Sell Crypto (Minecraft Economy)",
    )
    @option(
        "symbol",
        description="The Crypto Symbol",
        choices=["BTC", "ETH", "BNB", "SOL", "AVAX"],
    )
    @option("quantity", description="The Quantity Of Crypto To Sell", type=int)
    async def sell(self, ctx, symbol: str, quantity: int):
        await ctx.defer(ephemeral=True)

        if symbol not in ["BTC", "ETH", "BNB", "SOL", "AVAX"]:
            embed = discord.Embed(
                title="Invalid Symbol",
                description="Please Enter A Valid Symbol",
                color=0xFF0000,
            )

            embed.add_field(
                name="Valid Symbols",
                value="ETH, BTC, BNB, SOL, AVAX",
                inline=True,
            )

            await ctx.respond(embed=embed, ephemeral=True)
            return

        symbols = {
            "ETH": "ETH-USD",
            "BTC": "BTC-USD",
            "BNB": "BNB-USD",
            "SOL": "SOL-USD",
            "AVAX": "AVAX-USD",
        }

        main_symbol = symbols.get(symbol, symbol.upper())

        try:
            quote = self.finnhub_client.quote(symbol=main_symbol)

            if not quote:
                embed = discord.Embed(
                    title="Crypto Data Unavailable",
                    description="Could Not Retrieve Crypto Information. Please Try Again Later.",
                    color=0xFF0000,
                )
                return await ctx.respond(embed=embed, ephemeral=True)

            price = quote.get("c", 0)
            total_price = price * quantity

            document = self.collection.find_one({"ID": ctx.author.id})
            if not document:
                embed = discord.Embed(
                    title="No Crypto",
                    description="You Don't Have Any Crypto To Sell",
                    color=0xFF0000,
                )
                return await ctx.respond(embed=embed, ephemeral=True)

            current_amount = document["CryptoAmount"].get(main_symbol, 0)
            if current_amount > quantity:
                embed = discord.Embed(
                    title="Insufficient Crypto",
                    description="You Don't Have Enough Crypto To Sell",
                    color=0xFF0000,
                )
                return await ctx.respond(embed=embed, ephemeral=True)

            user_data = document
            user_data["CryptoAmount"][main_symbol] = current_amount - quantity

            self.collection.update_one(
                {"ID": ctx.author.id}, {"$set": user_data}, upsert=True
            )

            conSOL_channel = self.bot.get_channel(CONSOL_CHANNEL)
            sent = await conSOL_channel.send(
                f"eco give {user_data['Username']} {total_price}"
            )

            def check(m):
                return (
                    m.channel.id == conSOL_channel.id
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
                        f"Successfully Sold {quantity} {symbol} Crypto\n"
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
            print(f"[ - ] Crypto COG : Error : {e}")

    @crypto.command(name="reset", description="Reset User Portfolio")
    async def reset(self, ctx, user: discord.Member = None):
        await ctx.defer(ephemeral=True)

        if user is None or ctx.author.id not in ADMINS:
            user = ctx.author

        try:
            for symbol in ["ETH", "BTC", "BNB", "SOL", "AVAX"]:
                document = self.collection.find_one({"ID": user.id})

                if document:
                    user_data = document
                    user_data["CryptoAmount"][symbol] = 0
                    user_data["CryptoBuyPrice"][f"{symbol}_P"] = 0

                    self.collection.update_one(
                        {"ID": user.id}, {"$set": user_data}, upsert=True
                    )

            embed = discord.Embed(
                title="Portfolio Reset",
                description="Your Portfolio Has Been Reset",
                color=0xD5E4CF,
            )

            await ctx.respond(embed=embed, ephemeral=True)

        except Exception as e:
            print(f"[ - ] Crypto COG : Error : {e}")
            await ctx.respond(
                f"[ - ] Crypto COG : Error : \n```{e}```",
                ephemeral=True,
                delete_after=5,
            )
            ErrorChannel = self.bot.get_channel(ERROR_CHANNEL)
            await ErrorChannel.send(f"[ - ] Crypto COG : Error : \n```{e}```")


def setup(bot):
    bot.add_cog(Crypto(bot))
