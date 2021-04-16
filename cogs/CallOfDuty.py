import discord
from discord.utils import get
from discord.ext import commands
import sqlite3
from datetime import datetime

class CallOfDuty(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #Events
    @commands.Cog.listener()
    async def on_ready(self):
        print("COD Cog is being read")

    # DATABASE STUFF
    def connectToDB(self):  # returns database and cursor pointer to games database
        db = sqlite3.connect("C:/Users/Joseph/PycharmProjects/discordBot/games.sqlite")
        cursor = db.cursor()
        return db, cursor

    def closeDB(self, db, cursor):  # commits changes and closes database and cursor
        db.commit()
        cursor.close()
        db.close()

    # COD Warzone Wins
    @commands.command(name = "codWin", help = "Adds Warzone win", description = "")
    async def codWin(self, ctx, eclipseK, eclipseD, jmK, jmD, leahparK, leahparD, quakeK, quakeD):
        def getKills():
            totalKills = int(eclipseK) + int(jmK) + int(leahparK) + int(quakeK)
            return totalKills

        def getDamage():
            totalDamage = int(eclipseD) + int(jmD) + int(leahparD) + int(quakeD)
            return totalDamage

        db, cursor = self.connectToDB()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS warzoneWins(
                date CURRENT_TIMESTAMP,
                eclipseK INT,
                eclipseD INT,
                jmK INT,
                jmD INT,
                leahparK INT,
                leahparD INT,
                quakeK INT,
                quakeD INT)
            ''')
        now = datetime.now()
        sql = "INSERT INTO warzoneWins VALUES (?,?,?,?,?,?,?,?,?)"
        val = now, eclipseK, eclipseD, jmK, jmD, leahparK, leahparD, quakeK, quakeD
        cursor.execute(sql, val)
        self.closeDB(db, cursor)

        response = ("```" +
                    "DATE: " + str(now.strftime("%m/%d/%Y %H:%M:%S")) +
                    '\n{:<5s}{:>7s}{:>10s}'.format("", "K", "D") +
                    '\n{:<5s}{:>7s}{:>10s}'.format('E', eclipseK, eclipseD) +
                    '\n{:<5s}{:>7s}{:>10s}'.format('J', jmK, jmD) +
                    '\n{:<5s}{:>7s}{:>10s}'.format('R', leahparK, leahparD) +
                    '\n{:<5s}{:>7s}{:>10s}'.format('V', quakeK, quakeD) +
                    '\n{:<5s}{:>7d}{:>10d}'.format('T', getKills(), getDamage()) + "```"
                    )

        await ctx.channel.send(response)

    @commands.command(name = "codGetLastWin", help = "Scoreboard of last Warzone win", description = "")
    async def codGetLastWin(self, ctx):
        db, cursor = self.connectToDB()
        cursor.execute("SELECT * FROM warzoneWins WHERE date = (SELECT MAX(date) FROM warzoneWins)")
        result = cursor.fetchall()
        query = []
        for i in range(0, 9):
            query.append(result[0][i])
        date = query[0]
        date = date.split(".")[0]
        totalK = query[1] + query[3] + query[5] + query[7]
        totalD = query[2] + query[4] + query[6] + query[8]
        response = ("```" +
                    "DATE: " + date +
                    '\n{:<5s}{:>7s}{:>10s}'.format("", "K", "D") +
                    '\n{:<5s}{:>7d}{:>10d}'.format('E', query[1], query[2]) +
                    '\n{:<5s}{:>7d}{:>10d}'.format('J', query[3], query[4]) +
                    '\n{:<5s}{:>7d}{:>10d}'.format('R', query[5], query[6]) +
                    '\n{:<5s}{:>7d}{:>10d}'.format('V', query[7], query[8]) +
                    '\n{:<5s}{:>7d}{:>10d}'.format('T', totalK, totalD) + "```"
                    )
        self.closeDB(db, cursor)
        print(response)
        await ctx.send(response)

    @commands.command(name = "codStats", help = "Total scoreboard of all Warzone wins", description = "")
    async def codStats(self, ctx):
        db, cursor = self.connectToDB()
        cursor.execute("SELECT * FROM warzoneWins")
        result = cursor.fetchall()
        query = []
        print(result[1])
        eK = 0
        eD = 0
        jK = 0
        jD = 0
        lK = 0
        lD = 0
        qK = 0
        qD = 0
        totalK = 0
        totalD = 0
        for j in range(len(result)):
            for k in range(1, 9):
                query.append(result[j][k])
        print(query)
        for x in range(0, len(query), 2):
            totalK += query[x]
        for y in range(1, len(query), 2):
            totalD += query[y]
        for a in range(0, len(query), 8):
            eK += query[a]
        for b in range(1, len(query), 8):
            eD += query[b]
        for c in range(2, len(query), 8):
            jK += query[c]
        for d in range(3, len(query), 8):
            jD += query[d]
        for e in range(4, len(query), 8):
            lK += query[e]
        for f in range(5, len(query), 8):
            lD += query[f]
        for g in range(6, len(query), 8):
            qK += query[g]
        for h in range(7, len(query), 8):
            qD += query[h]

        cursor.execute("SELECT COUNT(*) FROM warzoneWins")
        winTotal = cursor.fetchall()
        winTotal = winTotal[0][0]
        response = ("```" +
                    '\n{:<5s}{:>7s}{:>10s}'.format("", "K", "D") +
                    '\n{:<5s}{:>7d}{:>10d}'.format('E', eK, eD) +
                    '\n{:<5s}{:>7d}{:>10d}'.format('J', jK, jD) +
                    '\n{:<5s}{:>7d}{:>10d}'.format('R', lK, lD) +
                    '\n{:<5s}{:>7d}{:>10d}'.format('V', qK, qD) +
                    '\n{:<5s}{:>7d}{:>10d}'.format('T', totalK, totalD) +
                    "\n WIN COUNT: " + str(winTotal) + "```"
                    )
        self.closeDB(db, cursor)
        print(response)
        await ctx.send(response)

def setup(bot):
    bot.add_cog(CallOfDuty(bot))
