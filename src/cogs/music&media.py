from __init__ import*
import yt_dlp
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import sclib
import lyricsgenius 

class Musik_and_Media(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
            client_id= os.getenv("SPOTIFY_ID"),
            client_secret= os.getenv("SPOTIFY_SECRET")
        ))
        self.player = {}
        self.current_track = {}# keeps track of current music, current music player message and no of users voted.

    async def play_next(self, ctx):
        if str(ctx.guild.id) not in self.player:
            await ctx.send(embed = Embed(title= "Queue Finished | Leaving VC . . ."))
            self.current_track.pop(str(ctx.guild.id), None)
            return
        music = self.player[str(ctx.guild.id)].pop(0)
        self.current_track[str(ctx.guild.id)]["music"] = music
        if self.player[str(ctx.guild.id)] == []:
            self.player.pop(str(ctx.guild.id), None)
        em = Embed(color= Color.green())
        em.set_author(name= "▶️ Now Playing")
        em.title = f"{music["emoji"]} {music["title"]}"
        em.url = music["link"]
        em.description = f"**Artists**: {",".join(music["artists"])}\n**Duration**: {music["duration"]}"
        em.set_thumbnail(url= music["thumbnail_url"])
        msg = await ctx.send(embed= em)
        await msg.add_reaction("⏮️")
        await msg.add_reaction("⏸️")
        if str(ctx.guild.id) in self.player:
            await msg.add_reaction("⏭️")
        self.current_track[str(ctx.guild.id)]["msg_id"] = msg.id
        #start streaming
        ffmpeg_options = {
        'before_options': "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        'options': "-vn"
        }
        try:
            source = await discord.FFmpegOpusAudio.from_probe(music["audio_url"], **ffmpeg_options)
            voice = ctx.voice_client
            voice.play(source, after= lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), ctx.bot.loop))
        except Exception as e:
            await ctx.send("Unexpected error: Music Player stopped working", delete_after=30)
            await ctx.bot.get_user(894072003533877279).send(f"Error in music player: {e}")
            
    async def music_player(self, ctx, action):
        """Action can be pause, play, rewind, or skip"""
        em = Embed(color= Color.green())
        channel = 0
        player = []
        music = self.player.get(str(ctx.guild.id), None)
        if action == "▶️":
            music = self.current_track[str(ctx.guild.id)]["music"]
            em.set_author(name= "▶️ Now Playing")
            em.title = f"{music["emoji"]} {music["title"]}"
            em.url = music["link"]
            em.description = f"**Artists**: {",".join(music["artists"])}\n**Duration**: {music["duration"]}"
            em.set_thumbnail(url= music["thumbnail_url"])
            em.set_footer(f"Resumed by {ctx.author.display_name}", icon_url= ctx.author.avatar)
            if ctx.voice_client.is_paused():
                ctx.voice_client.resume()
        elif action == "⏸️":
            music = self.current_track[str(ctx.guild.id)]["music"]
            em.set_author(name="⏸️ Stopped Playing")
            em.title = f"{music["emoji"]} {music["title"]}"
            em.url = music["link"]
            em.color = Color.red()
            em.set_thumbnail(url= music["thumbnail_url"])
            em.set_footer(f"Paused by {ctx.author.display_name}", icon_url= ctx.author.avatar)
            if ctx.voice_client and ctx.voice_client.is_playing():
                ctx.voice_client.pause()
        elif action == "⏮️":
            music = self.current_track[str(ctx.guild.id)]["music"]
            em.color = Color.dark_gold()
            em.set_author(name= f"⏮️ Song Rewinded")
            em.title = f"{music["emoji"]} {music["title"]}"
            em.url = music["link"]
            em.description = f"**Artists**: {",".join(music["artists"])}\n**Duration**: {music["duration"]}"
            em.set_thumbnail(url= music["thumbnail_url"])
            em.set_footer(f"Rewinded by {ctx.author.display_name}", icon_url= ctx.author.avatar)
            self.player[str(ctx.guild.id)].insert(0, music)
            ctx.voice_client.stop()
        elif action == "⏭️":
            if not str(ctx.guild.id) in self.player:
                await ctx.send("Can't Skip this is the last song")
                return
            self.player[str(ctx.guild.id)].pop(0)
            music = self.current_track[str(ctx.guild.id)]["music"]
            em.color = Color.dark_gold()
            em.set_author(name= f"⏭️ Song Skipped")
            em.title = f"{music["emoji"]} {music["title"]}"
            em.url = music["link"]
            em.description = f"**Artists**: {",".join(music["artists"])}\n**Duration**: {music["duration"]}"
            em.set_thumbnail(url= music["thumbnail_url"])
            em.set_footer(f"Skipped by {ctx.author.display_name}", icon_url= ctx.author.avatar)
            ctx.voice_client.stop()
        elif action == "📝":
            async with ctx.typing():
                try:
                    lyrics = GENIUS.search_song(self.current_track[str(ctx.guild.id)]["music"]["title"])
                    await ctx.send(f"**Lyrics for {lyrics.title}**\n```{lyrics.lyrics[:1900]}```")
                except:
                    await ctx.send("Couldn't get any lyrics for this song")
        try:
            msg = await ctx.channel.fetch_message(self.current_track["msg_id"])
            if action != "📝":
                await msg.edit(embed= em)
            await msg.clear_reactions()
            await msg.add_reaction("⏮️")
            if ctx.voice_client.is_paused():
                await msg.add_reaction("▶️")
            else:
                await msg.add_reaction("⏸️")
            if action != "📝":
                await msg.add_reaction("📝")
            if str(ctx.guild.id) in self.player:
                await msg.add_reaction("⏭️")
        except: pass
        
    def search_song(self, track_name):
        results = self.sp.search(track_name ,limit=1, type= "track")
        track = {"title": "", "artists": [], "duration": "0:0",  "link": "", "thumbnail_url": "", "emoji": "<:spotify:1432179988647645336>", "audio_url": ""}
        tracks = results["tracks"]["items"][0]
        ydl_opts = {
            "format": "bestaudio/best",
            "nonplaylist": True,
            "quiet": True,
            "default_search": "ytsearch",
            "cookiefile": "assets//cookie.txt"
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
            if str(ctx.guild.id) in self.player:
                self.player.pop(str(ctx.guild.id))

        music_track = self.search_song(search)
        if not music_track:
            em = Embed(title= "Unable to Find song", description= "We are unable to find any song with the given name 😔 anywhere on Spotify, Youtube, SoundCloud, etx. Please forgive us and try again using more specific name", color = Color.greyple())
            await ctx.send(embed=em)
            return
        estimated_time = 0
        if str(ctx.guild.id) in self.player:
            duration = self.current_track[str(ctx.guild.id)]["music"]["duration"]
            seconds = (int(duration.split(":")[0])*60) + int(duration.split(":")[1])
            for song in self.player[str(ctx.guild.id)]:
                duration = song["duration"]
                seconds += (int(duration.split(":")[0])*60) + int(duration.split(":")[1])
            estimated_time = f"{seconds//60}:{seconds%60}"
        else:
            estimated_time = "0:0"
        em = Embed(title="🎶 Song Added in Queue", description= f"[**{music_track["title"]}**]({music_track["link"]})\n**Artist**: {",".join(music_track["artists"])}\n**Duration**: {music_track["duration"]}\n**Estimated time before playing**: {estimated_time}", color = Color.purple())
        em.set_author(name= ctx.author.name, icon_url= ctx.author.avatar)
        em.set_footer(text= f"Song added by {ctx.author.name} | At {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')}" , icon_url= ctx.author.avatar)
        em.set_thumbnail(url= music_track["thumbnail_url"])
        await ctx.send(embed= em)
        if str(ctx.guild.id) in self.player:
            self.player[str(ctx.guild.id)].append(music_track)
        else:
            self.player[str(ctx.guild.id)] = [music_track]
            await self.play_next(ctx)

    @commands.command(aliases=["q"])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def queue(self, ctx):
        """Shows the songs queue list 🎵"""
        em = Embed(title = "🎶 Upcoming Playlist 🎶", description = "\n".join([f"[**{song["title"]}**]({song["link"]}) - {song["duration"]}" for song in self.player[str(ctx.guild.id)] ]), color = Color.purple())
        em.set_footer(text= f"Requested by {ctx.author.name} | At {datetime.now(UTC).strftime('%m-%d %H:%M')}" , icon_url= ctx.author.avatar)
        await ctx.send(embed = em)
    
    @commands.command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def skip(self, ctx):
        """Skips the current playing song. Requires voting from all vc members."""
        music = self.current_track.get(str(ctx.guild.id), None)
        for m in ctx.voice_client.channel.members:
            if m.id == ctx.author.id:
                break
        else:
            await ctx.send(embed= Embed(description="You are not in a voice channel.", color=Color.red()))
            return
        if not music:
            await ctx.send("No Track is being played currently.")
            return
        em = Embed(color= Color.green())
        em.set_author(name= "▶️ Now Playing")
        em.title = f"{music["emoji"]} {music["title"]}"
        em.url = music["link"]
        em.description = f"**Artists**: {",".join(music["artists"])}\n**Duration**: {music["duration"]}"
        em.set_thumbnail(url= music["thumbnail_url"])
        msg = await ctx.send(embed=em)
        await ctx.send("React with controller buttons to interact with music player.", delete_after= 3)
        await msg.add_reaction("⏮️")
        await msg.add_reaction("⏸️")
        await msg.add_reaction("📝")
        await msg.add_reaction("⏭️")
        self.current_track[str(ctx.guild.id)]["msg_id"] = msg.id

    @commands.command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def stop(self, ctx):
        """Stops playing the current song. Requires voting from all vc members."""
        for m in ctx.voice_client.channel.members:
            if m.id == ctx.author.id:
                break
        else:
            await ctx.send(embed= Embed(description="You are not in a voice channel.", color=Color.red()))
            return
        music = self.current_track.get(str(ctx.guild.id), None)
        if not music:
            await ctx.send("No Track is being played currently.")
            return
        em = Embed(color= Color.green())
        em.set_author(name= "▶️ Now Playing")
        em.title = f"{music["emoji"]} {music["title"]}"
        em.url = music["link"]
        em.description = f"**Artists**: {",".join(music["artists"])}\n**Duration**: {music["duration"]}"
        em.set_thumbnail(url= music["thumbnail_url"])
        msg = await ctx.send(embed=em)
        await ctx.send("React with controller buttons to interact with music player.", delete_after= 3)
        await msg.add_reaction("⏮️")
        await msg.add_reaction("⏸️")
        await msg.add_reaction("📝")
        await msg.add_reaction("⏭️")
        self.current_track[str(ctx.guild.id)]["msg_id"] = msg.id


    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if str(payload.guild_id) not in self.current_track:
            return 
        if payload.message_id != self.current_track[str(payload.guild_id)]["msg_id"]:
            return
        guild = self.client.get_guild(payload.guild_id)
        channel = self.client.get_channel(payload.channel_id)
        for member in guild.voice_client.channel.members:
            if member.id == payload.user_id:
                msg = await channel.fetch_message(self.current_track[str(guild.id)]["msg_id"])
                ctx = await self.client.get_context(msg)
                members_count = len([m for m in guild.voice_client.channel.members])
                required = ceil(0.7 * members_count)
                if "⏸️" in str(payload.emoji):
                    try:
                        self.current_track[str(guild.id)]["pause_voters"] += 1
                    except:
                        self.current_track[str(guild.id)]["pause_voters"] = 1
                    if self.current_track[str(guild.id)]["pause_voters"] >= required:
                        await self.music_player(ctx, str(payload.emoji))
                    else:
                        await ctx.send(embed=Embed(description= f"Pausing, **{self.current_track[str(guild.id)]["pause_voters"]}**/**{members_count}** (**{required}** Votes required)"))
                    
                elif "⏮️" in str(payload.emoji):
                    try:
                        self.current_track[str(guild.id)]["rewind_voters"] += 1
                    except:
                        self.current_track[str(guild.id)]["rewind_voters"] = 1
                    if self.current_track[str(guild.id)]["rewind_voters"] >= required:
                        await self.music_player(ctx, str(payload.emoji))
                    else:
                        await ctx.send(embed=Embed(description= f"Rewinding, **{self.current_track[str(guild.id)]["rewind_voters"]}**/**{members_count}** (**{required}** Votes required)"))
                    
                elif "⏭️" in str(payload.emoji):
                    try:
                        self.current_track[str(guild.id)]["skip_voters"] += 1
                    except:
                        self.current_track[str(guild.id)]["skip_voters"] = 1
                    if self.current_track[str(guild.id)]["skip_voters"] >= required:
                        await self.music_player(ctx, str(payload.emoji))
                    else:
                        await ctx.send(embed=Embed(description= f"Skipping, **{self.current_track[str(guild.id)]["skip_voters"]}**/**{members_count}** (**{required}** Votes required)"))
                else:
                    await self.music_player(ctx, str(payload.emoji))         
                return
        else:
            return

            
async def setup(bot):
    await bot.add_cog(Musik_and_Media(bot))
    print("Loaded cogs: MusikMedia")
