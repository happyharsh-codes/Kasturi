from __init__ import*
import yt_dlp
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import sclib
import lyricsgenius 

class MusicController:
    def __init__(self, ctx, player):
        self.player = player
        self.ctx = ctx
        self.skip_votes = set()
        self.pause_votes = set()
        self.rewind_votes = set()

    async def check(self, interaction):
        player = interaction.guild.voice_client
        if not interaction.user.voice:
            await interaction.response.send_message("❌ You must be in a voice channel.", ephemeral=True )
            return True
        if not player or not player.channel:
            await interaction.response.send_message("❌ I'm not connected to a voice channel.",ephemeral=True)
            return True
        if interaction.user.voice.channel != player.channel:
            await interaction.response.send_message("❌ You must be in the same voice channel as me.",ephemeral=True)
            return True
        return False
        
    async def send_player(self, ctx):
        track = self.player.current
        em = Embed(color= Color.green())
        em.set_author(name= "▶️ Now Playing")
        em.title = f"{<:youtube:1432179973367533578> {track.title}"
        em.url = track.uri
        duration = track.length // 1000
        minutes = duration // 60
        seconds = duration % 60
        em.description = f"**Artist**: {track.author}\n**Duration**: {minutes}:{seconds:02d}"
        em.set_thumbnail(url= f"https://img.youtube.com/vi/{track.identifier}/hqdefault.jpg")
        em.set_footer(text= "⟡ Operate Music Player with buttons")

        pause = Button(style=ButtonStyle.secondary, custom_id="pause", label="⏸️")
        play = Button(style=ButtonStyle.secondary, custom_id="play", label="▶️", disabled = True)
        rewind = Button(style=ButtonStyle.secondary, custom_id="rewind", label="⏮️")
        skip = Button(style=ButtonStyle.secondary, custom_id="skip", label="⏭️")
        lyrics = Button(style=ButtonStyle.secondary, custom_id="lyrics", label="📝")

        async def on_pause(self, interaction):
            if await self.check(interaction):
                return
            paused, required, voters, members = self.add_voter("pause")
            if paused:
                await self.player.pause(True)
                self.clear_votes()
                em.title = "⏸️ Song Paused"
                em.set_footer(text=f"Song Paused by {voters}/{members}")
                view.clear_items()
                view.add_item(rewind)
                view.add_item(play)
                view.add_item(lyrics)
                view.add_item(skip)
                return await interaction.response.edit_message(embed=em, view= view)
            em.set_footer(text= f"\nPausing, {voters}/{members} ({required} votes required)")
            return await interaction.response.edit_message(embed=em)
        
        async def on_rewind(self, interaction):
            if await self.check(interaction):
                return
            rewinded, required, voters, members = self.add_voter("pause")
            if rewinded:
                await self.player.seek(0)
                self.clear_votes()
                em.title = "⏮️ Song Rewinded"
                em.set_footer(text=f"Song Rewinded by {voters}/{members}")
                return await interaction.response.edit_message(embed=em, view= view)
            em.set_footer(text= f"\nRewinding, {voters}/{members} ({required} votes required)")
            return await interaction.response.edit_message(embed=em)

        async def on_skip(self, interaction):
            if await self.check(interaction):
                return
            skipped, required, voters, members = self.add_voter("pause")
            if skipped:
                await self.player.stop()
                self.clear_votes()
                em.title = "⏭️ Song Skipped"
                em.set_footer(text=f"Song Skipped by {voters}/{members}")
                if not self.player.queue:
                    skip.disabled = True
                return await interaction.response.edit_message(embed=em, view= view)
            em.set_footer(text= f"\nSkipping, {voters}/{members} ({required} votes required)")
            return await interaction.response.edit_message(embed=em)

        async def on_play(self, interaction):
            if await self.check(interaction):
                return
            self.player.pause(False)
            em.title = "▶️ Now Playing"
            view.clear_items()
            view.add_item(rewind)
            view.add_item(pause)
            view.add_item(lyrics)
            view.add_item(skip)
            self.clear_votes()
            return await interaction.response.edit_message(embed=em, view=view)

        async def on_lyrics(self, interaction):
            if await self.check(interaction):
                return
            lyrics.disabled = True
            return await interaction.response.edit_message("Lyrics", view=view)
            
        pause.callback = on_pause
        play.callback = on_play
        rewind.callback = on_rewind
        skip.callback = on_skip
        lyrics.callback = on_lyrics
   
        view = View(timeout=100)
        async def on_timeout():
            nonlocal em, msg, view, pause, rewind, skip, lyrics
            for children in view.children:
                children.disabled = True
            em.color = Color.light_grey()
            await msg.edit(embed=em, view=view)
            
        view.on_timeout = on_timeout
        view.add_item(rewind)
        view.add_item(pause)
        view.add_item(lyrics)
        view.add_item(skip)
        
        msg = await ctx.send(embed= em, view= view)

    def clear_voters(self):
        self.skip_votes.clear()
        self.rewind_votes.clear()
        self.skip_votes.clear()
        
    async def add_voter(self, vote_for, voter_id):
        """returns True if now majority have voted else returns False"""
        channel = self.player.channel
        members = [m for m in channel.members if not m.bot]
        required = max(1, math.ceil(len(members) * 0.6))
        
        if vote_for == "skip":
            if voter_id in self.skip_votes:
                await self.ctx.send("You have already voted for this one", ephemeral= True)
                return False, required, self.skip_votes
            self.skip_votes.add(voter_id)
            if len(self.skip_votes) >= required:
                return True, required, self.skip_votes, members
            return False, required, self.skip_votes, members
        if vote_for == "pause":
            if voter_id in self.pause_votes:
                await self.ctx.send("You have already voted for this one", ephemeral= True)
                return False, required, self.pause_votes
            self.pause_votes.add(voter_id)
            if len(self.pause_votes) >= required:
                return True, required, self.pause_votes, members
            return False, required, self.pause_votes, members
        if vote_for == "rewind":
            if voter_id in self.rewind_votes:
                await self.ctx.send("You have already voted for this one", ephemeral= True)
                return False, required, self.rewind_votes
            self.rewind_votes.add(voter_id)
            if len(self.rewind_votes) >= required:
                return True, required, self.rewind_votes, members
            return False, required, self.rewind_votes, members
            
class Music_and_Media(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.controllers = {}
        
    @commands.Cog.listener("on_wavelink_track_end")
    async def on_track_end(self, payload: wavelink.TrackEndEventPayload):
        player = payload.player
        guild = player.guild
        guild_id = guild.id
        controller = self.controllers.get(guild_id)
        if not controller:
            return
        if len(voice.channel.members) - 1 == 0:
            self.controllers.pop(guild_id, None)
            await controller.ctx.send(embed=Embed(description="No Active Listerns, Leaving Vc..."))
            return await player.stop()
        if player.queue:
            next_track = player.queue.get()
            await player.play(next_track)
            ctx = controller.ctx
            await controller.send_player(ctx, next_track)
        else:
            await player.disconnect()
            self.controllers.pop(guild.id, None)
            
    @commands.hybrid_command(aliases=["p"])
    @commands.cooldown(1,10, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def play(self, ctx, *, query: str):
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
        player: wavelink.Player = ctx.voice_client
        guild_id = ctx.guild.id
        if not player:
            player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        tracks = await wavelink.Playable.search(query)
        if not tracks: 
            return await ctx.send(embed= Embed(title= "Unable to Find this song", description= "Uable to find any song with the given name anywhere. Please try again using more specific name", color = Color.greyple()))
        track = tracks[0]
        duration = track.length // 1000
        minutes = duration // 60
        seconds = duration % 60
        player.home = ctx.channel
        if guild_id not in self.controllers:
            self.controllers[guild_id] = MusicController(ctx, player)
        controller = self.controllers[guild_id]
        if player.playing:
            estimated_duration = 0
            for itrack in player.queue:
                estimated_duration += itrack.duration
            estimated_duration = estimated_duration // 1000
            estimated_time = f"{estimated_duration//60}:{estimated_duration%60:02d}"
            player.queue.put(track)
            em = Embed(title="🎶 Song Added in Queue", description= f"[**{track.title}**]({track.uri})\n**Artist**: {track.author}\n**Duration**: {minutes}:{seconds:02d}\n**Queue No**: {len(player.queue)}\n**Estimated time before playing**: {estimated_time}", color = Color.purple())  
            em.set_author(name= ctx.author.name, icon_url= ctx.author.avatar)  
            em.set_footer(text= f"Song added by {ctx.author.name}" , icon_url= ctx.author.avatar) 
            em.set_thumbnail(url= f"https://img.youtube.com/vi/{track.identifier}/hqdefault.jpg")  
            await ctx.send(embed=em)
        else:
            await player.play(track)
            await controller.send_player(ctx)    
        
    @commands.hybrid_command(aliases=["q", "up", "upcoming"])  
    @commands.cooldown(1,10, type = commands.BucketType.user )  
    @commands.has_permissions()  
    @commands.bot_has_permissions()  
    async def queue(self, ctx):  
        """Shows the songs queue list 🎵"""
        if ctx.guild.id) in self.controllers:
            controller = self.controllers[ctx.guild.id]
        else:
            await ctx.send(embed= Embed(description= "Playlist empty. Play songs using `play` command"))
            return
        player = controller.player 
        if not player.queue:
            await ctx.send(embed= Embed(description= "Playlist empty. Play songs using `play` command"))
            return
        descrip = ""
        for i, track in enumerate(player.queue):
            duration = track.length // 1000
            minutes = duration // 60
            seconds = duration % 60
            description += f"**{i+1}**. [**{track.title}**]({track.uri}) - {minutes}:{seconds:02d}\n" 
        em = Embed(title = "🎶 Upcoming Playlist 🎶", description = descrip, color = Color.purple())
        em.set_author(name = ctx.author.display_name, icon_url=ctx.author.avatar)
        em.set_footer(text= f"Requested by {ctx.author.name}")  
        await ctx.send(embed = em)  
      
    @commands.hybrid_command(aliases=[])  
    @commands.cooldown(1,10, type = commands.BucketType.user )  
    @commands.has_permissions()  
    @commands.bot_has_permissions()  
    async def skip(self, ctx):  
        """Skips the current playing song. Requires voting from all vc members."""  
        controller = self.controllers.get(ctx.guild.id, None)  
        if not music:  
            await ctx.send(embed=Embed(description="No Track is playing currently.",color = Color.red()))  
            return
        voice = ctx.guild.voice_client
        if not voice:
            await ctx.send(embed= Embed(title="No voice channel connected, stopped playing"))
            try:
                self.controller.pop(str(ctx.guild.id))
            except:
                pass
            return 
        for m in voice.channel.members:  
            if m.id == ctx.author.id:  
                break  
        else:  
            await ctx.send(embed= Embed(description="You are not in a voice channel or in a different voice channel than the bot.", color=Color.red()))  
            return  
        await controller.send_player(ctx)
        
    @commands.hybrid_command(aliases=[])  
    @commands.cooldown(1,10, type = commands.BucketType.user )  
    @commands.has_permissions()  
    @commands.bot_has_permissions()  
    async def stop(self, ctx):  
        """Stops playing the current song. Requires voting from all vc members."""  
        controller = self.controllers.get(ctx.guild.id, None)  
        if not music:  
            await ctx.send(embed=Embed(description="No Track is playing currently.",color = Color.red()))  
            return
        voice = ctx.guild.voice_client
        if not voice:
            await ctx.send(embed= Embed(title="No voice channel connected, stopped playing"))
            try:
                self.controller.pop(str(ctx.guild.id))
            except:
                pass
            return 
        for m in voice.channel.members:  
            if m.id == ctx.author.id:  
                break  
        else:  
            await ctx.send(embed= Embed(description="You are not in a voice channel or in a different voice channel than the bot.", color=Color.red()))  
            return  
        await controller.send_player(ctx)

    @commands.hybrid_command(aliases=["np"])  
    @commands.cooldown(1,10, type = commands.BucketType.user )  
    @commands.has_permissions()  
    @commands.bot_has_permissions()  
    async def now_playing(self, ctx):  
        """Shows the current song playing."""  
        controller = self.controllers.get(ctx.guild.id, None)  
        if not music:  
            await ctx.send(embed=Embed(description="No Track is playing currently.",color = Color.red()))  
            return
        voice = ctx.guild.voice_client
        if not voice:
            await ctx.send(embed= Embed(title="No voice channel connected, stopped playing"))
            try:
                self.controller.pop(str(ctx.guild.id))
            except:
                pass
            return 
        for m in voice.channel.members:  
            if m.id == ctx.author.id:  
                break  
        else:  
            await ctx.send(embed= Embed(description="You are not in a voice channel or in a different voice channel than the bot.", color=Color.red()))  
            return  
        await controller.send_player(ctx)

    @commands.hybrid_command(aliases=[])  
    @commands.cooldown(1,10, type = commands.BucketType.user )  
    @commands.has_permissions()  
    @commands.bot_has_permissions()  
    async def lyrics(self, ctx):  
        """Shows lyrics for the current song"""  
        controller = self.controllers.get(ctx.guild.id, None)  
        if not music:  
            await ctx.send(embed=Embed(description="No Track is playing currently.",color = Color.red()))  
            return
        voice = ctx.guild.voice_client
        if not voice:
            await ctx.send(embed= Embed(title="No voice channel connected, stopped playing"))
            try:
                self.controller.pop(str(ctx.guild.id))
            except:
                pass
            return 
        for m in voice.channel.members:  
            if m.id == ctx.author.id:  
                break  
        else:  
            await ctx.send(embed= Embed(description="You are not in a voice channel or in a different voice channel than the bot.", color=Color.red()))  
            return  
        await controller.send_player(ctx)

    @commands.hybrid_command(aliases=[])  
    @commands.cooldown(1,10, type = commands.BucketType.user )  
    @commands.has_permissions()  
    @commands.bot_has_permissions()  
    async def rewind(self, ctx):  
        """Rewinds the current song. Requires voting from all vc members."""  
        controller = self.controllers.get(ctx.guild.id, None)  
        if not music:  
            await ctx.send(embed=Embed(description="No Track is playing currently.",color = Color.red()))  
            return
        voice = ctx.guild.voice_client
        if not voice:
            await ctx.send(embed= Embed(title="No voice channel connected, stopped playing"))
            try:
                self.controller.pop(str(ctx.guild.id))
            except:
                pass
            return 
        for m in voice.channel.members:  
            if m.id == ctx.author.id:  
                break  
        else:  
            await ctx.send(embed= Embed(description="You are not in a voice channel or in a different voice channel than the bot.", color=Color.red()))  
            return  
        await controller.send_player(ctx)
  
async def setup(bot):  
    await bot.add_cog(Music_and_Media(bot))  
    print("Loaded cogs: MusikMedia")
