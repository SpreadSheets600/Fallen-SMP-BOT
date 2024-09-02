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
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tax_data (
            user_id INTEGER PRIMARY KEY,
            amount REAL,
            last_pay_date DATE,
            week_no INTEGER
        )
    """
    )
    connection.commit()

    cursor.close()
    connection.close()


# =================================================================================================== #


class InGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.mongo_client = MongoClient(os.getenv("MONGO_URI"))
        self.db = self.mongo_client["Users"]
        self.collection = self.db["UserData"]

    tax = SlashCommandGroup(
        name="tax",
        description="Tax Related Commands",
    )

    @tax.command(
        name="add",
        description="add Taxes ( In Game Money )",
    )
    async def add_tax(self, ctx, user: discord.Member, amount: int):

        await ctx.defer(ephemeral=True)

        if ctx.author.id not in ADMINS:
            return await ctx.respond(
                "SOHAM Will Get Tax Invasion If He Let's You Use It", ephemeral=True
            )

        user_id = user.id
        document = self.collection.find_one({"ID": user_id})

        if not document:
            embed = discord.Embed(
                title=":x: Error",
                description="User Not Registered In The Database\nPlease Get The User Whitelisted First",
                color=0xFF0000,
            )

            await ctx.respond(embed=embed, ephemeral=True)

        else:
            connection = get_db_connection()
            cursor = connection.cursor()

            week_no = datetime.now().isocalendar()[1]

            cursor.execute(
                """
                INSERT INTO tax_data (user_id, amount, last_pay_date, week_no)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    amount=excluded.amount,
                    last_pay_date=excluded.last_pay_date,
                    week_no=excluded.week_no
            """,
                (user_id, amount, datetime.now().date(), week_no),
            )

            connection.commit()
            cursor.close()

            embed = discord.Embed(
                title=":white_check_mark: Success",
                description=f"### Added `{amount}` To `{user.display_name}` Taxes",
                color=0x00FF00,
            )

            await ctx.respond(embed=embed, ephemeral=True)

            user = self.bot.get_user(user_id)

            try:
                await user.send(embed=embed)
            except discord.Forbidden:
                pass

    @tax.command(
        name="remove",
        description="Remove Taxes ( In Game Money )",
    )
    async def remove_tax(self, ctx, user: discord.Member, amount: int):

        await ctx.defer(ephemeral=True)

        if ctx.author.id not in ADMINS:
            return await ctx.respond(
                "SOHAM Will Get Tax Invasion If He Let's You Use It", ephemeral=True
            )

        user_id = user.id
        document = self.collection.find_one({"ID": user_id})

        if not document:
            embed = discord.Embed(
                title=":x: Error",
                description="User Not Registered In The Database\nPlease Get The User Whitelisted First",
                color=0xFF0000,
            )

            await ctx.respond(embed=embed, ephemeral=True)

        else:
            connection = get_db_connection()
            cursor = connection.cursor()

            week_no = datetime.now().isocalendar()[1]

            cursor.execute(
                """
                INSERT INTO tax_data (user_id, amount, last_pay_date, week_no)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    amount=excluded.amount,
                    last_pay_date=excluded.last_pay_date,
                    week_no=excluded.week_no
            """,
                (user_id, amount, datetime.now().date(), week_no),
            )

            connection.commit()
            cursor.close()

            emebd = discord.Embed(
                title=":white_check_mark: Success",
                description=f"### Removed `{amount}` From `{user.display_name}` Taxes",
                color=0x00FF00,
            )

            await ctx.respond(embed=embed, ephemeral=True)

            user = self.bot.get_user(user_id)

            try:
                await user.send(embed=embed)
            except discord.Forbidden:
                pass

    @tax.command(
        name="update",
        description="Update Taxes ( In Game Money )",
    )
    async def update_tax(self, ctx, user: discord.Member, amount: int):

        await ctx.defer(ephemeral=True)

        if ctx.author.id not in ADMINS:
            return await ctx.respond(
                "SOHAM Will Get Tax Invasion If He Let's You Use It", ephemeral=True
            )

        user_id = user.id
        document = self.collection.find_one({"ID": user_id})

        if not document:
            embed = discord.Embed(
                title=":x: Error",
                description="User Not Registered In The Database\nPlease Get The User Whitelisted First",
                color=0xFF0000,
            )

            await ctx.respond(embed=embed, ephemeral=True)

        else:
            connection = get_db_connection()
            cursor = connection.cursor()

            week_no = datetime.now().isocalendar()[1]

            cursor.execute(
                """
            UPDATE tax_data
            SET amount = ?
            WHERE user_id = ?
        """,
                (amount, user.id),
            )

            connection.commit()
            cursor.close()

            emebd = discord.Embed(
                title=":white_check_mark: Success",
                description=f"### Updated `{user.display_name}` Taxes To `{amount}`",
                color=0x00FF00,
            )

            await ctx.respond(embed=embed, ephemeral=True)

            user = self.bot.get_user(user_id)

            try:
                await user.send(embed=embed)
            except discord.Forbidden:
                pass

    @tax.command(
        name="pay",
        description="Pay Taxes ( In Game Money )",
    )
    async def pay_tax(self, ctx):

        await ctx.defer(ephemeral=True)

        user_id = ctx.author.id
        document = self.collection.find_one({"ID": user_id})

        if not document:
            embed = discord.Embed(
                title=":x: Error",
                description="User Not Registered In The Database\nPlease Contact The Admins To Get Registered",
                color=0xFF0000,
            )

            await ctx.respond(embed=embed, ephemeral=True)

        else:

            username = document["Username"]

            connection = get_db_connection()
            cursor = connection.cursor()

            user_id = ctx.author.id
            week_no = datetime.now().isocalendar()[1]

            cursor.execute(
                "SELECT amount FROM tax_data WHERE user_id = ? AND week_no = ?",
                (user_id, week_no),
            )
            result = cursor.fetchone()

            if result:
                amount = result[0]

                cursor.execute(
                    """
                    UPDATE tax_data
                    SET last_pay_date = ?, week_no = ?
                    WHERE user_id = ?
                """,
                    (datetime.now().date(), week_no, user_id),
                )

                connection.commit()
                cursor.close()

                console_channel = self.bot.get_channel(CONSOLE_CHANNEL)
                await console_channel.send(f"eco take {username} {amount}")

                def check(message):
                    return (
                        message.author == 1261353536206274672
                        and message.channel == CONSOLE_CHANNEL
                    )

                try:
                    message = await self.bot.wait_for(
                        "message", check=check, timeout=30
                    )

                    if message.startswith("The minimum balance"):
                        embed = discord.Embed(
                            title=":x: Payment Failed",
                            description="You Do Not Have Enough Money To Pay Taxes",
                            color=0xFF0000,
                        )

                        return await ctx.respond(embed=embed, ephemeral=True)

                    if message.startswith("$"):
                        embed = discord.Embed(
                            title=":white_check_mark: Payment Success",
                            description=f"### Paid `{amount}` Taxes",
                            color=0x00FF00,
                        )

                        return await ctx.respond(embed=embed, ephemeral=True)

                except asyncio.TimeoutError:
                    return await ctx.respond("Failed To Pay Taxes", ephemeral=True)

            else:
                embed = discord.Embed(
                    title=":x: Error",
                    description="Tax Amount Not Set\nPlease Contact The Admins",
                    color=0xFF0000,
                )

                await ctx.respond(embed=embed, ephemeral=True)

    @tax.command(
        name="info",
        description="Get Tax Information",
    )
    async def tax_info(self, ctx, user: discord.Member = None):
        await ctx.defer(ephemeral=True)

        if not user:
            user = ctx.author

        user_id = user.id
        week_no = datetime.now().isocalendar()[1]

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT amount, last_pay_date
            FROM tax_data
            WHERE user_id = ? AND week_no = ?
            """,
            (user_id, week_no),
        )

        result = cursor.fetchone()

        if result:
            amount, last_pay_date_str = result

            if last_pay_date_str:
                last_pay_date = datetime.strptime(last_pay_date_str, "%Y-%m-%d")
                last_pay_date_discord = f"<t:{int(last_pay_date.timestamp())}:F>"
            else:
                last_pay_date_discord = "Not Yet Paid"

            last_pay_datetime = last_pay_date if last_pay_date_str else datetime.now()
            next_pay_date = last_pay_datetime + timedelta(weeks=1)
            next_pay_date_discord = f"<t:{int(next_pay_date.timestamp())}:F>"

            embed = discord.Embed(
                title=":white_check_mark: Tax Information",
                description=f"### `{user.display_name}` Owes `{amount}` Taxes\n\n### Week No: `{week_no}`",
                color=0x00FF00,
            )

            embed.add_field(
                name="Last Pay Date",
                value=last_pay_date_discord,
                inline=False,
            )

            embed.add_field(
                name="Next Pay Date",
                value=next_pay_date_discord,
                inline=False,
            )

            await ctx.respond(embed=embed, ephemeral=True)

        else:
            embed = discord.Embed(
                title=":x: Error",
                description="Tax Amount Not Set\nPlease Contact The Admins",
                color=0xFF0000,
            )

            await ctx.respond(embed=embed, ephemeral=True)

        cursor.close()
        connection.close()

    @tasks.loop(hours=24)
    async def tax_auto_pay(self):
        connection = get_db_connection()
        cursor = connection.cursor()

        current_date = datetime.now().date()
        week_no = datetime.now().isocalendar()[1]

        cursor.execute(
            """
            SELECT user_id, amount
            FROM tax_data
            WHERE last_pay_date < ? AND week_no = ?
            """,
            (current_date - timedelta(weeks=1), week_no),
        )

        users_to_pay = cursor.fetchall()

        for user_id, amount in users_to_pay:
            cursor.execute(
                """
                UPDATE tax_data
                SET last_pay_date = ?
                WHERE user_id = ?
                """,
                (current_date, user_id),
            )

            connection.commit()
            user = self.bot.get_user(user_id)

            document = self.collection.find_one({"ID": user_id})

            if not document:
                continue

            username = document["Username"]
            console_channel = self.bot.get_channel(CONSOLE_CHANNEL)
            await console_channel.send(f"eco take {username} {amount}")

            def check(message):
                return (
                    message.author.id == 1261353536206274672
                    and message.channel.id == CONSOLE_CHANNEL
                )

            try:
                message = await self.bot.wait_for("message", check=check, timeout=30)

                if message.content.startswith("The minimum balance"):
                    continue

                if message.content.startswith("$"):
                    embed = discord.Embed(
                        title=":white_check_mark: Automatic Payment Success",
                        description=f"### Paid `{amount}` Taxes",
                        color=0x00FF00,
                    )

                    try:
                        await user.send(embed=embed)
                    except discord.Forbidden:
                        pass

            except asyncio.TimeoutError:
                continue

        cursor.close()
        connection.close()

    @commands.Cog.listener()
    async def on_ready(self):
        print("[ + ] InGame COG : OnReady")

        initialize_db()
        print("[ + ] Tax Database Initialized")

        if not self.tax_auto_pay.is_running():
            self.tax_auto_pay.start()


def setup(bot):
    bot.add_cog(InGame(bot))
