import discord
from discord.ext import commands

import json
import re
import os

from keep_alive import keep_alive

intents = discord.Intents.default()
intents.message_content=True

bot = discord.Bot(intents=intents)

with open("config.json","r") as f:
    config = json.load(f)
    
bannedWords = config['bannedWords']
servers = config['servers']

@bot.event
async def on_ready():
    print("ready")
    print(servers)

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
    
@bot.event
async def on_message(message):
    msgAuth = message.author

    if bannedWords != None and (isinstance(message.channel, discord.channel.DMChannel) == False):
        for bannedWord in bannedWords:
            if bannedWord in message.content.lower():
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
    queryd = query.replace(" ", "+")
    search_url=f"https://www.google.com/search?q={queryd}"
    gogem = discord.Embed(title="Your results...",url=search_url)
    await ctx.send(gogem)

    
keep_alive()
bot.run(os.getenv('TOKEN'))

