from __init__ import *

async def hierarchy_check(ctx, member):
    if member.id == ctx.guild.owner_id:
        await ctx.reply(embed = Embed(title="❌ Cannot take action on server owner.", color = Color.red()))
        return False
    if member.top_role >= ctx.author.top_role:
        await ctx.reply(embed = Embed(title="❌ That user has higher or equal role than you.", color = Color.red()))
        return False
    if member.top_role >= ctx.guild.me.top_role:
        await ctx.reply(embed = Embed(title="❌ I cannot act on that user due to role hierarchy.", color = Color.red()))
        return False
    return True

class Moderation(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
    
    # ===== Kelly-Only Mute =====

    @commands.hybrid_command(aliases=["kelly_mute", "kmute"])
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def mute_from_kelly(self, ctx: commands.Context, member: discord.Member, minutes, *, reason: str):
        """Temporarily prevents a user from chatting with Kelly, not server-wide."""
        until = (datetime.now(UTC) + timedelta(minutes=minutes)).isoformat()
        Server_Settings[str(ctx.guild.id)]["muted"][str(member.id)] = until

        embed = action_embed(ctx,
            "🔇 Kelly Chat Mute Applied",
            f"{member.mention} has been muted for **{minutes} minutes**.\n**Reason:** {reason}",
            member, Color.pink(), text=f"Kelly Muted by {ctx.author.name}"
        )
        await ctx.send(embed=embed)

    # ===== Server Mute =====

    @commands.hybrid_command(aliases=[])
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def mute(self, ctx: commands.Context, member: discord.Member, minutes: int, *, reason: str):
        """Server mute — prevents member from sending messages."""
        duration = timedelta(minutes=minutes)
        await member.timeout(duration, reason=reason)

        embed_dm = Embed(title=f"You have been muted in {ctx.guild.name}",description=f"**Reason:** {reason}\nPlease follow server rules.",color=Color.red())
        embed_dm.set_thumbnail(url=ctx.guild.icon)
        await safe_dm(member, embed_dm)

        embed = action_embed(ctx,
            "🔇 Member Muted",
            f"{member.mention} muted for **{minutes} minutes**.\n**Reason:** {reason}",
            member, Color.pink(), text=f"Muted by {ctx.author.name}"
            )
        await ctx.send(embed=embed)

    # ===== Kelly-Only Unmute =====

    @commands.hybrid_command(aliases=["kelly_unmute", "kunmute"])
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def unmute_from_kelly(self, ctx: commands.Context, member: discord.Member, *, reason: str = "No reason provided"):
        """Removes Kelly-only chat mute."""
        muted = Server_Settings[str(ctx.guild.id)]["muted"]
        if str(member.id) not in muted:
            return await ctx.send("⚠️ That user is not muted from Kelly.")

        del Server_Settings[str(ctx.guild.id)]["muted"][str(member.id)]

        embed = action_embed(ctx,
            "🔊 Kelly Chat Unmuted",
            f"{member.mention} can now talk to Kelly again.\n**Reason:** {reason}",
            member, Color.green(), text = "Unmuted by {ctx.author.name}"
        )
        await ctx.send(embed=embed)
        
        embed = action_embed(ctx, "🔊 Member Unmuted from Kelly Chat", f"You can chat with Kelly again in any server. Please be respectful and follow the chat rules and policy.", member, Color.green(), text= f"Kelly Unmuted by {ctx.author.name}" )
        await safe_dm(member, embed)

    # ===== Server Unmute =====

    @commands.hybrid_command()
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def unmute(self, ctx: commands.Context, member: discord.Member, *, reason: str):
        """Restores user's chat permissions server-wide."""
        if not member.timed_out_until:
            return await ctx.send("⚠️ That member is not muted.")

        await member.edit(timed_out_until=None, reason=reason)

        embed_dm = action_embed(ctx,
            f"You have been Unmuted in {ctx.guild.name}",
            f"**Reason:** {reason}",
            member, Color.green(), text=f"Unmuted by {ctx.author.name}", thumbnail= ctx.guild.icon)
        await safe_dm(member, embed_dm)

        embed = action_embed(ctx, "🔊 Member Unmuted", f"{member.mention} is unmuted.", member, Color.green(), text= f"Unmuted by {ctx.author.name}")
        await ctx.send(embed=embed)

    # ===== Kick =====

    @commands.hybrid_command()
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx: commands.Context, member: discord.Member, *, reason: str):
        """Kick a member from the server."""
        if not await hierarchy_check(ctx, member):
            return
            
        embed_dm = action_embed(ctx, f"You were kicked from {ctx.guild.name}", f"**Reason:** {reason}\nPlease Follow the guild rules and regulations.", member, Color.red(), text = f"Kicked by {ctx.author.name}", thumbnail= ctx.guild.icon)
        await safe_dm(member, embed_dm)

        await ctx.guild.kick(member, reason=reason)

        embed = action_embed(ctx,
            "👢 Member Kicked",
            f"{member.mention} was kicked.\n**Reason:** {reason}",
            member, Color.pink(), text= f"Kicked by {ctx.author.name}", thumbnail = ctx.guild.icon
        )
        await ctx.send(embed=embed)

    # ===== Warn =====

    @commands.hybrid_command()
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def warn(self, ctx, member: discord.Member, *, reason: str):
        """Send official warning to a member."""
        if not await hierarchy_check(ctx, member):
            return
            
        embed_dm = action_embed(ctx, f"You were warned in {ctx.guild.name}",f"**Reason:** {reason}", member, Color.orange(), text = f"Warning by {ctx.author.name}", thumbnail = ctx.guild.icon)
        await safe_dm(member, embed_dm)

        embed = action_embed(ctx, "⚠️ Member Warned", f"{member.mention}\n**Reason:** {reason}", member, Color.orange(), text = f"Warning by {ctx.author.name}")
        await ctx.send(embed=embed)
        
        if Server_Settings[str(ctx.guild.id)]["warn"].get(str(member.id)):
            Server_Settings[str(ctx.guild.id)]["warn"][str(member.id)] += 1
        else:
            Server_Settings[str(ctx.guild.id)]["warn"][str(member.id)] = 1
        if Server_Settings[str(ctx.guild.id)].get("warn_action", {}):
            warn_action =Server_Settings[str(ctx.guild.id)].get("warn_action")
            warn_no = Server_Settings[str(ctx.guild.id)]["warn"][str(member.id)]
            if str(warn_no) not in warn_action:
                return
            action = warn_action[str(warn_no)]
            if "Mute" in action:
                await ctx.invoke(ctx.bot.get_command("mute"), member = member, minutes = int(action.split()[2]), reason = "Warn Limit Exceeded")
            elif "Kick" in action:
                await ctx.invoke(ctx.bot.get_command("kick"), member = member, reason = "Warn Limit Exceeded")
            elif "Ban" in action:
                await ctx.invoke(ctx.bot.get_command("ban"), member = member, reason = "Warn Limit Exceeded")
            elif "Assign Role" in action:
                try:
                    role = await member.guild.fetch_role(int(action.split()[2]))
                    await ctx.invoke(ctx.bot.get_command("assignrole"), member = member, role = role)
                except:
                    await ctx.send("Cannot assign role ```{action.split()[2]}``` on warn limit exceed. Please report this issue or Reset warn action using `k warn_action`")
        

    @commands.hybrid_command()
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.has_permissions(manage_roles = True, moderate_members=True)
    @commands.bot_has_permissions(manage_roles = True, moderate_members=True)
    async def warn_action(self, ctx):
        """Adds Warn Infringement action when warn limit hits. Warn Automated actions can be : Mute, Kick, Ban, Assign Role"""
        warn_no_select = Select(custom_id="warn_no", placeholder="Select Warn Limit", options=[SelectOption(label=str(i),value=str(i)) for i in range(1,11)], max_values=1, min_values=1)
        actions = ["Mute", "Kick", "Ban", "Assign Role"]
        action_select = Select(custom_id="action", placeholder="Select Tirgger Action", options=[SelectOption(label=str(i),value=str(i)) for i in actions], max_values=1, min_values=1, disabled = True)
        mute_duration_select = Select(custom_id="mute_duration", placeholder="Select Mute Duration Minutes", options=[SelectOption(label=str(i),value=str(i)) for i in range(5,61, 5)], max_values=1, min_values=1)
        roles = [SelectOption(label=role.name,value=str(role.id)) for role in ctx.guild.roles if role < ctx.author.top_role and role < ctx.guild.me.top_role and not "everyone" in role.name]
        if not roles:
            role_add_select = Select(custom_id="role_add", placeholder="Role not available", disabled= True, options= [SelectOption(label="No role", value="no val")], max_values=1, min_values=1)
        else:
            role_add_select = Select(custom_id="role_add", placeholder="Select Role to Add", options=roles, max_values=1, min_values=1)
        add = Button(style = ButtonStyle.green, label= "Add", custom_id="add", disabled = True)
        done = Button(style = ButtonStyle.secondary, label= "Done", custom_id="done")
       
        view = View(timeout = 45)
        view.add_item(warn_no_select)
        view.add_item(action_select)
        view.add_item(add)
        async def timeout():
            nonlocal msg, em, view 
            for children in view.children:
                children.disabled = True
            em.color = Color.light_grey()
            await msg.edit(embed=em, view=view)
        
        warn_action = Server_Settings[str(ctx.guild.id)].get("warn_action", {})
        warn_action_text = ""
        if warn_action:
            for no, action in warn_action.items():
                if "Role" in action:
                    try:
                        role = await ctx.guild.fetch_role(int(action.split()[2]))
                        action = f"Assign Role {role.mention}"
                    except:
                        pass
                warn_action_text += f"{no} - {action.title()}\n"
        else:
            warn_action_text = "No action set"
        
        em = Embed(title="Set Warn Action", description= f"Set automated actions that will excey when user exeeds warn limit. You can set more than one action.\n**Warn Actions:**\n```{warn_action_text}```", color = Color.pink())
        em.set_footer(text= f"Warn Action setup by {ctx.author.name} | {timestamp(ctx)}", icon_url = ctx.author.avatar)
        
        async def on_warn_no_select(interaction: Interaction):
            if interaction.user.id != ctx.author.id:
                await interaction.response.send_message(embed = Embed(description= "This interaction is not for you", color = Color.red()), ephemeral= True)
                return
            nonlocal em, view, add, done, warn_no_select, action_select, mute_duration_select, role_add_select
            values = interaction.data.get("values", [])
            for option in warn_no_select.options:
                option.default = option.value in values
            action_select.disabled = False
            
            await interaction.response.edit_message(view=view)
        
        async def on_action_select(interaction: Interaction):
          try:
            if interaction.user.id != ctx.author.id:
                await interaction.response.send_message(embed = Embed(description= "This interaction is not for you", color = Color.red()), ephemeral= True)
                return
            nonlocal em, view, add, done, warn_no_select, action_select, mute_duration_select, role_add_select
            values = interaction.data.get("values", [])
            for option in action_select.options:
                option.default = option.value in values
            view.clear_items()
            view.add_item(warn_no_select)
            view.add_item(action_select)
            if "Mute" in values:
                view.add_item(mute_duration_select)
            elif "Assign Role" in values:
                view.add_item(role_add_select)
            view.add_item(add)
            add.disabled = False
            
            await interaction.response.edit_message(view=view)
          except Exception as e:
            await interaction.client.get_user(894072003533877279).send(e)
                
        async def on_mute_duration_select(interaction: Interaction):
            if interaction.user.id != ctx.author.id:
                await interaction.response.send_message(embed = Embed(description= "This interaction is not for you", color = Color.red()), ephemeral= True)
                return
            nonlocal em, view, add, done, warn_no_select, action_select, mute_duration_select, role_add_select
            values = interaction.data.get("values", [])
            for option in mute_duration_select.options:
                option.default = option.value in values
            add.disabled = False
            
            await interaction.response.edit_message(view=view)
        
        async def on_role_add_select(interaction: Interaction):
            if interaction.user.id != ctx.author.id:
                await interaction.response.send_message(embed = Embed(description= "This interaction is not for you", color = Color.red()), ephemeral= True)
                return
            nonlocal em, view, add, done, warn_no_select, action_select, mute_duration_select, role_add_select
            values = interaction.data.get("values", [])
            for option in role_add_select.options:
                option.default = option.value in values
            add.disabled = False
            
            await interaction.response.edit_message(view=view)
        
        async def on_add(interaction: Interaction):
            if interaction.user.id != ctx.author.id:
                await interaction.response.send_message(embed = Embed(description= "This interaction is not for you", color = Color.red()), ephemeral= True)
                return
            nonlocal em, view, add, done, warn_no_select, action_select, mute_duration_select, role_add_select
            if add.label == "Add More":
                view.clear_items()
                view.add_item(warn_no_select)
                view.add_item(action_select)
                view.add_item(add)
                add.label = "Add"
                add.disabled = True
                
                await interaction.response.edit_message(embed = em, view=view)
                return
            values = []
            for select in [warn_no_select, action_select, mute_duration_select, role_add_select]:
                for option in select.options:
                    if option.default:
                        option.default = False
                        values.append(option.value)
                        break
                else:
                    values.append(None)
                    
            warn_action = Server_Settings[str(ctx.guild.id)].get("warn_action", [])
            text = values[1]
            if "Mute" in text:
                text += f" for {values[2]} minutes"
            elif "Assign Role" in text:
                try:
                    role = await ctx.guild.fetch_role(int(value[3]))
                    role = role.mention
                except:
                    role = values[3]
                text += f" {role}"
            warn_action[values[0]] = text
            warn_action_text = ""
            for no, action in warn_action.items():
                warn_action_text += f"{no} - {action.title()}\n"
            Server_Settings[str(ctx.guild.id)]["warn_action"] = warn_action
            
            em = Embed(title="Set Warn Action", description= f"Set automated actions that will excey when user exeeds warn limit. You can set more than one action.\n**Warn Actions:**\n```{warn_action_text}```", color = Color.pink())
            em.set_footer(text= f"Warn Action setup by {ctx.author.name} | {timestamp(ctx)}", icon_url = ctx.author.avatar)
        
            add.label = "Add More"
            view.clear_items()
            view.add_item(done)
            view.add_item(add)
            
            await interaction.response.edit_message(embed = em, view=view)
        
        async def on_done(interaction: Interaction):
            if interaction.user.id != ctx.author.id:
                await interaction.response.send_message(embed = Embed(description= "This interaction is not for you", color = Color.red()), ephemeral= True)
                return
  
            await interaction.response.edit_message(view=None)
        
        view.on_timeout = timeout
        warn_no_select.callback = on_warn_no_select
        action_select.callback = on_action_select
        role_add_select.callback = on_role_add_select
        mute_duration_select.callback = on_mute_duration_select
        add.callback = on_add
        done.callback = on_done
        
        msg = await ctx.reply(embed = em, view = view)
    
    # ===== BAN / UNBAN ==== 

    @commands.hybrid_command(aliases= [])
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx: commands.Context, member: discord.Member, *, reason: str):
        """Bans a member permanently 🚫  
        Stops them from rejoining until unbanned.
        Moderators Only - Please consider case properly before using this command."""
        if not await hierarchy_check(ctx, member):
            return
            
        em = action_embed(ctx, "Member Banned", f"{member.name} was banned by {ctx.author.mention}.\n**Reason:** {reason}.",member, color=Color.pink(), text=f"Banned by {ctx.author.name}")
        em.set_footer(text=f"Banned by {ctx.author.name} | {timestamp(ctx)}", icon_url=ctx.author.avatar)
        
        await ctx.send(embed=em)
        
        await ctx.guild.ban(user=member, reason=reason, delete_message_days=0)

    @commands.hybrid_command(aliases=["kelly_ban", "kban"])
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban_from_kelly(self, ctx: commands.Context, member: discord.Member, *, reason: str):
        """Just Bans a member from ever Chatting to Kelly Not from Server 🚫  
        Now user can never chat with Kelly, unless unbanned."""
        if not await hierarchy_check(ctx, member):
            return
            
        embed = Embed(title = f"You have been Banned from Kelly Chat", description = f"**Reason**: {reason}\n**Please refrain from sending messages like this.**", color = Color.red())
        embed.set_footer(text=f"Kelly Ban by {ctx.author.name} | {timestamp(ctx)}", icon_url=ctx.author.avatar)
        
        await safe_dm(member, embed)
        
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
                return
                
        await ctx.send("User not found in ban list.")

    @commands.hybrid_command(aliases=["kelly_unban", "kunban"])
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def unban_from_kelly(self, ctx: commands.Context, member: discord.Member, *, reason: str):
        """Unbans a user by name or ID 🔓 from Kelly. 
        Now they can start chatting with Kelly again.
        This is not related with server."""
        embed = Embed(title = f"You have been Unbanned from Kelly Chat", description = f"**Reason**: {reason}\n**Please refrain from sending messages like this.**", color = Color.red())
        embed.set_footer(text=f"Kelly Umban by {ctx.author.name} | {timestamp(ctx)}", icon_url=ctx.author.avatar)
        
        await safe_dm(member, embed)
        
        Server_Settings[str(ctx.guild.id)]["block_list"].remove(member.id)
        em = Embed(
            title="Member Unbanned from Kelly Talk",
            description=f"{member.mention} was unbanned from kelly talking.\n**Reason: ** {reason}\nYou can Chat with Kelly using `kelly hi`.\nPlease be respectful this time.",
            color=Color.orange()
        )
        em.set_footer(text=f"Unbanned by {ctx.author.name} | {timestamp(ctx)}", icon_url=ctx.author.avatar)
        em.set_author(name=member.name,icon_url=member.avatar)
        await ctx.send(embed=em)
    
    # ===== ASSIGN ROLE / REMOVE ROLE ====
    
    @commands.hybrid_command()
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def assignrole(self, ctx: commands.Context, member: discord.Member, role: discord.Role):
        """Assigns given role to the user.
        Given role hierarchy should be equivalent to or less than your role."""
        if not await hierarchy_check(ctx, member):
            return
        if role > ctx.author.top_role:
            return await ctx.reply(embed = Embed(title="❌ That role is higher than your own role.", color = Color.red()))
        if role > ctx.guild.me.top_role:
            return await ctx.reply(embed = Embed(title="❌ I cannot add this role due to role hierarchy.", color = Color.red()))
            
        embed = Embed(title = f"You have been Awared a role in {ctx.guild.name}", description = f"**Role**: **{role.name}**", color = role.color)
        embed.set_footer(text=f"Assigned Role by {ctx.author.name} | {timestamp(ctx)}", icon_url=ctx.author.avatar)
        
        await safe_dm(member, embed)
        
        await member.add_roles(role)
        em = Embed(title="Role Assigned", description=f"{role.mention} assigned to {member.mention}", color=Color.green())
        em.set_footer(text=f"Role Assigned by {ctx.author.name} | {timestamp(ctx)}", icon_url=ctx.author.avatar)
        await ctx.send(embed=em)
        
    @commands.hybrid_command()
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def removerole(self, ctx: commands.Context, member: discord.Member, role: discord.Role):
        """Removes given role from the user.
        Given role hierarchy should benless than your role."""
        if not await hierarchy_check(ctx, member):
            return
        if role >= ctx.author.top_role:
            return await ctx.reply(embed = Embed(title="❌ That role is higher or equal than your own role.", color = Color.red()))
        if role >= ctx.guild.me.top_role:
            return await ctx.reply(embed = Embed(title="❌ I cannot add this role due to role hierarchy.", color = Color.red()))
            
        embed = Embed(title = f"You have been detained from your Role in {ctx.guild.name}", description = f"**Role**: **{role.name}**", color = role.color)
        embed.set_footer(text=f"Role Removed by {ctx.author.name} | {timestamp(ctx)}", icon_url=ctx.author.avatar)
        
        await safe_dm(member, embed)
        
        await member.remove_roles(role)
        em = Embed(title="Role Removed", description=f"{role.mention} removed from {member.mention}", color=Color.green())
        em.set_footer(text=f"Role Removed by {ctx.author.name} | {timestamp(ctx)}", icon_url=ctx.author.avatar)
        await ctx.send(embed=em)

    # ===== DEAFEN / UNDEAFEN =====

    @commands.hybrid_command()
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.has_permissions(deafen_members=True)
    @commands.bot_has_permissions(deafen_members=True)
    async def deafen(self, ctx: commands.Context, member: discord.Member, minutes: int = 0):
        """Deafens a member from all voice chat 🔇  
        If minutes is provided auto undeafens after expiry else manually undeafen required."""
        if not await hierarchy_check(ctx, member):
            return
            
        # Apply deaf
        await member.edit(deafen=True)

        # Auto-undeafen timeout
        if minutes > 0:
            async def undeafen_later():
                await asyncio.sleep(minutes * 60)
                try:
                    await member.edit(deafen=False)
                except:
                    pass
         
            asyncio.create_task(undeafen_later())

        # Embed
        em = Embed(
            title="Member Deafened 🔇",
            description=f"{member.mention} has been deafened by {ctx.author.mention}.",
            color=Color.dark_gray()
        )
        if minutes > 0:
            em.add_field(name="Duration", value=f"{minutes} minutes")

        if channel:
            em.add_field(name="Voice Channel", value=channel.mention)
  
        em.set_footer(text=f"Deafened by {ctx.author.name} | {timestamp(ctx)}", icon_url=ctx.author.avatar)
    
        await ctx.send(embed=em)


    @commands.hybrid_command()
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.has_permissions(deafen_members=True)
    @commands.bot_has_permissions(deafen_members=True)
    async def undeafen(self, ctx: commands.Context, member: discord.Member):
        """Undeafens user from voice channels 📢"""
   
        await member.edit(deafen=False)

        em = Embed(
            title="Member Undeafened 📢",
            description=f"{member.mention} has been undeafened by {ctx.author.mention}.",
            color=Color.green()
        )
        em.set_footer(text=f"Undeafened by {ctx.author.name} | {timestamp(ctx)}", icon_url=ctx.author.avatar)

        await ctx.send(embed=em)
    
    # ===== CLEAN / PURGE / SLOWMODE ====
    
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
        await ctx.send(embed = Embed(title=f"Purged {len(deleted) - 1} messages."), delete_after=6)

    # ===== LOCK / UNLOCK ====
    
    @commands.hybrid_command()
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def lock(self, ctx: commands.Context, minutes: int = 0):
        """Locks the current channel 🔒  
         If minutes are given, unlocks automatically after the time."""

        channel = ctx.channel
        overwrite = channel.overwrites_for(ctx.guild.default_role)
 
        if overwrite.send_messages is False:
            return await ctx.send(embed=Embed(description="🔒 This channel is already locked."))

        overwrite.send_messages = False
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)

        em = Embed(
            title="Channel Locked 🔒",
            description=f"{channel.mention} has been locked by {ctx.author.mention}.",
            color=Color.red()
        )

        if minutes > 0:
            em.add_field(name="Auto-Unlock", value=f"{minutes} minutes")
 
            async def auto_unlock():
                await asyncio.sleep(minutes * 60)
                try:
                    overwrite = channel.overwrites_for(ctx.guild.default_role)
                    overwrite.send_messages = None
                    await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
                except:
                    pass

            asyncio.create_task(auto_unlock())

        await ctx.send(embed=em)

    @commands.hybrid_command()
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def unlock(self, ctx: commands.Context):
        """Unlocks the current channel 🔓"""

        channel = ctx.channel
        overwrite = channel.overwrites_for(ctx.guild.default_role)

        if overwrite.send_messages is None or overwrite.send_messages is True:
            return await ctx.send(embed=Embed(description="🔓 This channel is already unlocked."))

        overwrite.send_messages = None
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)

        em = Embed(
            title="Channel Unlocked 🔓",
            description=f"{channel.mention} has been unlocked by {ctx.author.mention}.",
            color=Color.green()
        )

        await ctx.send(embed=em)
        
    # ===== SET UP CHANNELS ====
    
    @commands.hybrid_command()
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(manage_guild=True)
    async def set_rank_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        """Sets the rank update channel 📊  
        Displays level-up and XP progress here."""
        Server_Settings[str(ctx.guild.id)]["rank_channel"] = channel.id
        em = Embed(title="Rank Channel Set :white_check_mark:", description="Rank channel set successfully.\nNow everyone can start gaining xp point on every message, voice and activities.\nFor Automatic Rank rewards use `k rank_reward`", color= Color.green())
        await ctx.send(embed=em)

    @commands.hybrid_command()
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(manage_guild=True)
    async def set_welcome_channel(self, ctx: commands.Context, channel: discord.TextChannel = None):
        """Sets the welcome message channel 🎉  
        Greets new members automatically here.
        Sets up custom Welcome Message and design it."""
        welcome_theme_no = 1
        welcome_message = ""
        welcome_channel = channel.id if channel else None
        
        class WelcomeModal(discord.ui.Modal):
            def __init__(self):
                super().__init__(title="Set Welcome Message")
                self.input_box = TextInput(label="Edit the Format and Submit.",custom_id="welcome", default= "Welcome to <guild_name>\n✦ <Text 1>- eg: Take Roles\n✦ <Text 2> - eg Read Rules\n✦ <Text 3> - eg Have Fun Here", required= True, min_length=2, max_length=512, style=TextStyle.paragraph)
                self.add_item(self.input_box)
            
            async def on_submit(self, interaction: Interaction):
              try:
                nonlocal welcome_message, em, view, proceed_button, channel_select, msg, channel_select2, next_button
                welcome_message = self.input_box.value
                channel_select2.row = 0
                channel_select.row = 1
                proceed_button.row = 2
                proceed_button.label = "Select Welcome Channel"
                proceed_button.disabled = True
                display_msg = welcome_message[welcome_message.find('\n')+1:]
                em.description = f"Welcome message set sucessfully.\n Now First select your `redirect to` channels orderwise. These are the channels that each line in welcome message will redirect to. ```{display_msg}```Next select the channel in which you want to send welcome messages."
                proceed_button.callback = next_button
                proceed_button.disabled = True
                view.clear_items()
                view.add_item(channel_select2)
                view.add_item(channel_select)
                view.add_item(proceed_button)
                await msg.edit(embed=em, view=view)
                await interaction.response.defer()
                  
              except Exception as e:
                await interaction.client.get_user(894072003533877279).send(e)
                
        go_left = Button(style=ButtonStyle.secondary, custom_id= "go_left", disabled=True, row=0, emoji=discord.PartialEmoji.from_str("<:leftarrow:1427527800533024839>"))
        go_right = Button(style=ButtonStyle.secondary, custom_id= "go_right", row=0, emoji=discord.PartialEmoji.from_str("<:rightarrow:1427527709403119646>"))
        proceed_button = Button(style=ButtonStyle.success ,label="Select Theme", custom_id="proceed", row=0)
        channel_select = Select(custom_id="channel", placeholder="Select your Channel", options=[SelectOption(label=f"#{channel.name}",value=str(channel.id)) for channel in ctx.guild.text_channels], max_values=1, min_values=1)
        if channel:
            for option in channel_select.options:
                if option.value == str(channel.id):
                    option.default = True
                    break
        channel_select2 = Select(custom_id="channel_selector", placeholder="Select your redirect to channels in Order.", options=[SelectOption(label=f"#{channel.name}",value=str(channel.id)) for channel in ctx.guild.text_channels], max_values= 5 if len(ctx.guild.text_channels) > 5 else len(ctx.guild.text_channels), min_values=1)
        
        view = View(timeout = 45)
        view.add_item(go_left)
        view.add_item(proceed_button)
        view.add_item(go_right)
        
        async def process_buttons(interaction: discord.Interaction):
            if interaction.user.id != ctx.author.id:
                await interaction.response.send_message(embed = Embed(description= "This interaction is not for you", color = Color.red()), ephemeral= True)
                return 
            nonlocal WelcomeModal
            modal = WelcomeModal()
            await interaction.response.send_modal(modal)
                
        async def next_button(interaction: Interaction):
            if interaction.user.id != ctx.author.id:
                await interaction.response.send_message(embed = Embed(description= "This interaction is not for you", color = Color.red()), ephemeral= True)
                return 
            nonlocal welcome_message, channel_select, channel_select2, welcome_theme_no, em, welcome_channel
            temp = welcome_message.split("\n")[1:]
            welcome_message = welcome_message.split("\n")[0]
            values = [option.value for option in channel_select2.options if option.default]
            for index, i in enumerate(temp):
                if index < len(values):
                    welcome_message += f"\n{i.split()[0]} [**{i[2:]}**](https://discord.com/channels/{ctx.guild.id}/{values[index]})"
                else:
                    welcome_message += f"\n{i.split()[0]} **{i[2:]}**"
            for option in channel_select.options:
                if option.default:
                    welcome_channel = int(option.value)
                    option.default = False
                    break
            em.description= "Welcome channel set up perfectly.\nYou can have a preview here:"
            em.set_image(url=None)
            part1 = welcome_message.split("\n")[0]
            em2 = Embed(title= f"<:heeriye:1428773558062153768> **{part1}**", description="\n".join(welcome_message.split("\n")[1:]), color = Color.dark_gray())
            em2.set_author(name= ctx.author.name, icon_url= ctx.author.avatar)
            em2.set_thumbnail(url= ctx.author.avatar)
            em2.set_image(url= f"https://raw.githubusercontent.com/happyharsh-codes/Kasturi/refs/heads/main/assets/welcome_message_{welcome_theme_no}.gif")
            em2.set_footer(text=f"﹒ ﹒ ⟡ {ctx.guild.member_count} Members Strong 💪🏻 | At {datetime.now(UTC).strftime('%m-%d %H:%M')}")
            Server_Settings[str(ctx.guild.id)]["welcome_channel"] = welcome_channel
            Server_Settings[str(ctx.guild.id)]["welcome_image"] = welcome_theme_no
            Server_Settings[str(ctx.guild.id)]["welcome_message"] = welcome_message
            view.timeout = None
            await interaction.response.edit_message(embeds=[em,em2], view = None)
           
        async def timeout():
            nonlocal msg, em, view 
            for children in view.children:
                children.disabled = True
            em.color = Color.light_grey()
            await msg.edit(embed=em, view=view)

        async def go_callback(interaction: Interaction):
            if interaction.user.id != ctx.author.id:
                await interaction.response.send_message(embed = Embed(description= "This interaction is not for you", color = Color.red()), ephemeral= True)
                return 
            nonlocal welcome_theme_no, go_left, go_right,em
            if interaction.data["custom_id"] == "go_left":
                welcome_theme_no -= 1
            else:
                welcome_theme_no += 1
            go_left.disabled = welcome_theme_no == 1
            go_right.disabled = welcome_theme_no == 18
            em.set_image(url=f"https://raw.githubusercontent.com/happyharsh-codes/Kasturi/refs/heads/main/assets/welcome_message_{welcome_theme_no}.gif")
            await interaction.response.edit_message(embed=em, view=view)
       
        async def select_channels(interaction: Interaction):
          try:
            if interaction.user.id != ctx.author.id:
                await interaction.response.send_message(embed = Embed(description= "This interaction is not for you", color = Color.red()), ephemeral= True)
                return 
            nonlocal proceed_button, view, channel_select, channel_select2
            proceed_button.disabled = False
            selected_values = interaction.data.get("values",[])
            for val in selected_values:
                for option in channel_select.options:
                  if option.value == val:
                    option.default = True
            await interaction.response.edit_message(view=view)
          except Exception as e:
            await self.client.get_user(894072003533877279).send(e)
        
        async def select_channels2(interaction: Interaction):
            if interaction.user.id != ctx.author.id:
                await interaction.response.send_message(embed = Embed(description= "This interaction is not for you", color = Color.red()), ephemeral= True)
                return 
            nonlocal channel_select2
            selected_values = interaction.data["values"]
            for val in selected_values:
                for option in channel_select2.options:
                    if option.value == val:
                        option.default = True
            await interaction.response.defer()
        
        go_left.callback = go_callback
        go_right.callback = go_callback
        proceed_button.callback = process_buttons
        channel_select.callback = select_channels
        channel_select2.callback = select_channels2
        view.on_timeout = timeout
        
        em = Embed(color = Color.green())
        em.title="Set Welcome message"
        em.description="Set your beautiful welcome message Kelly will send whenever a new user joins the guild.\nSelect your theme from here."
        em.set_image(url="https://raw.githubusercontent.com/happyharsh-codes/Kasturi/refs/heads/main/assets/welcome_message_1.gif")
        
        msg = await ctx.reply(embed=em,view=view)

    @commands.hybrid_command()
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(manage_guild=True)
    async def set_social_channel(self, ctx: commands.Context):
        """Sets the social media updates channel 🌐  
        Posts updates from YouTube, Instagram, Twitter."""
        social_channel = 0
        class SocialModal(discord.ui.Modal):
            def __init__(self):
                super().__init__(title="Set Social Media/ Leave blank for none")
                self.input_box1 = TextInput(label="YouTube Link", custom_id="yt", placeholder="Enter your YouTube Channel Link:", required= False, min_length=0, max_length=50, style=TextStyle.short, default="idk")
                self.input_box2 = TextInput(label="Insta Id", custom_id="insta", placeholder="Enter your Insta id", required= False, min_length=0, max_length=20, style=TextStyle.short, default="ion have")
                self.input_box3 = TextInput(label="Twitter Id", custom_id="twitter", placeholder="Enter your Twitter Id: ", required= False, min_length=0, max_length=20, style=TextStyle.short, default="idgaf")
                self.add_item(self.input_box1)
                self.add_item(self.input_box2)
                self.add_item(self.input_box3)
                
            async def on_submit(self, interaction: Interaction):
              try:
                nonlocal em, view, proceed_button, msg, channel_select, social_channel
                yt = self.input_box1.value
                insta = self.input_box2.value
                twitter = self.input_box3.value
                em.title="Social Media Notification Set Successfully ✅"
                em.description=f"Now you'll get your updates in the <#{social_channel}>."
                em.set_image(url="https://raw.githubusercontent.com/happyharsh-codes/Kasturi/refs/heads/main/assets/social.png")
                Server_Settings[str(ctx.guild.id)]["social"] = {"yt": yt , "insta": insta, "twitter": twitter, "social_channel": social_channel}
                await msg.edit(embed=em, view=None)
                await interaction.response.defer()
              except Exception as e:
                await interaction.client.get_user(894072003533877279).send(e)
 
        em = Embed(color = Color.green())
        em.title="Set up Social Media Notification"
        em.description="Set up your Social Media whose updates you'll get right here on your selected channel.Enter your correct Id and then select the channel in which you want to get updates."
        em.set_image(url="https://raw.githubusercontent.com/happyharsh-codes/Kasturi/refs/heads/main/assets/social.png")
         
        proceed_button = Button(style= ButtonStyle.green, label = "Set Social Media", custom_id= "social", disabled = True)
        channel_select = Select(custom_id="channel", placeholder="Select your Channel", options=[SelectOption(label=f"#{channel.name}",value=str(channel.id)) for channel in ctx.guild.text_channels], max_values=1, min_values=1)
        view = View(timeout = 40)
        view.add_item(channel_select)
        view.add_item(proceed_button)
        
        async def timeout():
             nonlocal em, view, msg
             em.color = Color.light_grey()
             for children in view.children:
                 children.disabled = True
             await msg.edit(embed = em, view= view)
              
        async def on_click(interaction: Interaction):
            modal = SocialModal()
            await interaction.response.send_modal(modal)
            
        
        async def select_channel(interaction: Interaction):
            if interaction.user.id != ctx.author.id:
                await interaction.response.send_message(embed = Embed(description= "This interaction is not for you", color = Color.red()), ephemeral= True)
                return 
            nonlocal proceed_button, view, channel_select, social_channel
            proceed_button.disabled = False
            selected_values = interaction.data.get("values",[])
            for val in selected_values:
                for option in channel_select.options:
                  if option.value == val:
                    option.default = True
                    social_channel = int(val)
            await interaction.response.edit_message(view=view)

        view.on_timeout = timeout
        proceed_button.callback = on_click
        channel_select.callback = select_channel

        msg = await ctx.reply(embed=em, view=view)
         
    # ===== AUTOMOD SETUP ====
    @commands.hybrid_command()
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(manage_guild=True)
    async def automod(self, ctx: commands.Context):
        """Sets the automod services for the guild."""
        feature = {
            "custom_words_block": "Deletes custom words",
            "chat_rate_limiter": "Limits message to avoid flooding.",
            "caps_block": "Blocks excessive capital letters.",
            "emoji_spam": "Blocks mass emoji spam",
            "link_filter": "Blocks harmful or unauthorized links.",
            "nsfw_filter": "Blocks NSFW text or images.",
            "toxicity_filter": "Detects toxic messages (AI powered).",
            "duplicate_detector": "Stops repeated / similar messages.",
            "mass_mention_block": "Blocks mass mention."
        }
        raid_nuke = [
            "Anti-Message Spam",
            "Anti Rapid Join",
            "Anti-Server Nukes",
            "Auto Lockdown",
            "Auto Unverified Mass Kick/Ban",
            "Alerts to Moderation Channel"
        ]
            
        add_btn = Button(style=ButtonStyle.green, label="Add Features", custom_id="add", disabled=True)
        skip_btn = Button(style=ButtonStyle.secondary, label="Skip", custom_id="skip")
        feature_select = Select(custom_id="feature", placeholder="Select Features to Enable", options=[SelectOption(label=i.replace("_","").title(),value=i) for i in list(feature.keys())], max_values=9, min_values=1)
        raid_nuke_select = Select(custom_id="protect", placeholder="Select Protection to Enable", options=[SelectOption(label=i,value=i) for i in raid_nuke], max_values=6, min_values=1)
        channel_select = Select(custom_id="channel", placeholder="Select your Channel", options=[SelectOption(label=f"#{channel.name}",value=str(channel.id)) for channel in ctx.guild.text_channels], max_values=1, min_values=1)

        class AutomodModal(discord.ui.Modal):
            def __init__(self, features):
                super().__init__(title="Set Automod Features")
                for feature in features:
                    if feature == "custom_words_block":
                        self.custom_words_block = TextInput(label="Custom Block Words", custom_id="block_list", placeholder="Enter Custom words separated by comma.", required= True, min_length=1, max_length=512, style=TextStyle.paragraph)
                        self.add_item(self.custom_words_block)
                    elif feature == "chat_rate_limiter":
                        self.chat_rate_limiter = Select(custom_id="chat_rate_limit", placeholder="Select Chat Rate every 5 seconds", required= True, min_values=1, max_values=1, options = [SelectOption(label=str(i), value=str(i)) for i in range(1,11)])
                        self.add_item(self.chat_rate_limiter)
                    elif feature == "emoji_spam":
                        self.emoji_spam = Select(custom_id="emoji_spam", placeholder="Select Emoji Limit per message", required= True, min_values=1, max_values=1, options = [SelectOption(label=str(i), value=str(i)) for i in range(3,11)])
                        self.add_item(self.emoji_spam)
                    elif feature == "link_filter":
                        self.link_filter = Select(custom_id="link_filter", placeholder="Select Link filter type", required= True, min_values=1, max_values=1, options = [SelectOption(label=str(i), value=str(i)) for i in ["All Links", "Suspicious Links"]])
                        self.add_item(self.link_filter)
                    elif feature == "mass_mention_block":
                        self.mass_mention_block = Select(custom_id="mass_mention", placeholder="Set Mass mention Limit", required= True, min_values=1, max_values=1, options = [SelectOption(label=str(i), value=str(i)) for i in range(3,8)])
                        self.add_item(self.mass_mention_block)
                self.features = features
                
            async def on_submit(self, interaction: Interaction):
              try:
                nonlocal feature, view, add_btn, msg
                Server_Settings[str(ctx.guild.id)]["automod"] = {}
                selected_features = self.features
                non_features = [x for x in list(features.keys()) if x not in selected_protections]
                for feature in selected_features:
                    if feature == "custom_words_block":
                        Server_Settings[str(ctx.guild.id)]["banned_words"] = map(lambda x: x.strip(), self.custom_words_block.value.split(","))
                    elif feature == "chat_rate_limiter":
                        Server_Settings[str(ctx.guild.id)]["automod"][feature] = self.chat_rate_limiter.values[0]
                    elif feature == "emoji_spam":
                        Server_Settings[str(ctx.guild.id)]["automod"][feature] = self.emoji_spam.values[0]
                    elif feature == "link_filter":
                        Server_Settings[str(ctx.guild.id)]["automod"][feature] = self.link_filter.values[0]
                    elif feature == "mass_mention_block":
                        Server_Settings[str(ctx.guild.id)]["automod"][feature] = self.mass_mention_block.values[0]
                    else:
                        Server_Settings[str(ctx.guild.id)]["automod"][feature] = True
                for not_feature in non_features:
                    Server_Settings[str(ctx.guild.id)]["automod"][not_feature] = False
                em = msg.embeds[0]
                em.description = "Features succesfully Set"
                for i in list(feature.keys()):
                    if i in selected_features:
                        em.description += f"\n✅ {i.replace('_','').title()}"
                    else:
                        em.description += f"\n❌ {i.replace('_','').title()}"
                add_btn.label = "Continue"
                await msg.edit(embed = em, view = view)
              except Exception as e:
                await interaction.client.get_user(894072003533877279).send(e)

        page = 0
        embeds = []
        for i in range(6):
            em = Embed(title= f"Automod Setup {i+1}/5",color = Color.pink())
            em.set_footer(text=f"Automod used by {ctx.author.name} | {timestamp(ctx)} | Aura++", icon_url = ctx.author.avatar)
            if i == 0:
                descrip = ""
                em.description = "Select Features to enable:\nFor better functioning enable all our features."
                for feature_heading, feature_description in feature.items():
                    descrip += f"\n{feature_heading.replace('_','').title()}: {feature_description}"
                em.description += f"\n```{descrip}```"
            elif i == 1:
                em.description = f"Select Protection to Enable:\nPlease enable all services for the best.\n```{descrip}```"
                descrip = ""
                for raid_heading in raid_nuke:
                    descrip += f"\n• {raid_heading.title()}"
                em.description += f"```{descrip}```"
            elif i == 2:
                em.description = "Select Moderation Logging Channel\nSelect the logging channel in which Kelly will send all updates and all logging and auto action reports.\n```• AutoMod action\n• Server / User Modify details\n•Punishment Triggered\n• Kelly Updates```"
            elif i == 3:  
                em.description = "Select Punishment Method\nPunishment method automatically handles when trigger is hit and punishment gradually increase on more infringement. You can set Punishments via ```k warn_action``` later on."
            elif i == 4:
                em.description = "Allow Permission Access: For Auto-moderation I require these permission. Best option would be to give me all permissions.\n```• Administrator```\nOr\n```• Manage Guild, Manage Roles, Manage Webhooks\n• Manage Nicknames, Kick, Ban, Timeout Members\n• Manage Messages"
            elif i == 5:
                em.title = "Automod Successfully Set"
                em.description = "Successfully set automod rules\nYou server is protected now."
            embeds.append(em)
        
        async def next_page(inter: Interaction):
            if inter.user.id != ctx.author.id:
                return await inter.response.send_message("This is not your interaction.", ephemeral=True)
            nonlocal embeds, msg, view, page, add_btn, skip_btn, feature_select, raid_nuke_select, channel_select, raid_nuke, feature
            page += 1
            em = embeds[page-1]
            btn = inter.data.get("custom_id")
            if page == 1:
                if btn == "skip":
                    page += 1
                else:
                    nonlocal AutomodModal
                    selected_features = []
                    for option in feature_select.options:
                        if option.default:
                            selected_features.append(option.value)
                    modal = AutomodModal(selected_features)
                    await inter.response.send_modal(modal)
                    return
            if page == 2:
                view.clear_items()
                view.add_item(raid_nuke_select)
                view.add_item(add_btn)
                view.add_item(skip_btn)
                add_btn.label = "Add Protection"
                add_btn.disabled = True
            if page == 3:
                view.clear_items()
                view.add_item(channel_select)
                view.add_item(add_btn)
                view.add_item(skip_btn)
                add_btn.label = "Set Channel"
                add_btn.disabled = True
                if btn == "skip":
                    return await inter.response.edit_message(embed=em, view=view)
                selected_protections = []
                for option in raid_nuke_select.options:
                    if option.default:
                        selected_protections.append(option.value)
                Server_Settings[str(ctx.guild.id)]["protections"] = {}
                for p in raid_nuke:
                    Server_Settings[str(ctx.guild.id)]["protections"][p] = (p in selected_protections)
                
            if page == 4:
                add_btn.label = "Continue"
                view.clear_items()
                view.add_item(add_btn)
                if btn == "skip":
                    return await inter.response.edit_message(embed=em, view=view)
                selected_features = []
                for option in feature_select.options:
                    if option.default:
                        Server_Settings[str(ctx.guild.id)]["logging"] = int(option.value)
                        break
            if page == 5:
                add_btn.label = "Finish 🎉"
            if page == 6:
                view = None
            await inter.response.edit_message(embed=em, view=view)

        async def on_raid_nuke_select(inter: Interaction):
            if inter.user.id != ctx.author.id:
                return await inter.response.send_message("This is not your interaction.", ephemeral=True)
            nonlocal view, msg, add_btn, raid_nuke_select
            selected_values = inter.data.get("values",[])
            for option in raid_nuke_select.options:
                if option.value in selected_values:
                    option.default = True
            add_btn.disabled = False
            await inter.response.edit_message(embed=em, view=view)
            
            
        async def on_feature_select(inter: Interaction):
            if inter.user.id != ctx.author.id:
                return await inter.response.send_message("This is not your interaction.", ephemeral=True)
            nonlocal view, msg, add_btn, feature_select
            selected_values = inter.data.get("values",[])
            for option in feature_select.options:
                if option.value in selected_values:
                    option.default = True
            add_btn.disabled = False
            await inter.response.edit_message(embed=em, view=view)

        async def on_channel_select(inter: Interaction):
            if inter.user.id != ctx.author.id:
                return await inter.response.send_message("This is not your interaction.", ephemeral=True)
            nonlocal view, msg, add_btn, channel_select
            selected_values = inter.data.get("values",[])
            for option in channel_select.options:
                if option.value in selected_values:
                    option.default = True
            add_btn.disabled = False
            await inter.response.edit_message(embed=em, view=view)

        async def timeout():
            nonlocal view, msg
            em = msg.embeds[0]
            em.color = Color.light_grey()
            for children in view.children:
                children.disabled = True
            await msg.edit(embed = em, view= view)
              
        view = View(timeout=200)
        view.add_item(feature_select)
        view.add_item(add_btn)
        view.add_item(skip_btn)
        view.on_timeout = timeout
        add_btn.callback = next_page
        skip_btn.callback = next_page
        raid_nuke_select.callback = on_raid_nuke_select
        feature_select.callback = on_feature_select
        channel_select.callback = on_channel_select
        
        msg = await ctx.send(embed=embeds[0], view=view)
        
    # ===== RANK REWARD ====

    @commands.hybrid_command()
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(manage_guild=True)
    async def rank_reward(self, ctx: commands.Context):
        """Allows you to set up level up rank reward."""

        guild_id = str(ctx.guild.id)

        if not Server_Settings[guild_id].get("rank_channel", 0):
            return await ctx.send(embed=Embed(description=":x: You must set a Rank Channel first.\nUse `k set_rank_channel`.",color=Color.red()))

        reward_select = Select(custom_id="reward_type",placeholder="Select Reward Type",options=[SelectOption(label=i, value=i) for i in ["Role", "Cash", "Aura", "Gems", "Nitro"]],max_values=1,min_values=1,disabled=False)
        roles = [SelectOption(label=role.name,value=str(role.id)) for role in ctx.guild.roles if role < ctx.author.top_role and role < ctx.guild.me.top_role and not "everyone" in role.name]
        if not roles:
            role_select = Select(custom_id="role_add", placeholder="Role not available", disabled= True, options= [SelectOption(label="No role", value="no val")], max_values=1, min_values=1)
        else:
            role_select = Select(custom_id="role_add", placeholder="Select Role to Add", options=roles, max_values=1, min_values=1)
        add_btn = Button(style=ButtonStyle.green, label="Add", custom_id="add", disabled=True)
        done_btn = Button(style=ButtonStyle.secondary, label="Done", custom_id="done")

        class RankModal(discord.ui.Modal):
            def __init__(self, reward_type):
                super().__init__(title="Add Rank Reward")
                self.input_box = TextInput(label="Level", custom_id="level", placeholder="Enter Reward Level: 1-100", required= True, min_length=1, max_length=3, style=TextStyle.short)
                self.reward = reward_type
                self.add_item(self.input_box)
                if reward_type == "Cash":
                    self.select = TextInput(label="Cash Amount", custom_id="cash", placeholder="Enter Cash amount: (1-10000)", required= True, min_length=1, max_length=5, style=TextStyle.short)
                    self.add_item(self.select)
                elif reward_type == "Aura":
                    self.select = TextInput(label="Aura Points", custom_id="aura", placeholder="Enter Aura Points: (1-999)", required= True, min_length=1, max_length=3, style=TextStyle.short)
                    self.add_item(self.select)
                elif reward_type == "Gems":
                    self.select = TextInput(label="Gems Amount", custom_id="gems", placeholder="Enter Gems amount: (1-100)", required= True, min_length=1, max_length=3, style=TextStyle.short)
                    self.add_item(self.select)
                elif reward_type == "Nitro":
                    self.select = TextInput(label="Nitro Code", custom_id="nitro", placeholder="Enter Valid Nitro Gift Code", required= True, min_length=1, max_length=50, style=TextStyle.short)
                    self.add_item(self.select)
                
            async def on_submit(self, interaction: Interaction):
              try:
                nonlocal em, view, add_btn, done_btn, msg, reward_select, update_embed, role_select
                invalid = False
                level = self.input_box.value
                if level.isdigit() and int(level) < 101 and int(level) > 0:
                    level = int(level)
                else:
                    invalid = True
                if self.reward == "Role":
                    for option in role_select.options:
                        if option.default:
                            value = option.value
                            break
                elif self.reward == "Cash":
                    value = self.select.value
                    if value.isdigit() and int(value) <= 10000 and int(value) > 0:
                        value = int(value)
                    else:
                        invalid = True
                elif self.reward == "Aura":
                    value = self.select.value
                    if value.isdigit() and int(value) <= 999 and int(value) > 0:
                        value = int(value)
                    else:
                        invalid = True
                elif self.reward == "Gems":
                    value = self.select.value
                    if value.isdigit() and int(value) <= 100 and int(value) > 0:
                        value = int(value)
                    else:
                        invalid = True
                elif self.reward == "Nitro":
                    value = self.select.value
                if invalid:
                    for children in view.children:
                        children.disabled = True
                    await msg.edit(view=view)
                    return await inter.response.send_message(f"{ctx.author.mention}", embed=Embed(description="**Invalid Values Given**", color=Color.red()))
                
                Server_Settings[str(ctx.guild.id)]["rank_reward"][level] = [self.reward, value]
                update_embed()
            
                if add_btn.label == "Add":
                    add_btn.label = "Add More"
                    view.clear_items()
                    view.add_item(reward_select)
                    view.add_item(add_btn)
                    view.add_item(done_btn)
                await msg.edit(embed=em, view=view)
                await interaction.response.defer()
              except Exception as e:
                await interaction.client.get_user(894072003533877279).send(e)
 
        view = View(timeout=45)
        view.add_item(reward_select)
        view.add_item(add_btn)
        async def timeout():
            nonlocal em, view, msg
            fields = em.fields
            em.color = Color.light_grey()
            em.fields = fields
            for children in view.children:
                children.disabled = True
            await msg.edit(embed=em, view=view)
        view.on_timeout = timeout

        em = Embed(title="Set Rank Level-Up Rewards",description="Select a Reward that will be automatically given when users reaches a level.",color=Color.pink())

        def update_embed():
            nonlocal em, view, guild_id
            em.clear_fields()
            rank_reward = Server_Settings[guild_id].get("rank_reward", {})
        
            if rank_reward:
                txt = ""
                for level, reward in rank_reward.items():
                    if reward[0] == "Role":
                        try:
                            role = ctx.guild.get_role(int(reward[1]))
                            if role:
                                reward[1] = role.name
                        except:
                            pass
                    txt += f"• Level {level} → {reward[0]}: {reward[1]}\n"
            else:
                txt = "No rewards set yet."

            em.add_field(name="Current Rewards", value=f"```{txt}```", inline=False)

        update_embed()

        async def on_reward_select(inter: Interaction):
            if inter.user.id != ctx.author.id:
                return await inter.response.send_message("This is not your interaction.", ephemeral=True )

            selected_reward = inter.data["values"][0]
            nonlocal reward_select, add_btn, view, done_btn, role_select
            for option in reward_select.options:
                if option.value in selected_reward:
                    option.default = True
                    break
            if "Role" in selected_reward:
                view.clear_items()
                view.add_item(reward_select)
                view.add_item(role_select)
                view.add_item(add_btn)
                if add_btn.label == "Add More":
                    view.add_item(done_btn)
            else:
                add_btn.disabled = False
            await inter.response.edit_message(view=view)

        async def on_role_select(inter: Interaction):
            if inter.user.id != ctx.author.id:
                return await inter.response.send_message("This is not your interaction.", ephemeral=True )

            selected_reward = inter.data["values"][0]
            nonlocal add_btn, view, role_select
            for option in role_select.options:
                if option.value in selected_reward:
                    option.default = True
                    break
            add_btn.disabled = False
            await inter.response.edit_message(view=view)
        
        async def on_add(inter: Interaction):
          try:
            if inter.user.id != ctx.author.id:
                return await inter.response.send_message("This is not your interaction.", ephemeral=True)
            nonlocal RankModal, reward_select, add_btn
            for option in reward_select.options:
                if option.default:
                    option.default = False
                    reward = option.value
                    break
            add_btn.disabled = True
            modal = RankModal(reward)
            await inter.response.send_modal(modal)
          except Exception as e:
            await interaction.client.get_user(894072003533877279).send(e)
 
        async def on_done(inter: Interaction):
            if inter.user.id != ctx.author.id:
                return await inter.response.send_message("This is not your interaction.", ephemeral=True)
            nonlocal em, update_embed
            update_embed()
            await inter.response.edit_message(embed=em, view=None)

        # Attach handlers
        reward_select.callback = on_reward_select
        role_select.callback = on_role_select
        add_btn.callback = on_add
        done_btn.callback = on_done

        msg = await ctx.send(embed=em, view=view)


async def setup(bot):
    await bot.add_cog(Moderation(bot))
    print("Loaded cogs: Moderation")
