# bot.py
import os
import random
import discord
from discord.ext import commands
from discord.utils import get
from dotenv import load_dotenv
from datetime import datetime
import sqlite3
import lyricsgenius
import youtube_dl
import sys
import ffmpeg


file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)


load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("DISCORD_GUILD")
VAULT_GUILD = os.getenv("DISCORD_VAULT_GUILD")

bot = commands.Bot(command_prefix = "~")

for filename in os.listdir("C:/Users/Joseph/PycharmProjects/discordBot/cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")

#load/unload cogs
@bot.command(hidden = True)
async def load(ctx, extension):
    bot.load_extension(f"cogs.{extension}")

@bot.command(hidden = True)
async def unload(ctx, extension):
    bot.unload_extension(f"cogs.{extension}")

#on events
@bot.event
async def on_ready():  #upon being started
    fp = open("C:/Users/Joseph/PycharmProjects/discordBot/peepoNotes.png", 'rb')
    pfp = fp.read()
    #await bot.user.edit(avatar=pfp)
    for guild in bot.guilds:
        if guild.name == GUILD:
            print(
                f"{bot.user} is connected to the following guild:\n"
                f"{guild.name}(id: {guild.id})\n"
            )

            members = "\n - ".join([member.name for member in guild.members])
            membersId =  ([member.id for member in guild.members])
            memberDict = {}
            for member in guild.members:
                memberDict[member.id] = member.name
            db = sqlite3.connect("C:/Users/Joseph/PycharmProjects/discordBot/casino.sqlite")
            cursor = db.cursor()
            cursor.execute("""
                            CREATE TABLE IF NOT EXISTS players(
                                playerID INT,
                                playerName TEXT,
                                moneyAmount INT,
                                winCount INT,
                                lossCount INT,
                                lastAllowance DATE
                                )
                            """)


            db = sqlite3.connect("C:/Users/Joseph/PycharmProjects/discordBot/casino.sqlite")
            cursor = db.cursor()

            ##Populate Table First Time
            for players in memberDict:
                sql = "INSERT INTO players VALUES (?,?,?,?,?,?)"
                val = players, memberDict[players], 25000, 0,0, None
                cursor.execute(sql, val)

            db.commit()
            cursor.close()
            db.close()

        if guild.name == VAULT_GUILD:
            print(
                f"{bot.user} is connected to the following guild:\n"
                f"{guild.name}(id: {guild.id})\n"
            )

            members = "\n - ".join([member.name for member in guild.members])
            membersId = ([member.id for member in guild.members])
            memberDict = {}
            for member in guild.members:
                memberDict[member.id] = member.name
            db = sqlite3.connect("C:/Users/Joseph/PycharmProjects/discordBot/vaultCasino.sqlite")
            cursor = db.cursor()
            cursor.execute("""
                            CREATE TABLE IF NOT EXISTS players(
                                playerID INT,
                                playerName TEXT,
                                moneyAmount INT,
                                winCount INT,
                                lossCount INT,
                                lastAllowance DATE
                                )
                            """)
            db = sqlite3.connect("C:/Users/Joseph/PycharmProjects/discordBot/vaultCasino.sqlite")
            cursor = db.cursor()

            #Populate Table First Time
            #for players in memberDict:
            #    sql = "INSERT INTO players VALUES (?,?,?,?,?,?)"
            #    val = players, memberDict[players], 25000, 0,0, None
            #    print("something")
            #    cursor.execute(sql, val)


            db.commit()
            cursor.close()
            db.close()

    await bot.change_presence(activity = discord.Activity(type=discord.ActivityType.watching, name = "~help for commands"))
@bot.event
async def on_member_join(member):
    role = get(member.guild.roles, name="plebs")
    await member.add_roles(role)
    print(member.name + " was given pleb role")

@bot.event
async def on_message(message):  #if certain words are typed, bot has a response
    if message.author == bot.user:
        return

    if ("cheat" in message.content.lower()):   #clown reaction for anyone calling cheats
        emoji = "\U0001F921"
        await message.add_reaction(emoji)

    if ("%?" in message.content.lower()):     #alternate to percentage command
        chance = random.randint(0, 101)
        response = "Joris says " + str(chance) + "% and he is never wrong"
        await message.channel.send(response)

    if ("jm" in message.content.lower()):
        goat = "\U0001F410"
        await message.add_reaction(goat)

    if (("tft" in message.content.lower()) or ("LoL" in message.content) or "urf" in message.content.lower()):
        vomit = "\U0001F92E"
        await message.add_reaction(vomit)

    #if (message.author.name == "Leahpar"):
    #   await message.channel.send("(☞ ͡° ͜ʖ ͡°)☞ ᵈᵒⁿᵗ ᵗᵃˡᵏᶦⁿᵍ ᵖˡᵉᵃˢᵉ")

    # if(message.author.name == "Eclipse"):
    #   await message.channel.send("now ᴘʟᴀʏɪɴɢ: Who asked (Feat: Nobody) ───────────:white_circle:────── ◄◄⠀▐▐⠀►► 𝟸:𝟷𝟾 / 𝟹:𝟻𝟼⠀───○ :loud_sound:")

    await bot.process_commands(message)


@bot.command(name = "Joris", help = "Gives with 100% accuracy the probability of a scenario", description = "")
async def joris(ctx):
    chance = random.randint(0, 101)
    response = "Joris says " + str(chance) + "% and he is never wrong"
    print("Joris")
    await ctx.send(response)

#DATABASE STUFF
def connectToDB():  #returns database and cursor pointer to games database
    db = sqlite3.connect("C:/Users/Joseph/PycharmProjects/discordBot/games.sqlite")
    cursor = db.cursor()
    return db, cursor

def closeDB(db, cursor):   #commits changes and closes database and cursor
    db.commit()
    cursor.close()
    db.close()

#Get any query from any table
@bot.command(name = "customQuery", help = "Result of any query (using SQL)", description = "")
async def customQuery(ctx, *query):
    db,cursor = connectToDB()
    print("query" + " ".join(query))
    cursor.execute(" ".join(query))
    result = cursor.fetchall()
    print("result" + str(result))
    closeDB(db,cursor)
    await ctx.send(result)


bot.run(TOKEN)

