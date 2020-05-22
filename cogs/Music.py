import discord
from discord.utils import get
from discord.ext import commands
import lyricsgenius


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print("Music Cog is being read")

    def getSong(self, *song):
        i = 0
        track = []
        artist = []
        trackIncomplete = True
        while (i < (len(song))):
            if (song[i] != "by" and trackIncomplete):
                track.append(song[i])
                i += 1
            elif (song[i] == "by"):
                trackComplete = False
                i += 1
            elif (song[i] != "by" and not trackIncomplete):
                artist.append(song[i])
                i += 1

        trackStr = " ".join(track)
        artistStr = " ".join(artist)
        genius = lyricsgenius.Genius("ebRVz6hD0XyLfcyyjqXMfsIhWFHPY9ZIhj0eckmo61cf73OjZpbCaGL05eOg54xn")
        song = genius.search_song(trackStr, artistStr)
        return song

    @commands.command(name = "lyrics", help = "[Name of song] by [artist]", description = "Get the lyrics for the song")
    async def lyrics(self, ctx, *song):
        song = self.getSong(*song)
        song = song.lyrics
        await ctx.send(song)


    @commands.command(name = "lyricBreakdown", help = "[Name of song] by [artist]", description = "Get all words that appear more than once in a song")
    async def lyricBreakdown(self, ctx, *song):
        song = self.getSong(*song)
        song = song.lyrics
        song = list(song)
        for i in range(0, len(song)):
            if(song[i] == "["):
                while (song[i] != "]"):
                    song[i] = "|"
                    i += 1
            if(song[i] == "]"):
                song[i] = "|"
            if(song[i] == "\u2005"):
                song[i] = "|"
            if(song[i] == "\u205f"):
                song[i] = "|"
            if(song[i] == "\n"):
                song[i] = " "
        joinWithSpace = " "
        songString = joinWithSpace.join(song)
        songString = songString.replace("|", "")
        songString = songString.replace("  ", ">")
        songString = songString.replace(" ", "")
        songString = songString.replace(">", " ")
        songString = songString.replace(",", " ,")
        songString = songString.replace("?", " ,")
        songString = songString.replace("!", " ,")
        songString = songString.replace(".", " ,")
        word = ""
        wordList = []
        for j in range(0, len(songString)):
            if(songString[j] == " "):
                wordList.append(word.upper())
                word = ""
            else:
                word += songString[j]
        countList = []
        for k in wordList:
            if k not in countList:
                countList.append(k)

        finalList = dict()
        for i in range(0, len(countList)):
            if(countList[i] != "" or countList[i] == ","):
                finalList[countList[i]] = wordList.count(countList[i])
        a = sorted(finalList.items(), key = lambda x: x[1], reverse = True)
        response = "```"
        for elem in a:
            if(elem[1] > 2 and elem[0] != ","):
                response += "\n" + str(elem[0]) + " " + str(elem[1])
        response += "\n```"
        await ctx.send(response)

def setup(bot):
    bot.add_cog(Music(bot))