import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions, BadArgument
from discord.ui import Button, View

import json
import aiosqlite
import re
import os

from keep_alive import keep_alive

intents = discord.Intents.default()
intents.message_content=True
intents.members=True

bot = discord.Bot(intents=intents)

with open("config.json","r") as f:
    config = json.load(f)
    
bannedWords = config['bannedWords']
servers = config['servers']

@bot.event
async def on_ready():
    print("ready")
    print(servers)
    async with aiosqlite.connect("main.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute('CREATE TABLE IF NOT EXTSTS users (')

@bot.slash_command(
    name="banword",
    description="ban a word",
    guild_ids=servers
)
@commands.has_permissions(administrator=True)
async def addbannedword(ctx,word):
    if word.lower() in bannedWords:
        await ctx.respond("This word is already banned")
    else:
        bannedWords.append(word.lower())

        with open("config.json","r+") as f:
            data = json.load(f)
            data["bannedWords"] = bannedWords
            f.seek(0)
            f.write(json.dumps(data))
            f.truncate

        await ctx.respond("This word is now banned")

@bot.slash_command(
    name="unbanword",
    description="Unbans a word - admin use only!",
    guild_ids=servers
)
@commands.has_permissions(administrator=True)
async def removebannedword(ctx,word):
    if word.lower() in bannedWords:
        bannedWords.remove(word.lower())

        with open("config.json","r") as f:
            data = json.load(f)
            data["bannedWords"] = bannedWords
            print(bannedWords, data)
        with open("config.json","w") as f:
            json.dump(data,f)

        await ctx.respond(f"'{word}' is now unbanned")
        
    else:
        await ctx.respond("this word isn't banned")

@addbannedword.error
async def ban_error(ctx, error):
    if isinstance(error, BadArgument):
        await ctx.respond("Please specify a **valid** user!",ephemeral=True)
    elif isinstance(error, MissingPermissions):
        await ctx.respond("You need the **administrator** permission!",ephemeral=True)
    else:
        raise error

@removebannedword.error
async def ban_error(ctx, error):
    if isinstance(error, BadArgument):
        await ctx.respond("Please specify a **valid** user!",ephemeral=True)
    elif isinstance(error, MissingPermissions):
        await ctx.respond("You need the **administrator** permission!",ephemeral=True)
    else:
        raise error

def convert(lst):
    return (lst[0].split())

@bot.event
async def on_message(message):
    msgAuth = message.author
    listmsg = []
    listmsg.append(message.content.lower())
    msgc = convert(listmsg)
    
    if bannedWords != None and (isinstance(message.channel, discord.channel.DMChannel) == False):
        for bannedWord in bannedWords:
            for word in msgc:
                if bannedWord == word:
                    print(f"{msgAuth} said a banned word")
                    await message.delete()
                    await message.channel.send(f"{msgAuth.mention} your message was removed as it contained a banned word")

    await bot.process_application_commands(message)

@bot.slash_command(
    name="google",
    description="google something... right here!",
    guild_ids=servers
)
async def google(ctx,query):
    for bannedWord in bannedWords:
        if query in bannedWord or bannedWord in query:
            await ctx.respond("You can't google a banned word!",ephemeral=True)
            return

    queryd = query.replace(" ", "+")
    search_url=f"https://www.google.com/search?q={queryd}"

    results = Button(
        style = discord.ButtonStyle.link,
        label = "Search Results",
        url = search_url
    )

    view = View()
    view.add_item(results)
    
    gogem = discord.Embed(title=f"Search results for '{query}'",description="Click the button below to go to your results!",color=0x00ffff)

    await ctx.respond(embed=gogem,view=view)

@bot.slash_command(
    name="init",
    description="Subscribe to the slash commands - admin use only!",
    guild_ids=servers
)
@commands.has_permissions(administrator=True)
async def sub(ctx):
    embed = discord.Embed(title="Subscribe!",description="Subscribe to Sir Aramis' slash commands!")
    sub = Button(
        label="Subscribe",
        style=discord.ButtonStyle.success
    )
    nvm = Button(
        label="Nevermind",
        style=discord.ButtonStyle.grey
    )
    vay = Button(
        label="Shuddup",
        style=discord.ButtonStyle.danger
    )

    async def sub_callback(interaction):
        guiID = ctx.guild.id
        print(guiID,"Subbed!")

        with open("config.json","r") as f:
            data = json.load(f)
            guild_id = data['servers'].append(guiID)
            print(data,guild_id)
        
        await interaction.response.send_message("Congrats! You have subscribed to my slash commands!")
    async def nvm_callback(interaction):
        await interaction.response.send_message("You can always subscribe to my slash commands by running /init again!")
        return
    async def vay_callback(interaction):
        await interaction.response.send_message("Ok")
        return

    sub.callback = sub_callback
    nvm.callback = nvm_callback
    vay.callback = vay_callback
    
    view = View()
    view.add_item(sub)
    view.add_item(nvm)
    view.add_item(vay)

    await ctx.respond(embed=embed,view=view)



keep_alive()
bot.run(os.getenv('TOKEN'))

