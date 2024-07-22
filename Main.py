import discord

intent = discord.Intents.all()
bot = discord.Bot(intents=intent)


@bot.event
async def on_ready():
    print("-----------------------------")
    print("--- + SOHAM's Utilities + ---")
    print("-----------------------------")

    await bot.change_presence(activity=discord.Game(name="With Utilities"))


whitelist_channel_id = 1252905743732969534
character_channel_id = 1261600104784334938
general_channel_id = 1220225200461840384
console_channel_id = 1220225200612708383

mc_ids = {}

qupix_whitelist_channel_id = 1264420370979753994
qupix_character_channel_id = 1263898270342840383
qupix_general_channel_id = 1264430288247848992


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    general_channel = bot.get_channel(general_channel_id)
    qupix_general_channel = bot.get_channel(qupix_general_channel_id)

    # Fallen SMP Whitelisting
    if message.channel.id == whitelist_channel_id:
        user = message.author
        mc_ids[user.id] = [message.content, message.id]

        character_channel = bot.get_channel(character_channel_id)
        user_found = False

        async for msg in character_channel.history(limit=20):
            if msg.author == user:
                user_found = True
                break

        if user_found:
            embed = discord.Embed(
                title="Player Whitelist",
                description=f"## {user.mention} Has Been Whitelisted\n\nIf You Still Have Not Been Whitelisted, Please Contact <@979191620610170950> Or <@664157606587138048>",
                color=0xC5CE97,
            )
            await general_channel.send(f"{user.mention}", embed=embed)

            message_to_react = await message.channel.fetch_message(mc_ids[user.id][1])
            await message_to_react.add_reaction("✅")

            console_channel = bot.get_channel(console_channel_id)
            await console_channel.send(f"whitelist add {mc_ids[user.id][0]}")
        else:
            embed = discord.Embed(
                title="Player Whitelist",
                description=f"## {user.mention} Has Not Been Whitelisted\n\nPlease Make Sure You Have Posted Your Character Name In The {character_channel.mention}",
                color=0xC5CE97,
            )
            await general_channel.send(f"{user.mention}", embed=embed)

    if message.channel.id == character_channel_id:
        if message.content.lower().startswith("character name"):
            user = message.author

            whitelist_channel = bot.get_channel(whitelist_channel_id)
            user_found = False

            async for msg in whitelist_channel.history(limit=20):
                if msg.author == user:
                    user_found = True
                    break

            if user_found:
                embed = discord.Embed(
                    title="Player Whitelist",
                    description=f"## {user.mention} Has Been Whitelisted\n\nIf You Still Have Not Been Whitelisted, Please Contact <@979191620610170950> Or <@664157606587138048>",
                    color=0xC5CE97,
                )
                await general_channel.send(f"{user.mention}", embed=embed)

                message_to_react = await whitelist_channel.fetch_message(
                    mc_ids[user.id][1]
                )
                await message_to_react.add_reaction("✅")

                console_channel = bot.get_channel(console_channel_id)
                await console_channel.send(f"whitelist add {mc_ids[user.id][0]}")
            else:
                embed = discord.Embed(
                    title="Player Whitelist",
                    description=f"## {user.mention} Has Not Been Whitelisted\n\nPlease Make Sure You Have Posted Your Minecraft ID In The {whitelist_channel.mention}",
                    color=0xC5CE97,
                )
                await general_channel.send(f"{user.mention}", embed=embed)
        else:
            embed = discord.Embed(
                title="Character Story Error",
                description=f"## {message.author.mention} Please Follow The Template \n Template Message : [Click Here](https://discord.com/channels/1220225199736094780/1261600104784334938/1261600740397551687)",
                color=0xC5CE97,
            )
            await general_channel.send(f"{message.author.mention}", embed=embed)

    # Qupix Whitelisting
    if message.channel.id == qupix_whitelist_channel_id:
        user = message.author
        mc_ids[user.id] = [message.content, message.id]

        qupix_character_channel = bot.get_channel(qupix_character_channel_id)
        user_found = False

        async for msg in qupix_character_channel.history(limit=20):
            if msg.author == user:
                user_found = True
                break

        if user_found:
            embed = discord.Embed(
                title="Player Whitelist",
                description=f"## {user.mention} Has Been Whitelisted\n\nIf You Still Have Not Been Whitelisted, Please Contact <@979191620610170950> Or <@664157606587138048>",
                color=0xC5CE97,
            )
            await qupix_general_channel.send(f"{user.mention}", embed=embed)

            message_to_react = await message.channel.fetch_message(mc_ids[user.id][1])
            await message_to_react.add_reaction("✅")

            console_channel = bot.get_channel(console_channel_id)
            await console_channel.send(f"whitelist add {mc_ids[user.id][0]}")
        else:
            embed = discord.Embed(
                title="Player Whitelist",
                description=f"## {user.mention} Has Not Been Whitelisted\n\nPlease Make Sure You Have Posted Your Character Name In The {qupix_character_channel.mention}",
                color=0xC5CE97,
            )
            await qupix_general_channel.send(f"{user.mention}", embed=embed)

    if message.channel.id == qupix_character_channel_id:
        if message.content.lower().startswith("character name"):
            user = message.author

            qupix_whitelist_channel = bot.get_channel(qupix_whitelist_channel_id)
            user_found = False

            async for msg in qupix_whitelist_channel.history(limit=20):
                if msg.author == user:
                    user_found = True
                    break

            if user_found:
                embed = discord.Embed(
                    title="Player Whitelist",
                    description=f"## {user.mention} Has Been Whitelisted\n\nIf You Still Have Not Been Whitelisted, Please Contact <@979191620610170950> Or <@664157606587138048>",
                    color=0xC5CE97,
                )
                await qupix_general_channel.send(f"{user.mention}", embed=embed)

                message_to_react = await qupix_whitelist_channel.fetch_message(
                    mc_ids[user.id][1]
                )
                await message_to_react.add_reaction("✅")

                console_channel = bot.get_channel(console_channel_id)
                await console_channel.send(f"whitelist add {mc_ids[user.id][0]}")
            else:
                embed = discord.Embed(
                    title="Player Whitelist",
                    description=f"## {user.mention} Has Not Been Whitelisted\n\nPlease Make Sure You Have Posted Your Minecraft ID In The {qupix_whitelist_channel.mention}",
                    color=0xC5CE97,
                )
                await qupix_general_channel.send(f"{user.mention}", embed=embed)
        else:
            embed = discord.Embed(
                title="Character Story Error",
                description=f"## {message.author.mention} Please Follow The Template \n Template Message : [Click Here](https://discord.com/channels/1220225199736094780/1261600104784334938/1261600740397551687)",
                color=0xC5CE97,
            )
            await qupix_general_channel.send(f"{message.author.mention}", embed=embed)


bot.run("MTI2NDg0OTU0ODMzNDA3MTgyOA.GeajgG.wH4Xg2aTX3AjIjF87D1MDDJsR7_sd-GhIYJJj8")
