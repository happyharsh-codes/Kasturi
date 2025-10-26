from __init__ import*
import yt_dlp
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

class Muisk_and_Media(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
            client_id="SPOTIFY_CLIENT_ID",
            client_secret="SPOTIFY_CLIENT_SECRET"
        ))
        
    async def music_player(self, ctx, action):
        """Action can be pause, play, rewind, or skip"""
        em = Embed(color= Color.green())
        channel = 0
        player = []
        for i in MUSIC:
            if str(ctx.guild.id) in i:
                channel = i.split("_")[1]
                player = MUSIC[i]
        if action == "play":
            em.add_author(name= player[0]["name"], icon_url = player[0]["emoji"])
            em.title = f"▶️ Now Playing"
            em.description = f"[**{player[0]["name"]}**]({player[0]["link"]})"
            em.thumbnail(url= player[0]["thumbnail_url"])
        elif action == "stop":
            em.add_author(name= player[0]["name"], icon_url= player[0]["emoji"])
            em.title = "⏸️ Stopped Playing"
            em.description = f"Last playing: [**{player[0]["name"]}**]({player[0]["link"]})"
        elif action == "rewind":
            em.add_author(name= player[0]["name"], icon_url= player[0]["emoji"])
            em.title = f"⏮️ Song Rewinded"
            em.description = f"[**{player[0]["name"]}**]({player[0]["link"]})"
            em.thumbnail(url= player[0]["thumbnail_url"])
            em.set_footer(f"Rewinded by {ctx.author.display_name}", icon_url= ctx.author.avatar)
        elif action == "skip":
            pass
        await ctx.send(embed=em)

    def search_spotify(self, track):
        results = self.sp.search(track,limit=1, type= "track")
        track = {"name": "", "link": "", "thumbnail_url": "", "emoji": "spotify", "audio": ""}
        tracks = results["track"]["items"][0]:
        if tracks:
            track["name"] = tracks["name"]
            track["link"] = tracks["external_urls"]["spotify"]
            track["thumbnail_url"] = tracks["album"]["images"][0]["url"]
            
        else:
            return self.search_yt(track)
    def search_yt(self, track):
        track = {"name": "", "link": "", "thumbnail_url": "", "emoji": "spotify"}
        
        pass
    def search_songcloud(self, track):
        track = {"name": "", "link": "", "thumbnail_url": "", "emoji": "spotify"}
        
        pass
    
    @commands.command(aliases=["p"])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def play(self, ctx, search):
        """Plays the Song music 🎶 on your VC"""
        #Joining Vc
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.reply("You must be in a voice channel to run this command", delete_after= 12)
            return
        channel = ctx.author.voice.channel
        #checking perms
        permissions = channel.permissions_for(ctx.guild.me)
        if not permissions.connect:
            await ctx.reply("I do not have permissions to join this channel. Please try again in another channel.", delete_after = 12)
            return
        if not permissions.speak:
            await ctx.reply("I do not have permissions to speak in this channel. Please join another channel and try again", delete_after = 12)
            return
        voice_client = ctx.guild.voice_client
        if voice_client:
            await voice_client.move_to(channel)
        else:
            voice_client = await channel.connect()
            for i in MUSIC:
                if str(ctx.guild.id) in i:
                    MUSIC.pop(i)
                    break
        

    @commands.command(aliases=["q"])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def queue(self, ctx):
        """Shows the songs queue list 🎵"""
        await ctx.send("This command is yet to be made :/")

    @commands.command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def skip(self, ctx):
        """Skips the current playing song. Requires voting from all vc members."""
        pass

    @commands.command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def stop(self, ctx):
        """Stops playing the current song. Requires voting from all vc members."""
        pass
        
async def setup(bot):
    await bot.add_cog(Muisk_and_Media(bot))
    print("Loaded cogs: MusikMedia")
