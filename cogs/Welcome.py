import discord
from discord.utils import get
from discord.ext import commands
import sqlite3

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #Events
    @commands.Cog.listener()
    async def on_ready(self):
        print("Welcome Cog is being read")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.bot.get_channel(705565469108863027).send(f"( ͡° ͜ʖ ͡°)>⌐■-■ Welcome to the fam " + member.mention + " blah blam! ᕙ(▀̿̿Ĺ̯̿̿▀̿ ̿) ᕗ")
        print(f"{member} has joined the server.")
        db = sqlite3.connect("casino.sqlite")
        cursor = db.cursor()
        sql = "INSERT INTO players VALUES (?,?,?,?,?)"
        val = member.id, member.name, 5000, 0, 0
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await self.bot.get_channel(705565469108863027).send(f"( ͡° ͜ʖ ͡°)︻̷┻̿═━一- *pew pew* " + "**"+member.name+"**" + " has been executed!")
        print(f"{member} has left the server.")

def setup(bot):
    bot.add_cog(Welcome(bot))

