from __init__ import *

class Moderation(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    # ===== Utility Functions =====

    async def safe_dm(self, member: discord.Member, embed: discord.Embed):
        """Safely tries to DM a user, fallback to channel if DMs are closed."""
        try:
            if not member.dm_channel:
                await member.create_dm()
            await member.dm_channel.send(embed=embed)
        except:
            return False
        return True

    def action_embed(self, title: str, desc: str, ctx: commands.Context, member=None, color=Color.pink()):
        """Creates a consistent embed style for actions."""
        embed = Embed(title=title, description=desc, color=color)
        embed.set_footer(text=f"{ctx.command.name.title()} by {ctx.author.name} • {timestamp(ctx)}", icon_url=ctx.author.avatar)
        if member:
            embed.set_author(name=member.name, icon_url=member.avatar)
        return embed

    # ===== Kelly-Only Mute =====

    @commands.hybrid_command(aliases=["kelly_mute", "kmute"])
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def mute_from_kelly(self, ctx: commands.Context, member: discord.Member, *, reason: str):
        """Temporarily prevents a user from chatting with Kelly, not server-wide."""
        minutes = randint(5, 15)
        until = (datetime.now(UTC) + timedelta(minutes=minutes)).isoformat()
        Server_Settings[str(ctx.guild.id)]["muted"][str(member.id)] = until

        embed = self.action_embed(
            "🔇 Kelly Chat Mute Applied",
            f"{member.mention} has been muted for **{minutes} minutes**.\n**Reason:** {reason}",
            ctx, member
        )
        await ctx.send(embed=embed)

    # ===== Server Mute =====

    @commands.hybrid_command(aliases=[])
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def mute(self, ctx: commands.Context, member: discord.Member, minutes: int, *, reason: str):
        """Server mute — prevents member from sending messages."""
        try:
            duration = timedelta(minutes=minutes)
            await member.timeout(duration, reason=reason)

            embed_dm = Embed(
                title=f"You have been muted in {ctx.guild.name}",
                description=f"**Reason:** {reason}\nPlease follow server rules.",
                color=Color.red()
            )
            await self.safe_dm(member, embed_dm)

            embed = self.action_embed(
                "🔇 Member Muted",
                f"{member.mention} muted for **{minutes} minutes**.\n**Reason:** {reason}",
                ctx, member
            )
            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"❌ Could not mute {member.mention}. Error: `{e}`")

    # ===== Kelly-Only Unmute =====

    @commands.hybrid_command(aliases=["kelly_unmute", "kunmute"])
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def unmute_from_kelly(self, ctx: commands.Context, member: discord.Member, *, reason: str = "No reason provided"):
        """Removes Kelly-only chat mute."""
        muted = Server_Settings[str(ctx.guild.id)]["muted"]
        if str(member.id) not in muted:
            return await ctx.send("⚠️ That user is not muted from Kelly.")

        muted.pop(str(member.id))

        embed = self.action_embed(
            "🔊 Kelly Chat Unmuted",
            f"{member.mention} can now talk to Kelly again.\n**Reason:** {reason}",
            ctx, member, Color.green()
        )
        await ctx.send(embed=embed)

    # ===== Server Unmute =====

    @commands.hybrid_command()
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def unmute(self, ctx: commands.Context, member: discord.Member, *, reason: str):
        """Restores user's chat permissions server-wide."""
        if not member.timed_out_until:
            return await ctx.send("⚠️ That member is not muted.")

        await member.edit(timed_out_until=None, reason=reason)

        embed_dm = Embed(
            title=f"You have been Unmuted in {ctx.guild.name}",
            description=f"**Reason:** {reason}",
            color=Color.green()
        )
        embed_dm.set_footer(text=f"Unmuted by {ctx.author.name}")
        await self.safe_dm(member, embed_dm)

        embed = self.action_embed("🔊 Member Unmuted", f"{member.mention} is unmuted.", ctx, member, Color.green())
        await ctx.send(embed=embed)

    # ===== Kick =====

    @commands.hybrid_command()
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx: commands.Context, member: discord.Member, *, reason: str):
        """Kick a member from the server."""
        embed_dm = Embed(
            title=f"You were kicked from {ctx.guild.name}",
            description=f"**Reason:** {reason}",
            color=Color.red()
        )
        await self.safe_dm(member, embed_dm)

        await ctx.guild.kick(member, reason=reason)

        embed = self.action_embed(
            "👢 Member Kicked",
            f"{member.mention} was kicked.\n**Reason:** {reason}",
            ctx, member
        )
        await ctx.send(embed=embed)

    # ===== Warn =====

    @commands.hybrid_command()
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def warn(self, ctx, member: discord.Member, *, reason: str):
        """Send official warning to a member."""
        embed_dm = Embed(
            title=f"You were warned in {ctx.guild.name}",
            description=f"**Reason:** {reason}",
            color=Color.orange()
        )
        await self.safe_dm(member, embed_dm)

        embed = self.action_embed("⚠️ Member Warned", f"{member.mention}\n**Reason:** {reason}", ctx, member, Color.orange())
        await ctx.send(embed=embed)

    # ===== BAN / UNBAN ==== 

    @commands.hybrid_command(aliases= [])
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx: commands.Context, member: discord.Member, *, reason: str):
        """Bans a member permanently 🚫  
        Stops them from rejoining until unbanned.
        Moderators Only - Please consider case properly before using this command."""
        em = Embed(title="Member Banned", description=f"{member.name} was banned by {ctx.author.mention}.\n**Reason:** {reason}.", color=Color.pink())
        em.set_footer(text=f"Banned by {ctx.author.name} | {timestamp(ctx)}", icon_url=ctx.author.avatar)
        em.set_author(name=member.name, icon_url= member.avatar)
        await ctx.send(embed=em)
        em = Embed(title= f"You were Banned from {ctx.guild.name}", description= f"**Reason:** {reason}", color = Color.red())
        em.set_footer(text = "If you believe this was a mistake please forgive us.")
        view = View()
        button = Button(style=ButtonStyle.primary, custom_id= "revive", label = "Click to Say your Last Words")
        
        class LastWordsModal(discord.ui.Modal):
            
            def __init__(self, member, msg):
                super().__init__(title="Last Words Apology Form")
                self.input_box = TextInput(label="Enter Your Last Words Here:", custom_id="last_words", required= True, min_length=5, max_length=1024, style=TextStyle.paragraph, default="I'm sorry")
                self.add_item(self.input_box)
                self.member = member
                self.msg = msg 
                
            async def on_submit(self, interaction: Interaction):
              try:
                member = self.member
                msg = self.msg
                last_words = self.input_box.value
                owner = ctx.bot.get_user(ctx.guild.owner_id)
                em = Embed(title = f"{member.display_name} | {member.name} | {member.id} - \nSays their Last Words After getting Banned.", description= f"```{last_words}```", color = Color.blue())
                em.set_thumbnail(url=member.avatar)
                em.set_footer(text= "If you think this was a mistake then please ignore.")
                try:
                    dm_channel = owner.dm_channel
                    if not dm_channel:
                        dm_channel = await owner.create_dm()
                    await dm_channel.send(embed=em)
                    moderators = Server_Settings[str(ctx.guild.id)]["moderators"]
                    if moderators:
                        for mod in moderators:
                            if int(mod) == member.id:
                                continue 
                            user = ctx.bot.get_user(int(mod))
                            if not user:
                                continue 
                            dm_channel = user.dm_channel
                            if not dm_channel:
                                dm_channel = await user.create_dm()
                            try:
                                await dm_channel.send(embed=em)
                            except:
                                pass
                except:
                    pass
                view = View()
                view.add_item(Button(style=ButtonStyle.secondary,label="Last Words Submitted",custom_id="submitted",disabled=True))
                await msg.edit(view=view)
                await msg.channel.send("**Your Last Words were recorded and sent to the Guild Owner and Guild Moderators**")
                await interaction.response.defer()
              except Exception as e:
                await ctx.bot.get_user(894072003533877279).send(str(e))
                await interaction.response.defer()
        
        async def last_words(interaction: Interaction):
          try: 
            nonlocal msg
            modal = LastWordsModal(member, msg)
            await interaction.response.send_modal(modal)     
          except Exception as e:
            await ctx.bot.get_user(894072003533877279).send(str(e))
            await interaction.response.defer()
        
        button.callback = last_words
        view.add_item(button)
        try:
            dm_channel = member.dm_channel
            if not dm_channel:
                dm_channel = await member.create_dm()
            msg = await dm_channel.send(embed=em, view=view)
        except:
            pass
        await ctx.guild.ban(user=member, reason=reason, delete_message_days=0)

    @commands.hybrid_command(aliases=["kelly_ban", "kban"])
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def ban_from_kelly(self, ctx: commands.Context, member: discord.Member, *, reason: str):
        """Just Bans a member from ever Chatting to Kelly Not from Server 🚫  
        Now user can never chat with Kelly, unless unbanned."""
        embed = Embed(title = f"You have been Banned from Kelly Chat", description = f"**Reason**: {reason}\n**Please refrain from sending messages like this.**", color = Color.red())
        embed.set_footer(text=f"Kelly Ban by {ctx.author.name} | <{timestamp(ctx)}", icon_url=ctx.author.avatar)
        
        try:
            dm_channel = member.dm_channel
            if not dm_channel:
                dm_channel = await member.create_dm()
            await dm_channel.send(embed=embed)
        except:
            await ctx.send(content= f"{member.mention}", embed=embed)
        
        Server_Settings[str(ctx.guild.id)]["block_list"].append(member.id)
        em = Embed(title="Member Banned From Kelly Talkings", description=f"{member.name} was banned by {ctx.author.mention}.\n**Reason:** {reason}", color=Color.pink())
        em.set_footer(text=f"Banned by {ctx.author.name} | {timestamp(ctx)}", icon_url=ctx.author.avatar)
        em.set_author(name=member.name, icon_url=member.avatar)
        await ctx.send(embed=em)
        
    @commands.hybrid_command()
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def unban(self, ctx: commands.Context, user_tag: str, *, reason: str):
        """Unbans a user by name or ID 🔓  
        Lets them rejoin your server.
        Sends them a Unbanned message."""
        async for entry in ctx.guild.bans():
            if entry.user.name.lower() == user_tag.lower() or entry.user.id == int(user_tag):
                await ctx.guild.unban(entry.user, reason= reason)
                em = Embed(title="Member Unbanned", description=f"{entry.user.name} was unbanned by {ctx.author.mention}.\n**Ban Reason:** {entry.reason}\n**Unban Reason:** {reason}", color=Color.red())
                em.set_footer(text=f"Unbanned by {ctx.author.name} | {timestamp(ctx)}", icon_url=ctx.author.avatar)
                await ctx.send(embed=em)
                dm_channel = entry.user.dm_channel
                if not dm_channel:
                    dm_channel = await entry.user.create_dm()
                try:
                    invite_link = Server_Settings[str(ctx.guild.id)]["invite_link"]
                    em = Embed(title = f"You were Unbanned from {ctx.guild.name}", description= f"You just got unbanned from the guild.\nClick here to join again\n{invite_link}", color=Color.green())
                    em.set_footer(text=f"Unbanned by {ctx.author.name} | {timestamp(ctx)}", icon_url=ctx.author.avatar)
                    await dm_channel.send(embed = em)
                except:
                    pass
                return
        await ctx.send("User not found in ban list.")

    @commands.hybrid_command(aliases=["kelly_unban", "kunban"])
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def unban_from_kelly(self, ctx: commands.Context, member: discord.Member, *, reason: str):
        """Unbans a user by name or ID 🔓 from Kelly. 
        Now they can start chatting with Kelly again.
        This is not related with server."""
        embed = Embed(title = f"You have been Unbanned from Kelly Chat", description = f"**Reason**: {reason}\n**Please refrain from sending messages like this.**", color = Color.red())
        embed.set_footer(text=f"Kelly Umban by {ctx.author.name} | <{timestamp(ctx)}", icon_url=ctx.author.avatar)
        
        try:
            dm_channel = member.dm_channel
            if not dm_channel:
                dm_channel = await member.create_dm()
            await dm_channel.send(embed=embed)
        except:
            await ctx.send(content= f"{member.mention}", embed=embed)
        
        
        Server_Settings[str(ctx.guild.id)]["block_list"].remove(member.id)
        em = Embed(
            title="Member Unbanned from Kelly Talk",
            description=f"{member.mention} was unbanned from kelly talking.\n**Reason: ** {reason}\nYou can Chat with Kelly using `kelly hi`.\nPlease be respectful this time.",
            color=Color.orange()
        )
        em.set_footer(text=f"Unbanned by {ctx.author.name} | {timestamp(ctx)}", icon_url=ctx.author.avatar)
        em.set_author(name=member.name,icon_url=member.avatar)
        await ctx.send(embed=em)
    
    @commands.hybrid_command()
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def assignrole(self, ctx: commands.Context, member: discord.Member, role: discord.Role):
        """Assigns given role to the user.
        Given role hierarchy should be equivalent to or less than your role."""
        embed = Embed(title = f"You have been Awared a role in {ctx.guild.name}", description = f"**Role**: {role.mention}\n**", color = Color.blue())
        embed.set_footer(text=f"Assigned Role by {ctx.author.name} | <{timestamp(ctx)}", icon_url=ctx.author.avatar)
        
        try:
            dm_channel = member.dm_channel
            if not dm_channel:
                dm_channel = await member.create_dm()
            await dm_channel.send(embed=embed)
        except:
            await ctx.send(content= f"{member.mention}", embed=embed)
        
        await member.add_roles(role)
        em = Embed(title="Role Assigned", description=f"{role.mention} assigned to {member.mention}", color=Color.green())
        em.set_footer(text=f"Role Assigned by {ctx.author.name} | {timestamp(ctx)}", icon_url=ctx.author.avatar)
        await ctx.send(embed=em)

    @commands.hybrid_command()
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.has_permissions(deafen_members=True)
    @commands.bot_has_permissions(deafen_members=True)
    async def deafen(self, ctx: commands.Context, member: discord.Member, minutes: int, channel: discord.VoiceChannel):
        """Deafens a member from all voice chat 🔇  
        Blocks audio from VC entirely.
        If voice channel is specified works for that channel only otherwise defens from all voice channel by default."""
        await member.edit(deafen=True)
        status = "Deafened"
        em = Embed(title="Voice Status Changed", description=f"{member.mention} was {status.lower()} by {ctx.author.mention}.", color=Color.light_gray())
        em.set_footer(text=f"Deafened by {ctx.author.name} | {timestamp(ctx)}", icon_url=ctx.author.avatar)
        await ctx.send(embed=em)

    @commands.hybrid_command()
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.has_permissions(deafen_members=True)
    @commands.bot_has_permissions(deafen_members=True)
    async def undeafen(self, ctx: commands.Context, member: discord.Member):
        """Undeafens user from all Voice Channels 📢
        If defened already."""
        await ctx.send(embed= Embed(description="This command is yet to be made :/"))
        
        
    @commands.hybrid_command()
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def clean(self, ctx: commands.Context, amount: int = 5):
        """Deletes given no of messages from the channel."""
        deleted = await ctx.channel.purge(limit=amount + 1)
        await ctx.send(embed=Embed(description=f"Deleted {len(deleted) - 1} messages."), delete_after=5)

    @commands.hybrid_command()
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def slowmode(self, ctx: commands.Context, channel: discord.TextChannel, seconds: int):
        """Adds Slowmode to the given channel. Use slowmode #channel 0 to remove slowmode"""
        await channel.edit(slowmode_delay=seconds)
        await ctx.send(embed = Embed(title = f"Slowmode set to `{seconds}` seconds in {channel.mention}"))

    @commands.hybrid_command()
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def purge(self, ctx: commands.Context, amount: int = 5):
        """Deletes given no of messages from the channel."""
        deleted = await ctx.channel.purge(limit=amount + 1)
        await ctx.send(embed = Embed(title=f"Purged {len(deleted) - 1} messages."), delete_after=5)

    @commands.hybrid_command()
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def lock(self, ctx: commands.Context, minutes: int = 0):
        """Locks the current channel 🔒  
        Prevents members from sending messages.
        However members with special permission can stil send messages.
        If time is provided unlocks automatically after the expiry time otherwise remains locked unless unlocked with the `unlock` command."""
        await ctx.send(embed= Embed(description="This command is yet to be made :/"))


    @commands.hybrid_command()
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def unlock(self, ctx: commands.Context):
        """Unlocks the current channel 🔓  
        Restores chat access for members."""
        await ctx.send(embed= Embed(description="This command is yet to be made :/"))

        
    @commands.hybrid_command()
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(administrator=True)
    async def set_rank_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        """Sets the rank update channel 📊  
        Displays level-up and XP progress here."""
        Server_Settings[str(ctx.guild.id)]["rank_channel"] = channel.id
        em = Embed(title="Rank Channel Set :white_check_mark:", description="Rank channel set successfully.\nNow everyone can start gaining xp point on every message, voice and activities.\nFor more details and customization visit [Kasturi_Methi.com](https://www.kasturi_methi.com/kelly)", color= Color.red())
        await ctx.send(embed=em)

    @commands.hybrid_command()
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(administrator=True)
    async def set_welcome_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        """Sets the welcome message channel 🎉  
        Greets new members automatically here.
        Sets up custom Welcome Message and design it."""
        Server_Settings[str(ctx.guild.id)]["join/leave_channel"] = channel.id
        em = Embed(title="Welcome Channel Set :white_check_mark:", description=f"Welcome Channel set successfully.\nNow you'll recieve exclusive messages on members joining and leaving the server in {channel.mention}\nFor more details and customization visit [Kasturi_Methi.com](https://www.kasturi_methi.com/kelly)", color= Color.red())
        await ctx.send(embed=em)

    @commands.hybrid_command()
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(administrator=True)
    async def set_social_channel(self, ctx: commands.Context):
        """Sets the social media updates channel 🌐  
        Posts updates from YouTube, Instagram, Twitter."""
        await ctx.send(embed= Embed(description="This command is yet to be made :/"))
 

async def setup(bot):
    await bot.add_cog(Moderation(bot))
    print("Loaded cogs: Moderation")
