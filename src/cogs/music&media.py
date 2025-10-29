from __init__ import*
import yt_dlp
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import sclib

class Muisk_and_Media(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
            client_id="SPOTIFY_CLIENT_ID",
            client_secret="SPOTIFY_CLIENT_SECRET"
        ))
        self.player = {}

    async def play_next(self, ctx):
        if str(ctx.guild.id) not in self.player:
            await ctx.send(embed = Embed(title= "Queue Finished | Leaving VC . . ."))
            return
        music = self.player[str(ctx.guild.id)].pop(0)
        em = Embed(color= Color.green())
        em.add_author(name= "▶️ Now Playing")
        em.title = f"{music["emoji"]} {music["title"]}"
        em.url = music["link"]
        em.description = f"**Artists**: {",".join(music["artists"])}\n**Duration**: {music["duration"]}"
        em.thumbnail(url= music["thumbnail_url"])
        await ctx.send(embed= em)
        #start streaming
        ffmpeg_options = {
        'before_options': "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        'options': "-vn"
        }
        try:
            source = await discord.FFmpegOpusAudio.from_probe(music["audio_url"], **fmpeg_options)
            voice = ctx.voice_client
            voice.play(source, after= lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), ctx.bot.loop))
        except Exceptions as e:
            await ctx.send("Unexpected error: Music Player stopped working", delete_after=30)
            await ctx.bot.get_user(894072003533877279).send(f"Error in music player: {e}")
            
    async def music_player(self, ctx, action):
        """Action can be pause, play, rewind, or skip"""
        em = Embed(color= Color.green())
        channel = 0
        player = []
        music = self.player.get(str(ctx.guild.id), None)
        if not music:
            return
        if action == "play":
            await self.play_next(ctx)
        elif action == "stop":
            music = music[0]
            em.add_author(name="⏸️ Stopped Playing")
            em.title = f"{music["emoji"]} {music["title"]}"
            em.url = music["link"]
            em.color = Color.red()
            if ctx.voice_client:
                await ctx.voice_client.disconnect()
            self.player.pop(str(ctx.guild.id))
        elif action == "rewind":
            music = music[0]
            em.color = Color.dark_gold()
            em.add_author(name= f"⏮️ Song Rewinded")
            em.title = f"{music["emoji"]} {music["title"]}"
            em.url = music["link"]
            em.description = f"**Artists**: {",".join(music["artists"])}\n**Duration**: {music["duration"]}"
            em.thumbnail(url= music["thumbnail_url"])
            em.set_footer(f"Rewinded by {ctx.author.display_name}", icon_url= ctx.author.avatar)
        elif action == "skip":
            music.pop(0)
            if music == []:
                self.player.pop(str(ctx.guild.id))
            else:
                self.player[str(ctx.guild.id)] = music
            music = music[0]
            em.color = Color.dark_gold()
            em.add_author(name= f"⏭️ Song Skipped")
            em.title = f"{music["emoji"]} {music["title"]}"
            em.url = music["link"]
            em.description = f"**Artists**: {",".join(music["artists"])}\n**Duration**: {music["duration"]}"
            em.thumbnail(url= music["thumbnail_url"])
            em.set_footer(f"Skipped by {ctx.author.display_name}", icon_url= ctx.author.avatar)
            await ctx.voice_client.stop()
            
        await ctx.send(embed=em)
        
        
    def search_song(self, track_name):
        results = self.sp.search(track_name ,limit=1, type= "track")
        track = {"title": "", "artists": [], "duration": "0:0",  "link": "", "thumbnail_url": "", "emoji": "<:spotify:1432179988647645336>", "audio_url": ""}
        tracks = results["track"]["items"][0]
        ydl_opts = {
            "format": "bestaudio/best",
            "nonplaylist": True,
            "quiet": True,
            "default_search": "ytsearch"
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(track_name, download=False)["entries"][0]
            track["audio_url"] = info["url"]
            track["thumbnail_url"] = info.get("thumbnail", None)
            duration = info["duration"]
            track["duration"] = f"{duration//60}:{duration%60}"
        if tracks:
            for artist in tracks["artists"]:
                track["artists"].append(artist["name"])
            track["title"] = f"{tracks["name"]} - {",".join(track["artists"])}"
            track["link"] = tracks["external_urls"]["spotify"]
            if not track["thumbnail_url"]:
                track["thumbnail_url"] = tracks["album"]["images"][0]["url"]
        else:
            track["emoji"] = "<:youtube:1432179973367533578>"
            track["title"] = info["title"]
            track["artists"] = info["artists"]
            track["link"] = info["webpage_url"]

        return track

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
            self.player.pop(str(ctx.guild.id))

        music_track = self.search_song(search)
        if not music_track:
            em = Embed(title= "Unable to Find song", description= "We are unable to find any song with the given name 😔 anywhere on Spotify, Youtube, SoundCloud, etx. Please forgive us and try again using more specific name", color = Color.greyple())
            await ctx.send(embed=em)
            return
        estimated_time = "0:0"
        em = Embed(title="🎶 Song Added in Queue", description= f"[**{music_track["title"]}**]({music_track["link"]})\n**Artist**: {",".join(music_track["artists"])}\n**Duration**: {music_track["duration"]}\n**Estimated time before playing**: {estimated_time}", color = Color.purple())
        em.set_author(name= ctx.author.name, icon_url= ctx.author.avatar)
        em.set_footer(text= f"Song added by {ctx.author.name} | At {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')}" , icon_url= ctx.author.avatar)
        em.set_thumbnail(url= music_track["thumbnail_url"])
        await ctx.send(embed= em)
        if str(ctx.guild.id) in self.player():
            self.player[str(ctx.guild.id)].append(music_track)
            #await self.music_player(ctx, "playafter")
        else:
            self.player[str(ctc.guild.id)] = [music_track]
            await self.music_player(ctx, "play")

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
