import os
import json
import random
import sqlite3
import pymongo
import discord
import asyncio
import datetime
import traceback
from discord.ext import tasks
from datetime import datetime
from datetime import timedelta
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


def get_db_connection():
    return sqlite3.connect("Tax.db")


def initialize_db():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tax_data (
                user_id INTEGER PRIMARY KEY,
                amount REAL,
                last_pay_date DATE,
                next_pay_date DATE
            )
        """
        )
        connection.commit()
    except Exception as e:
        print(f"[ - ] InGame COG : DataBase Error : {e}")
    finally:
        cursor.close()
        connection.close()


# =================================================================================================== #


class InGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mongo_client = MongoClient(os.getenv("MONGO_URI"))
        self.db = self.mongo_client["Users"]
        self.collection = self.db["UserData"]

    tax = SlashCommandGroup(name="tax", description="Tax Related Commands")

    async def update_tax_record(self, user_id, amount, last_pay_date, next_pay_date):
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO tax_data (user_id, amount, last_pay_date, next_pay_date)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    amount=excluded.amount,
                    last_pay_date=excluded.last_pay_date,
                    next_pay_date=excluded.next_pay_date
                """,
                (user_id, amount, last_pay_date, next_pay_date),
            )
            connection.commit()
        except Exception as e:
            print(f"[ - ] InGame COG : DataBase Error : {e}")
        finally:
            cursor.close()
            connection.close()

    async def notify_payment(self, user_id, amount, success=True):
        try:
            user = self.bot.get_user(user_id)
            if success:
                embed = discord.Embed(
                    title=":white_check_mark: Tax Payment Success",
                    description=f"Paid `{amount}` Taxes",
                    color=0x00FF00,
                )
            else:
                embed = discord.Embed(
                    title=":x: Tax Payment Failed",
                    description="You Do Not Have Enough Money To Pay Taxes",
                    color=0xFF0000,
                )
            await user.send(embed=embed)
        except discord.Forbidden:
            print(f"Could not DM the user: {user_id}")

    @tax.command(name="info", description="Get Tax Info")
    async def tax_info(self, ctx, user: discord.Member = None):
        await ctx.defer(ephemeral=True)
        if user is None:
            user = ctx.author

        user_id = user.id
        document = self.collection.find_one({"ID": user_id})

        if not document:
            embed = discord.Embed(
                title=":x: Error",
                description="User Not Found In Database.\nPlease Contact The Admins.",
                color=0xFF0000,
            )
            return await ctx.respond(embed=embed, ephemeral=True)

        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                "SELECT amount, last_pay_date, next_pay_date FROM tax_data WHERE user_id = ?",
                (user_id,),
            )
            result = cursor.fetchone()

            if not result:
                embed = discord.Embed(
                    title=":x: Error",
                    description="Tax Amount Not Set.\nPlease Contact The Admins.",
                    color=0xFF0000,
                )
                return await ctx.respond(embed=embed, ephemeral=True)

            amount, last_pay_date, next_pay_date = result
            current_date = datetime.now().date()

            embed = discord.Embed(
                title=":moneybag: Tax Info",
                description=f"**User:** {user.mention}\n**Amount:** {amount}\n**Last Pay Date:** {last_pay_date}\n**Next Pay Date:** {next_pay_date}",
                color=0x00FF00,
            )
            await ctx.respond(embed=embed, ephemeral=True)

        finally:
            cursor.close()
            connection.close()

    @tax.command(name="update", description="Update Tax Info")
    async def update_tax(self, ctx, user: discord.Member, amount: int):
        await ctx.defer(ephemeral=True)
        if ctx.author.id not in ADMINS:
            return await ctx.respond("Pagal Hai Kaya ?!", ephemeral=True)

        user_id = user.id
        current_date = datetime.now().date()
        next_pay_date = current_date + timedelta(days=1)
        await self.update_tax_record(user_id, amount, current_date, next_pay_date)

        embed = discord.Embed(
            title=":white_check_mark: Success",
            description=f"Updated `{user.display_name}`'s Taxes To `{amount}`",
            color=0x00FF00,
        )
        await ctx.respond(embed=embed, ephemeral=True)

        try:
            await user.send(embed=embed)
        except discord.Forbidden:
            print(f"Could Not DM The User: {user_id}")

    @tax.command(name="add", description="Add taxes")
    async def add_tax(self, ctx, user: discord.Member, amount: int):
        await ctx.defer(ephemeral=True)
        if ctx.author.id not in ADMINS:
            return await ctx.respond("Pagal Hai Kaya ?!", ephemeral=True)

        user_id = user.id
        current_date = datetime.now().date()
        next_pay_date = current_date + timedelta(days=1)
        await self.update_tax_record(user_id, amount, current_date, next_pay_date)

        embed = discord.Embed(
            title=":white_check_mark: Success",
            description=f"Added `{amount}` To `{user.display_name}`'s Taxes",
            color=0x00FF00,
        )
        await ctx.respond(embed=embed, ephemeral=True)

        try:
            await user.send(embed=embed)
        except discord.Forbidden:
            print(f"Could Not DM The User: {user_id}")

    @tax.command(name="pay", description="Pay taxes")
    async def pay_tax(self, ctx):
        await ctx.defer(ephemeral=True)
        user_id = ctx.author.id
        document = self.collection.find_one({"ID": user_id})

        if not document:
            embed = discord.Embed(
                title=":x: Error",
                description="User Not Found In Database.\nPlease Contact The Admins.",
                color=0xFF0000,
            )
            return await ctx.respond(embed=embed, ephemeral=True)

        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                "SELECT amount, next_pay_date FROM tax_data WHERE user_id = ?",
                (user_id,),
            )
            result = cursor.fetchone()

            if not result:
                embed = discord.Embed(
                    title=":x: Error",
                    description="Tax Amount Not Set.\nPlease Contact The Admins.",
                    color=0xFF0000,
                )
                return await ctx.respond(embed=embed, ephemeral=True)

            amount, next_pay_date = result
            current_date = datetime.now().date()

            if current_date < next_pay_date:
                time_left = next_pay_date - current_date
                embed = discord.Embed(
                    title=":clock1: Tax Payment Not Due",
                    description=f"Your Next Tax Payment Is Due {time_left.days} Days.",
                    color=0xFFFF00,
                )
                return await ctx.respond(embed=embed, ephemeral=True)

            # Attempt to pay taxes
            success = await self.execute_tax_payment(ctx, user_id, amount)

            if success:
                new_next_pay_date = current_date + timedelta(days=1)
                await self.update_tax_record(
                    user_id, amount, current_date, new_next_pay_date
                )
                embed = discord.Embed(
                    title=":white_check_mark: Tax Payment Success",
                    description=f"Paid `{amount}` Taxes.\nNext Payment Due On {new_next_pay_date}.",
                    color=0x00FF00,
                )
            else:
                embed = discord.Embed(
                    title=":x: Tax Payment Failed",
                    description="You Do Not Have Enough Money To Pay Taxes",
                    color=0xFF0000,
                )

            await ctx.respond(embed=embed, ephemeral=True)
            await self.notify_payment(user_id, amount, success)

        finally:
            cursor.close()
            connection.close()

    async def execute_tax_payment(self, ctx, user_id, amount):
        document = self.collection.find_one({"ID": user_id})
        username = document["Username"]

        console_channel = self.bot.get_channel(CONSOLE_CHANNEL)
        await console_channel.send(f"eco take {username} {amount}")

        def check(message):
            return (
                message.author.id == 1270255175579471963
                and message.channel.id == CONSOLE_CHANNEL
            )

        try:
            message = await self.bot.wait_for("message", check=check, timeout=30)
            return not message.content.startswith("The minimum balance")
        except asyncio.TimeoutError:
            return False

    @tasks.loop(hours=24)
    async def tax_auto_pay(self):
        connection = get_db_connection()
        cursor = connection.cursor()

        current_date = datetime.now().date()

        try:
            cursor.execute(
                "SELECT user_id, amount, next_pay_date FROM tax_data WHERE next_pay_date <= ?",
                (current_date,),
            )
            users_to_pay = cursor.fetchall()

            for user_id, amount, next_pay_date in users_to_pay:
                if current_date >= next_pay_date:
                    success = await self.execute_tax_payment(None, user_id, amount)

                    if success:
                        new_next_pay_date = current_date + timedelta(weeks=1)
                        await self.update_tax_record(
                            user_id, amount, current_date, new_next_pay_date
                        )

                    await self.notify_payment(user_id, amount, success)

        finally:
            cursor.close()
            connection.close()

    @commands.slash_command(name="WTS", description="Sell An Item")
    async def wts(self, ctx, item: str, price: int, amount: int = 1):
        await ctx.defer()

        user_id = ctx.author.id
        document = self.collection.find_one({"ID": user_id})

        if not document:
            embed = discord.Embed(
                title=":x: Error",
                description="User Not Found In Database.\nPlease Contact The Admins.",
                color=0xFF0000,
            )
            return await ctx.respond(embed=embed, ephemeral=True)

        embed = discord.Embed(
            title=":white_check_mark: Success",
            description=f"Item `{item}` Listed For Sale At `{price}`",
            color=0x00FF00,
        )

        embed.add_field(
            name="Seller",
            value=f"{ctx.author.mention} ({document['Username']})",
            inline=True,
        )
        embed.add_field(name="Amount", value=str(amount), inline=True)
        embed.add_field(name="Price", value=str(price), inline=True)

        await ctx.respond(embed=embed)

        thread = await ctx.create_thread(
            name=f"WTS : {item} : {ctx.author.display_name}"
        )
        await thread.send(f"Item: {item}\nAmount: {amount}\nPrice: {price}")

    @commands.slash_command(name="WTB", description="Buy An Item")
    async def wtb(self, ctx, item: str, price: int, amount: int = 1):
        await ctx.defer()

        user_id = ctx.author.id
        document = self.collection.find_one({"ID": user_id})

        if not document:
            embed = discord.Embed(
                title=":x: Error",
                description="User Not Found In Database.\nPlease Contact The Admins.",
                color=0xFF0000,
            )
            return await ctx.respond(embed=embed, ephemeral=True)

        embed = discord.Embed(
            title=":white_check_mark: Success",
            description=f"Item `{item}` Listed For Purchase At `{price}`",
            color=0x00FF00,
        )

        embed.add_field(
            name="Buyer",
            value=f"{ctx.author.mention} ({document['Username']})",
            inline=True,
        )
        embed.add_field(name="Amount", value=str(amount), inline=True)
        embed.add_field(name="Price", value=str(price), inline=True)

        await ctx.respond(embed=embed)

        thread = await ctx.create_thread(
            name=f"WTB : {item} : {ctx.author.display_name}"
        )
        await thread.send(f"Item: {item}\nAmount: {amount}\nPrice: {price}")

    @commands.Cog.listener()
    async def on_ready(self):
        print("[ + ] InGame COG : OnReady")
        initialize_db()
        print("[ + ] Tax Database Initialized")
        if not self.tax_auto_pay.is_running():
            self.tax_auto_pay.start()


def setup(bot):
    bot.add_cog(InGame(bot))
