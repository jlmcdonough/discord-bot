import discord
from discord.utils import get
from discord.ext import commands
import lyricsgenius
import youtube_dl
import os
import ffmpeg


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.players = {}

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

    @commands.command(pass_context = True)
    async def join(self, ctx):
        channel = ctx.message.author.voice.channel
        await channel.connect()

    @commands.command(pass_context = True)
    async def leave(self, ctx):
        guild = ctx.message.guild
        voice_client = guild.voice_client
        await voice_client.disconnect()

    @commands.command(pass_context = True, hidden = True)
    async def play(self, ctx, url: str):

        song_there = os.path.isfile("song.mp3")
        try:
            if song_there:
                os.remove("song.mp3")
                print("Removed old song file")
        except PermissionError:
            print("Trying to delete song file, but it's being played")
            await ctx.send("ERROR: Music playing")
            return

        guild = ctx.message.guild
        voice_channel = guild.voice_client
        print(voice_channel)

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            print("Downloading audio now\n")
            ydl.download([url])

        for file in os.listdir("./"):
            if file.endswith(".mp3"):
                name = file
                print(f"Renamed File: {file}\n")
                os.rename(file, "song.mp3")

        ctx.voice_channel.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: print("Song done!"))
        voice_channel.source = discord.PCMVolumeTransformer(voice.source)
        voice_channel.source.volume = 0.07

        nname = name.rsplit("-", 2)
        await ctx.send(f"Playing: {nname[0]}")
        print("playing\n")


    @commands.command(pass_context = True, hidden = True)
    async def tplay(self, ctx):
        guild = ctx.message.guild
        voice_client = ctx.message.author.voice.channel
        print(guild, voice_client)
        discord.VoiceClient.play("https://www.youtube.com/watch?v=MbhXIddT2YY")
        #player = await voice_client.create_ytdl.player(url)
        #player[guild.id] = player
        #player.start()
def setup(bot):
    bot.add_cog(Music(bot))