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

    async def send_player(self, ctx, music):
        em = Embed(color= Color.green())
        em.set_author(name= "▶️ Now Playing")
        em.title = f"{music['emoji']} {music['title']}"
        em.url = music["link"]
        em.description = f"**Artist**: {music['artists'][0])}\n**Duration**: {music['duration']}"
        em.set_thumbnail(url= music["thumbnail_url"])
        em.set_footer(text= ". Operate Music Player with buttons")
        
        pause = Button(style=ButtonStyle.secondary, custom_id="pause", label="⏸️")
        play = Button(style=ButtonStyle.secondary, custom_id="play", label="▶️", disabled = True)
        rewind = Button(style=ButtonStyle.secondary, custom_id="rewind", label="⏮️")
        skip = Button(style=ButtonStyle.secondary, custom_id="skip", label="⏭️")
        lyrics = Button(style=ButtonStyle.secondary, custom_id="lyrics", label="📝")

        pause.callback = self.music_player
        play.callback = self.music_player
        rewind.callback = self.music_player
        skip.callback = self.music_player
        lyrics.callback = self.music_player
        
        view = View(timeout=20)
        async def on_timeout():
            nonlocal msg
            await msg.edit(view=None)
        view.on_timeout = timeout
        view.add_item(rewind)
        view.add_item(pause)
        view.add_item(play)
        view.add_item(lyrics)
        view.add_item(skip)
        
        msg = await ctx.send(embed= em, view= view)
        
    async def play_next(self, ctx, start = False):
        if len([m for m in ctx.voice_client.channel.members]) == 0:
            await ctx.send(embed = Embed(description= "No listeners leaving VC..."))
            try: 
                self.player.pop(str(ctx.guild.id))
                await ctx.voice_client.disconnect()
            except:
                pass
            return
        if not start:
            self.player[str(ctx.guild.id)].pop(0)
        if self.player[str(ctx.guild.id)] == []:
            await ctx.send(embed = Embed(title= "Queue Finished \nLeaving VC . . ."),color = Color.dark_gold())
            return
            
        #sending music player
        music = self.player[str(ctx.guild.id)][0]
        await self.send_player(ctx, music)
        
        #start streaming
        ffmpeg_options = {
        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -protocol_whitelist file,http,https,tcp,tls,crypto",
        "options": "-vn -af volume=1.0"
        }
        
        try:
            source = await discord.FFmpegOpusAudio.from_probe(music["audio_url"], **ffmpeg_options)
            voice = ctx.voice_client
            if not voice:
                await ctx.send(embed= Embed(title="No voice channel connected, stopped playing"))
                try:
                    self.player.pop(str(ctx.guild.id))
                except:
                    pass
                return 
            voice.play(source, after= lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), ctx.bot.loop))
        except Exception as e:
            await ctx.send("Unexpected error: Music Player stopped working", delete_after=30)
            await ctx.bot.get_user(894072003533877279).send(f"Error in music player: {e}")
    
    async def music_player(self, interaction: Interaction):
        if not str(interaction.guild_id) in self.player:
            return
        music = self.player[str(interaction.guild_id)][0]
        pressed = interaction.data["custom_id"]
        em = interaction.message.embeds[0]

        voice_client = interaction.guild.voice_client
        if not voice_client:
            return
        if not interaction.user.voice.channel.id != voice_client.channel.id:
            return
            
        member_count = len([m for m in voice_client.channel.members]) - 1#for own
        majority = ceil(0.7 * member_count)
        voted = 0
        description = interaction.message.embeds[0].description.lower()

        view = View(timeout=20)
        async def on_timeout():
            await interaction.response.edit_message(view=None)
        view.on_timeout = on_timeout
        
        pause = Button(style=ButtonStyle.secondary, custom_id="pause", label="⏸️")
        play = Button(style=ButtonStyle.secondary, custom_id="play", label="▶️", disabled = True)
        rewind = Button(style=ButtonStyle.secondary, custom_id="rewind", label="⏮️")
        skip = Button(style=ButtonStyle.secondary, custom_id="skip", label="⏭️")
        lyrics = Button(style=ButtonStyle.secondary, custom_id="lyrics", label="📝")

        pause.callback = self.music_player
        play.callback = self.music_player
        rewind.callback = self.music_player
        skip.callback = self.music_player
        lyrics.callback = self.music_player

        view.add_item(rewind)
        view.add_item(pause)
        view.add_item(play)
        view.add_item(lyrics)
        view.add_item(skip)
        
        if pressed == "pause":
            if "pause_voters" in music:
                voted = music["pause_voters"] + 1
                self.player[str(interaction.guild_id)][0]["pause_voters"] += 1
            else:
                self.player[str(interaction.guild_id)][0]["pause_voters"] = 1
                voted = 1
            if voted >= majority:  
                em.set_author(name="▶️ Song Paused")
                em.set_footer(name=f"Paused by **{voted}**/**{member_count}**")
                await voice_client.pause()
                pause.disabled = True
                play.disabled = False
            else:
                em.description = f"\nPausing, **{voted}**/**{member_count}** (**{majority}** votes required)"
        elif pressed == "play":
            await voice_client.play()
            pause.disabled = False
            play.disabled = True 
        elif pressed == "rewind":
            if "rewind_voters" in music:
                voted = music["rewind_voters"] + 1
                self.player[str(interaction.guild_id)][0]["rewind_voters"] += 1
            else:
                self.player[str(interaction.guild_id)][0]["rewind_voters"] = 1
                voted = 1
            if voted >= majority:  
                em.set_author(name="⏮️ Song Rewinded")
                em.set_footer(name=f"Rewinded by **{voted}**/**{member_count}**")
                self.player[str(interaction.guild_id)].insert(1, music)
                await voice_client.stop()
                rewinded.disabled = True
            else:
                em.description = f"\nRewinding, **{voted}**/**{member_count}** (**{majority}** votes required)"
        
        elif pressed == "skip":
            if "skip_voters" in music:
                voted = music["skip_voters"] + 1
                self.player[str(interaction.guild_id)][0]["skip_voters"] += 1
            else:
                self.player[str(interaction.guild_id)][0]["skip_voters"] = 1
                voted = 1
            if voted >= majority:  
                em.set_author(name="⏭️ Song Skipped")
                em.set_footer(name=f"Skipped by **{voted}**/**{member_count}**")
                await voice_client.stop()
                pause.disabled = True
                rewind.disabled = True
                skip.disabled = True
                lyrics.disabled = True
            else:
                em.description = f"\nSkipping, **{voted}**/**{member_count}** (**{majority}** votes required)"
        
        elif pressed == "lyrics";
            async with ctx.typing():
                try:
                    lyrics = GENIUS.search_song(music['title'])
                    await interaction.message.channel.send(f"**Lyrics for {lyrics.title}**\n```{lyrics.lyrics[:1900]}```")
                except:
                    await ctx.send("Couldn't get any lyrics for this song")
            lyrics.disabled = True
        
        await interaction.response.edit_message(embed=em, view=view)
        
    async def search_song(self, track_name):
        results = self.sp.search(track_name ,limit=1, type= "track")
        track = {"title": "", "artists": [], "duration": "0:0",  "link": "", "thumbnail_url": "", "emoji": "<:spotify:1432179988647645336>", "audio_url": ""}
        tracks = results["tracks"]["items"][0]
        ydl_opts = {
            "format": "bestaudio/best",
            "noplaylist": True,
            "quiet": True,
            "nopart": True,
            #"extract_flat": True,
            "default_search": "ytsearch",
            "cookiefile": "assets//cookie.txt"
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1: {track_name}", download=False)
            if not info:
                return None
            if "entries" in info and len(info["entries"])>0:
                info = info["entries"][0]
            track["audio_url"] = info["url"]
            track["thumbnail_url"] = info.get("thumbnail", None)
            duration = info.get("duration", 0)
            if (duration%60) < 10:
                track["duration"] = f"{duration//60}:0{duration%60}"
            else:
                track["duration"] = f"{duration//60}:{duration%60}"
        if tracks:
            for artist in tracks["artists"]:
                track["artists"].append(artist["name"])
            track["title"] = f"{tracks['name']} - {','.join(track['artists'])}"
            track["link"] = tracks["external_urls"]["spotify"]
            duration = tracks.get("duration_ms", 0)//1000
            track["duration"] = f"{duration//60}:{duration%60}"
            if not track["thumbnail_url"]:
                track["thumbnail_url"] = tracks["album"]["images"][0]["url"]
        else:
            track["emoji"] = "<:youtube:1432179973367533578>"
            track["title"] = info["title"]
            track["artists"] = info["artists"]
            track["link"] = info["webpage_url"]

        return track

    @commands.command(aliases=["p"])
    @commands.cooldown(1,10, type = commands.BucketType.user )
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
            if voice_client.is_playing() and voice_client.channel.id != channel.id:  
                await ctx.send(embed= Embed(title=f"Cannot join your channel because currently playing in <#{voice_client.channel.id}>", color = Color.red()))  
                return  
            else:  
                await voice_client.move_to(channel)  
        else:  
            voice_client = await channel.connect()  
            if str(ctx.guild.id) in self.player:  
                self.player.pop(str(ctx.guild.id))  
        async with ctx.typing():
            msg = await ctx.send("-# 🔍 Searching for song <a:musicloader:1433171921524232302> ")
            music_track = await self.search_song(search)  
            await msg.delete()
        if not music_track:  
            em = Embed(title= "Unable to Find song", description= "We are unable to find any song with the given name 😔 anywhere on Spotify, Youtube, SoundCloud, etx. Please forgive us and try again using more specific name", color = Color.greyple())  
            await ctx.send(embed=em)  
            return  
        estimated_time = 0  
        if str(ctx.guild.id) in self.player:  
            for song in self.player[str(ctx.guild.id)]:  
                duration = song["duration"]  
                seconds += (int(duration.split(":")[0])*60) + int(duration.split(":")[1])  
            if (seconds%60) < 10:
                estimated_time = f"{seconds//60}:0{seconds%60}"  
            else:
                estimated_time = f"{seconds//60}:{seconds%60}"  
        else:  
            estimated_time = "00:00"  
        em = Embed(title="🎶 Song Added in Queue", description= f"[**{music_track['title']}**]({music_track['link']})\n**Artist**: {music_track['artists'][0]}\n**Duration**: {music_track['duration']}\n**Estimated time before playing**: {estimated_time}", color = Color.purple())  
        em.set_author(name= ctx.author.name, icon_url= ctx.author.avatar)  
        em.set_footer(text= f"Song added by {ctx.author.name} | At {datetime.now(UTC).strftime('%m-%d %H:%M')}" , icon_url= ctx.author.avatar)  
        em.set_thumbnail(url= music_track["thumbnail_url"])  
        await ctx.send(embed= em)  
        if str(ctx.guild.id) in self.player:  
            self.player[str(ctx.guild.id)].append(music_track)  
        else:  
            self.player[str(ctx.guild.id)] = [music_track]  
            await self.play_next(ctx, start = True)  
  
    @commands.command(aliases=["q"])  
    @commands.cooldown(1,10, type = commands.BucketType.user )  
    @commands.has_permissions()  
    @commands.bot_has_permissions()  
    async def queue(self, ctx):  
        """Shows the songs queue list 🎵"""
        if str(ctx.guild.id) in self.player:
            songs = self.player[str(ctx.guild.id)]
        else:
            await ctx.send(embed= Embed(description= "Playlist empty. Play songs using `play` command"))
            return
        description = ""
        for song in songs:
            description += 
        em = Embed(title = "🎶 Upcoming Playlist 🎶", description = "\n".join([f"[**{song['title']}**]({song['link']}) - {song['duration']}" for song in songs]) , color = Color.purple())  
        em.set_footer(text= f"Requested by {ctx.author.name} | At {datetime.now(UTC).strftime('%m-%d %H:%M')}" , icon_url= ctx.author.avatar)  
        await ctx.send(embed = em)  
      
    @commands.command(aliases=[])  
    @commands.cooldown(1,10, type = commands.BucketType.user )  
    @commands.has_permissions()  
    @commands.bot_has_permissions()  
    async def skip(self, ctx):  
        """Skips the current playing song. Requires voting from all vc members."""  
        music = self.player.get(str(ctx.guild.id), None)  
        if not music:  
            await ctx.send(embed=Embed(description="No Track is playing currently.",color = Color.red()))  
            return
        music = music[0]
        for m in ctx.voice_client.channel.members:  
            if m.id == ctx.author.id:  
                break  
        else:  
            await ctx.send(embed= Embed(description="You are not in a voice channel or in a different voice channel than me.", color=Color.red()))  
            return  
        await self.send_player(ctx, music)
        
    @commands.command(aliases=[])  
    @commands.cooldown(1,10, type = commands.BucketType.user )  
    @commands.has_permissions()  
    @commands.bot_has_permissions()  
    async def stop(self, ctx):  
        """Stops playing the current song. Requires voting from all vc members."""  
        music = self.player.get(str(ctx.guild.id), None)  
        if not music:  
            await ctx.send(embed=Embed(description="No Track is playing currently.",color = Color.red()))  
            return
        music = music[0]
        for m in ctx.voice_client.channel.members:  
            if m.id == ctx.author.id:  
                break  
        else:  
            await ctx.send(embed= Embed(description="You are not in a voice channel or in a different voice channel than me.", color=Color.red()))  
            return  
        await self.send_player(ctx, music)
  
async def setup(bot):  
    await bot.add_cog(Musik_and_Media(bot))  
    print("Loaded cogs: MusikMedia")
