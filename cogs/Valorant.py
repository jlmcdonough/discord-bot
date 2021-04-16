import discord
from discord.utils import get
from discord.ext import commands
import sqlite3
from datetime import datetime


class Valorant(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print("Valorant Cog is being read")

    # DATABASE STUFF
    def connectToDB(self):  # returns database and cursor pointer to games database
        db = sqlite3.connect("C:/Users/Joseph/PycharmProjects/discordBot/games.sqlite")
        cursor = db.cursor()
        return db, cursor

    def closeDB(self, db, cursor):  # commits changes and closes database and cursor
        db.commit()
        cursor.close()
        db.close()

    # Valorant Stats - table is the rank games were played at
    def getRank(self):  # since bot clears variable when going offline, currentRank table stores the current rank and keep track of rank ups/down
        db, cursor = self.connectToDB()
        query = cursor.execute("""SELECT rank
                                    FROM valCurrentRank
                                    WHERE changeDate IN (
                                        SELECT max(changeDate)
                                        FROM valCurrentRank);""")  # Gets the most recent rank
        result = cursor.fetchall()
        result = result[0][0]
        print(result)
        return str(result)  # sends the most recent rank to the match table so it knows which table to use

    @commands.command(name = "valGetRank",  help = "Gets current Valorant rank", description = "")
    async def valGetRank(self,ctx):
        response = "Current Rank: " + self.getRank()
        await ctx.channel.send(response)

    @commands.command(name = "valChangeRank",  help = "Change Valorant rank", description = "")
    async def valChangeRank(self, ctx, newRank):  # is what determines what table match data gets entered into
        db, cursor = self.connectToDB()
        now = datetime.now()
        sql = "INSERT INTO valCurrentRank VALUES (?,?)"
        val = newRank, now
        cursor.execute(sql, val)
        self.closeDB(db, cursor)
        await ctx.channel.send("rank updated you bot")

    @commands.command(name = "valAddMatch",  help = "Adds completed Valorant match", description = "")
    async def valAddMatch(self, ctx, mapPlayed, ourScore, theirScore, startingSide):
        db, cursor = self.connectToDB()
        valRank = self.getRank()  # calls getRank to go through currentRank table to get what the current rank is
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS """ + valRank + """(
                date CURRENT_TIMESTAMP,
                map TEXT,
                ourScore INT,
                theirScore INT,
                startingSide TEXT)
                """)
        ourScore = int(ourScore)
        theirScore = int(theirScore)
        now = datetime.now()
        sql = "INSERT INTO " + valRank + " VALUES (?,?,?,?,?)"
        val = now, mapPlayed, ourScore, theirScore, startingSide
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
        if (ourScore > theirScore):
            response = "wow, yall so good"
        elif (theirScore > ourScore):
            response = "damn, yall really lost to some silvers"
        elif (ourScore == theirScore):
            response = "shouldn't have lost that clutch smh"
        await ctx.channel.send(response)

def setup(bot):
    bot.add_cog(Valorant(bot))
