from __init__ import*
import lyricsgenius 

class Music_and_Media(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.skip_votes = {}
        self.pause_votes = {}
        self.rewind_votes = {}

    async def check(self, player, interaction):
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
        
    async def send_player(self, ctx, player):
      try:
        track = player.current
        em = Embed(color= Color.green())
        em.set_author(name= "▶️ Now Playing")
        em.title = f"<:youtube:1432179973367533578> {track.title}"
        em.url = track.uri
        duration = track.length // 1000
        minutes = duration // 60
        seconds = duration % 60
        em.description = f"**Artist**: {track.author}\n**Duration**: {minutes}:{seconds:02d}"
        em.set_thumbnail(url= track.artwork)
        em.set_footer(text= "⟡ Operate Music Player with buttons")

        pause = Button(style=ButtonStyle.secondary, custom_id="pause", label="⏸️")
        play = Button(style=ButtonStyle.secondary, custom_id="play", label="▶️", disabled = True)
        rewind = Button(style=ButtonStyle.secondary, custom_id="rewind", label="⏮️")
        skip = Button(style=ButtonStyle.secondary, custom_id="skip", label="⏭️")
        lyrics = Button(style=ButtonStyle.secondary, custom_id="lyrics", label="📝")

        async def on_pause(interaction):
            if await self.check(player, interaction):
                return
            paused, required, voters, members = self.add_voter("pause", interaction.user.id, interaction, ctx.guild.id, player)
            if paused:
                await player.pause()
                self.clear_voters(ctx.guild.id)
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
        
        async def on_rewind(interaction):
            if await self.check(player, interaction):
                return
            rewinded, required, voters, members = self.add_voter("rewind", interaction.user.id, interaction, ctx.guild.id, player)
            if rewinded:
                await player.seek(0)
                self.clear_voters(ctx.guild.id)
                em.title = "⏮️ Song Rewinded"
                em.set_footer(text=f"Song Rewinded by {voters}/{members}")
                return await interaction.response.edit_message(embed=em, view= view)
            em.set_footer(text= f"\nRewinding, {voters}/{members} ({required} votes required)")
            return await interaction.response.edit_message(embed=em)

        async def on_skip(interaction):
            if await self.check(player, interaction):
                return
            skipped, required, voters, members = self.add_voter("skip", interaction.user.id, interaction, ctx.guild.id, player)
            if skipped:
                await player.skip(force=True)
                self.clear_voters(ctx.guild.id)
                em.title = "⏭️ Song Skipped"
                em.set_footer(text=f"Song Skipped by {voters}/{members}")
                if player.queue.count == 0:
                    skip.disabled = True
                return await interaction.response.edit_message(embed=em, view= view)
            em.set_footer(text= f"\nSkipping, {voters}/{members} ({required} votes required)")
            return await interaction.response.edit_message(embed=em)

        async def on_play(interaction):
            if await self.check(player, interaction):
                return
            player.resume()
            em.title = "▶️ Now Playing"
            view.clear_items()
            view.add_item(rewind)
            view.add_item(pause)
            view.add_item(lyrics)
            view.add_item(skip)
            self.clear_voters(ctx.guild.id)
            return await interaction.response.edit_message(embed=em, view=view)

        async def on_lyrics(interaction):
            if await self.check(player, interaction):
                return
            lyrics.disabled = True
            em2 = Embed(title= "Lyrics", description= "Lyrics are coming...", color=Color.purple())
            return await interaction.response.send_message(embed=em2, view=view)
            
        pause.callback = on_pause
        play.callback = on_play
        rewind.callback = on_rewind
        skip.callback = on_skip
        lyrics.callback = on_lyrics
   
        view = View(timeout=duration)
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
      except Exception as e:
        await self.client.get_user(894072003533877279).send(e)
        
    def clear_voters(self, guild_id):
        self.skip_votes.pop(guild_id, None)
        self.rewind_votes.pop(guild_id, None)
        self.pause_votes.pop(guild_id, None)
        
    async def add_voter(self, vote_for, voter_id, interaction, guild_id, player):
        """returns True if now majority have voted else returns False"""
        channel = player.channel
        members = [m for m in channel.members if not m.bot]
        required = max(1, math.ceil(len(members) * 0.6))
        
        if vote_for == "skip":
            votes = self.skip_votes
        elif vote_for == "pause":
            votes = self.pause_votes
        elif vote_for == "rewind":
            votes = self.rewind_votes
        if guild_id in votes:
            if voter_id in votes[guild_id]:
                await interaction.response.send_message("You have already voted for this one", ephemeral= True)
                return False, required, len(votes[guild_id]), members
            votes[guild_id].append(voter_id)
        else:
            votes[guild_id] = [voter_id]
        if len(votes[guild_id]) >= required:
            return True, required, len(votes[guild_id]), len(members)
        return False, required, len(votes[guild_id]), len(members)
        
    @commands.Cog.listener("on_wavelink_track_start")     
    async def on_wavelink_track_start(self, payload: wavelink.TrackStartEventPayload) -> None:
      try:
        player: wavelink.Player | None = payload.player
        if not player:
            return
        track: wavelink.Playable = payload.track
        await self.send_player(player.home, player)
      except Exception as e:
        await self.client.get_user(894072003533877279).send(str(e))
        
    @commands.Cog.listener("on_wavelink_track_end")
    async def on_track_end(self, payload: wavelink.TrackEndEventPayload):
      try:
        player: wavelink.Player | None = payload.player
        if not player:
            return
        if not player.channel:
            return
        members = [m for m in player.channel.members if not m.bot]
        if len(members) == 0:
            await player.home.send(embed=Embed(description="No Active Listerns, Leaving Vc..."))
            return await player.disconnect()
        try:
            next_track = player.queue.get()
            await player.play(next_track)
        except:
            await player.disconnect()
      except Exception as e:
        await self.client.get_user(894072003533877279).send(str(e))
        
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
        player: wavelink.Player = ctx.voice_client
        if not player:
            player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        if player.playing and player.channel.id != channel.id:  
                return await ctx.send(embed= Embed(title=f"Cannot join your channel because currently playing in {player.channel.mention}", color = Color.red()))  
        tracks = await wavelink.Playable.search(query)
        if not tracks: 
            return await ctx.send(embed= Embed(title= "Unable to Find this song", description= "Uable to find any song with the given name anywhere. Please try again using more specific name", color = Color.greyple()))
        track = tracks[0]
        duration = track.length // 1000
        minutes = duration // 60
        seconds = duration % 60
        player.home = ctx.channel
        if player.playing:
            estimated_duration = player.current.length - player.position
            for itrack in player.queue:
                estimated_duration += itrack.length
            estimated_duration = estimated_duration // 1000
            estimated_time = f"{estimated_duration//60}:{estimated_duration%60:02d}"
            player.queue.put(track)
            em = Embed(title="🎶 Song Added in Queue", description= f"[**{track.title}**]({track.uri})\n**Artist**: {track.author}\n**Duration**: {minutes}:{seconds:02d}\n**Queue No**: {player.queue.count}\n**Estimated time before playing**: {estimated_time}", color = Color.purple())  
            em.set_author(name= ctx.author.name, icon_url= ctx.author.avatar)  
            em.set_footer(text= f"Song added by {ctx.author.name}" , icon_url= ctx.author.avatar) 
            em.set_thumbnail(url= track.artwork)  
            await ctx.send(embed=em)
        else:
            await player.play(track)
            
    @commands.hybrid_command(aliases=["q", "up", "upcoming"])  
    @commands.cooldown(1,10, type = commands.BucketType.user )  
    @commands.has_permissions()  
    @commands.bot_has_permissions()  
    async def queue(self, ctx):  
        """Shows the songs queue list 🎵"""
        player: wavelink.Player = ctx.voice_client
        if not player:
            await ctx.send(embed= Embed(description= "Playlist empty. Play songs using `play` command"))
            return 
        if player.queue.count == 0:
            await ctx.send(embed= Embed(description= "Playlist empty. Play songs using `play` command"))
            return
        descrip = ""
        for i, track in enumerate(player.queue):
            duration = track.length // 1000
            minutes = duration // 60
            seconds = duration % 60
            descrip += f"**{i+1}**. [**{track.title}**]({track.uri}) - {minutes}:{seconds:02d}\n" 
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
        player: wavelink.Player = ctx.voice_client
        if not player:
            await ctx.send(embed=Embed(description="No Track is playing currently.",color = Color.red()))  
            return
        if not ctx.author.voice or ctx.author.voice.channel != player.channel:  
            await ctx.send(embed= Embed(description="You are not in a voice channel or in a different voice channel than the bot.", color=Color.red()))  
            return  
        await self.send_player(ctx, player)
        
    @commands.hybrid_command(aliases=[])  
    @commands.cooldown(1,10, type = commands.BucketType.user )  
    @commands.has_permissions()  
    @commands.bot_has_permissions()  
    async def stop(self, ctx):  
        """Stops playing the current song. Requires voting from all vc members."""  
        player: wavelink.Player = ctx.voice_client
        if not player:
            await ctx.send(embed=Embed(description="No Track is playing currently.",color = Color.red()))  
            return
        if not ctx.author.voice or ctx.author.voice.channel != player.channel:
            await ctx.send(embed= Embed(description="You are not in a voice channel or in a different voice channel than the bot.", color=Color.red()))  
            return  
        await self.send_player(ctx, player)

    @commands.hybrid_command(aliases=["np"])  
    @commands.cooldown(1,10, type = commands.BucketType.user )  
    @commands.has_permissions()  
    @commands.bot_has_permissions()  
    async def now_playing(self, ctx):  
        """Shows the current song playing."""  
        player: wavelink.Player = ctx.voice_client
        if not player:
            await ctx.send(embed=Embed(description="No Track is playing currently.",color = Color.red()))  
            return
        
        if not ctx.author.voice or ctx.author.voice.channel != player.channel:  
            await ctx.send(embed= Embed(description="You are not in a voice channel or in a different voice channel than the bot.", color=Color.red()))  
            return  
        await self.send_player(ctx, player)

    @commands.hybrid_command(aliases=[])  
    @commands.cooldown(1,10, type = commands.BucketType.user )  
    @commands.has_permissions()  
    @commands.bot_has_permissions()  
    async def lyrics(self, ctx):  
        """Shows lyrics for the current song"""  
        player: wavelink.Player = ctx.voice_client
        if not player:
            await ctx.send(embed=Embed(description="No Track is playing currently.",color = Color.red()))  
            return
        if not ctx.author.voice or ctx.author.voice.channel != player.channel:
            await ctx.send(embed= Embed(description="You are not in a voice channel or in a different voice channel than the bot.", color=Color.red()))  
            return  
        await self.send_player(ctx, player)

    @commands.hybrid_command(aliases=[])  
    @commands.cooldown(1,10, type = commands.BucketType.user )  
    @commands.has_permissions()  
    @commands.bot_has_permissions()  
    async def rewind(self, ctx):  
        """Rewinds the current song. Requires voting from all vc members."""  
        player: wavelink.Player = ctx.voice_client
        if not player:  
            await ctx.send(embed=Embed(description="No Track is playing currently.",color = Color.red()))  
            return
        if not ctx.author.voice or ctx.author.voice.channel != player.channel:
            await ctx.send(embed= Embed(description="You are not in a voice channel or in a different voice channel than the bot.", color=Color.red()))  
            return  
        await self.send_player(ctx, player)
  
async def setup(bot):  
    await bot.add_cog(Music_and_Media(bot))  
    print("Loaded cogs: MusikMedia")
