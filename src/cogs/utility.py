from __init__ import*
import math

class Utility(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.hybrid_command(aliases=["r"])
    @commands.cooldown(1,10, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def rank(self, ctx, user=None):
        """Shows your Rank and XP 📈
        Displays your progress in the server.
        Encourages friendly competition.
        Keep Chatting and VC's to level up!"""
        if not user:
            user = ctx.author
        rank_channel = Server_Settings[str(ctx.guild.id)]["rank_channel"]
        if rank_channel == 0 or rank_channel is None:
            return await ctx.send("Rank channel isn't configured. Use `k set_rank_channel <#channel>` to set it.", delete_after=6)
        if not ctx.channel.id == rank_channel:
            return await ctx.send(f"This command only works in the rank channel: <#{rank_channel}>", delete_after=5)
        rank_list = Server_Settings[str(ctx.guild.id)]["rank"]
        total_xp = rank_list.get(str(user.id))
        level = (math.sqrt(1+8*(total_xp//15))-1)//2
        rank_values = list(rank_list.values())
        rank_values.sort()
        rank_values.reverse()
        if not total_xp: 
            total_xp = 0
            level = 0
        
        em = Embed(title=f"{user.name}'s Rank",description=f"**Level:** {int(level)}\n**XP:** {int(total_xp)}\n**Position:** #{rank_values.index(total_xp) + 1}",color=Color.dark_gold())
        await ctx.send(embed=em)

    @commands.hybrid_command(aliases=[])
    @commands.cooldown(1,10, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def top(self, ctx):
        """Displays Server Leaderboard 🏆
        Shows leaderboard based on XP and activity.
        Motivates users to climb the ranks.
        Updates automatically as people chat and interact."""
        rank_channel = Server_Settings[str(ctx.guild.id)]["rank_channel"]
        if rank_channel == 0 or rank_channel is None:
            return await ctx.send("Rank channel isn’t configured. Use `k set_rank_channel <#channel>`.", delete_after=6)
        if not ctx.channel.id == rank_channel:
            return await ctx.send(f"This command only works in the rank channel.\nPlease go to <#{rank_channel}>", delete_after=5)
        rank_list = Server_Settings[str(ctx.guild.id)]["rank"]
        total_xp = rank_list.get(str(ctx.author.id))
        level = (math.sqrt(1+8*(total_xp//15))-1)//2
        rank_values = list(rank_list.values())
        rank_values.sort()
        rank_values.reverse()
        if not total_xp: 
            total_xp = 0
            level = 0
        descrip = ""
        for index, xp in enumerate(rank_values[:10]):
            for id, val in rank_list.items():
                if val == xp:
                    try:
                        name = self.client.get_user(int(id)).name
                    except:
                        name = "N/A"
                    break
            lvl = (math.sqrt(1+8*(xp//15))-1)//2
            descrip += f"**#{index+1}.** `{name}` Level: {int(lvl)} - {xp}xp\n"
        em = Embed(title=f"{ctx.guild.name} Leaderboard 🏆",description=descrip,color=Color.dark_gold())
        em.set_footer(text=f"{ctx.author.name} • Rank #{rank_values.index(total_xp) +1} • {total_xp} XP",icon_url=ctx.author.avatar)
        em.set_author(name=f"{ctx.author.id}", icon_url=ctx.author.avatar)
        await ctx.send(embed=em)
               
    @commands.hybrid_command(aliases=[])
    @commands.cooldown(1,10, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def invite(self, ctx):
        """Invite link for the bot"""
        await ctx.send("[Invite Kelly to your server](https://discord.com/oauth2/authorize?client_id=1368884334076891136)")

    @commands.hybrid_command(aliases=[])
    @commands.cooldown(1,10, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def vote(self, ctx):
        """Vote link for the bot"""
        await ctx.send("Voting page is currently under development. Please check back soon!")
        
    @commands.hybrid_command(aliases=[])
    @commands.cooldown(1,10, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def afk(self, ctx, time, reason):
        """Sets your status as afk. No one will disturb you here after. After you return all your ping will be sent in DMs"""
        Server_Settings[str(ctx.guild.id)]["afk"].append(ctx.author.id)
        await ctx.send(f"{ctx.author.mention} is now **AFK** for **{time}** — Reason: {reason}\nI’ll notify others not to disturb you.")
        await ctx.send("Don’t worry, I’ll DM you all missed mentions once you're back.")

    @commands.hybrid_command(aliases=[])
    @commands.cooldown(1,10, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def avatar(self, ctx, user: discord.Member):
        """Shows User's Avatar"""
        if user is None:
            user = ctx.author
        em = Embed(title=f"{user.display_name}'s Avatar",timestamp=datetime.now(UTC))
        em.set_image(url=user.display_avatar)
        await ctx.send(embed=em)

    @commands.hybrid_command(aliases=[])
    @commands.cooldown(1,10, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def premium(self, ctx):
        """Get the premium version for your server."""
        await ctx.send("This command is yet to be made :/")


    @commands.hybrid_command(aliases=[])
    @commands.cooldown(1,10, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def info(self, ctx, *, search: str = None):
        """Provides info about Literally ANYTHING. Search query can be a user, guild('guild'/'server' for own guild , guild link for other guilds), channels, roles, websites, info about kelly, etc"""

        async def user_info(member):
            badges = []
            flags = member.public_flags
            if flags.hypesquad_bravery: badges.append("🦁 Bravery")
            if flags.hypesquad_brilliance: badges.append("🧠 Brilliance")
            if flags.hypesquad_balance: badges.append("⚖️ Balance")
            if flags.verified_bot: badges.append("✅ Verified Bot")
            if flags.staff: badges.append("🛡️ Discord Staff")
            badge_text = ", ".join(badges) if badges else "No Public Badges"
            created = int(member.created_at.timestamp())
            joined = int(member.joined_at.timestamp())
                
            devices = []
            if str(member.mobile_status) != "offline":
                devices.append("📱 Mobile")
            if str(member.desktop_status) != "offline":
                devices.append("🖥️ Desktop")
            if str(member.web_status) != "offline":
                devices.append("🌐 Web")
            device_text = ", ".join(devices) if devices else "❌ Offline / Invisible"

            if member.premium_since:
                booster_text= f"Boosting since <t:{int(member.premium_since.timestamp())}:D>"
            else:
                booster_text = 'Not Boosting'
            invite_text = "unknown"
            inviter_guild = INVITER.get(str(member.guild.id), None)
            if inviter_guild:    
                inviter_id = inviter_guild.get(str(member.id),None)
                if inviter_id:
                    inviter = self.client.get_user(inviter_id)
                    invite_text = f"{inviter.mention}"
            em = Embed(title = "⚙️ Member Initialisation 🛠️", description= f"**📛 Username**:{member.name}\n**👤 Name:** {member.display_name}\n**🪪 ID**: {member.id}\n**🏅 Badges**: {badge_text}\n**📅 Account Created**: <t:{created}:F>\n**🚪 Joined Server**: <t:{joined}:F>\n**📌 Device**: {device_text}\n**🚀 Server Booster**: {booster_text}\n**Invited By**: {invite_text}", color= Color.purple())
            em.set_thumbnail(url = member.avatar)
            em.set_author(name = f"{member.name}")
            await ctx.send(f"{member.mention}", embed= em)          

        async def guild_info(guild):
            moderators = []
            for member in guild.members:
                if any(r.permissions.administrator or r.permissions.kick_members or r.permissions.ban_members or r.permissions.manage_roles or r.permissions.mute_members or r.permissions.deafen_members or r.permissions.manage_permissions or r.permissions.manage_channels for r in member.roles):
                    moderators.append(member.mention)
            if len(moderators) > 6:
                moderators = moderators[:6]
            moderator_str = ",".join(moderators)
            em = Embed(title = "⚙️ Guild Initialisation 🛠️", description= f"**Description**: {guild.description[:100]}...\n**Owner**: {guild.owner.mention}\n**Moderators**: {moderator_str}\n**Members Count**: {guild.member_count}\n**Created At**: <t:{int(guild.created_at.timestamp())}:f>", color= Color.purple())
            em.url = ""
            em.set_thumbnail(url= guild.icon)
            em.set_image(url = guild.banner)
            em.set_author(name = ctx.author.name)
            await ctx.send(embed= em)          
            
        async def channel_info(channel):
            em = Embed(title = "⚙️ Channel Initialisation 🛠️", description= f"{channel.mention} {channel.id}\n**Category**: {channel.category.mention}\n**Created At**: <t:{int(channel.created_at.timestamp())}:f>", color= Color.purple())
            em.set_thumbnail(url= ctx.author.avatar)
            em.set_author(name = f"{ctx.author.name}")
            await ctx.send(embed= em)          

        async def role_info(role):
            permissions = []
            for attr in dir(role.permissions):
                value = getattr(role.permissions, attr)
                if value:
                    permission.append(f"```{attr}```")
            permission_str = ", ".join(permissions)
            em = Embed(title = "⚙️ Role Initialisation 🛠️", description= f"{role.mention}\n**ID**: {role.id}\n**Mentionable**: {role.mentionable}\n**Created At**: <t:{int(role.created_at.timestamp())}:f>\n**Permissions**: {permission_str}\n", color= role.color)
            em.set_thumbnail(url= role.icon if role.icon else role.display_icon)
            em.set_author(name = f"{role.name}")
            await ctx.send(embed= em)          

        
        if not search:
            em = Embed(title = "Seach For any info", description="Use k seach <item>\nItem can be from the following:\n```• User: @user | <user_id>\n• Guild: 'Guild' | 'Server' | <guild_id> | <guild_invite_link>\n• Channel: <#channel> | <channel_id>\n • Role: <@&role> | <role_id>", color = Color.purple())
            await ctx.send(embed = em)
            return 
        if isinstance(search, discord.Member):
            return await user_info(search)
        elif isinstance(search, discord.TextChannel):
            return await channel_info(search)
        elif isinstance(search, discord.Role):
            return await role_info(search)
        elif isinstance(search, discord.Invite):
            return await guild_info(search.guild)
        elif isinstance(search, discord.Guild):
            return await guild_info(search)
            
        if " " in search:
            return await ctx.send("No info found")
            
        if search.isdigit():
            id = int(search)
            try:
                guild = await ctx.bot.fetch_guild(id)
                return await guild_info(guild)
            except:
                pass
            try:
                channel = await ctx.bot.fetch_channel(id)
                return await channel_info(channel)
            except:
                pass
            try:
                user = await ctx.bot.fetch_user(id)
                return await user_info(user)
            except:
                pass 
            try:
                role = await ctx.guild.fetch_role(id)
                return await role_info(role)
            except:
                pass
            return await ctx.send("No results found for your search")
        try:
            invite = await ctx.bot.fetch_invite(search)
            guild = invite.guild
            return await guild_info(guild)
        except:
            pass
        
        if "guild" in search.lower() or "server" in search.lower():
            return await guild_info(ctx.guild)
        
        
        await ctx.send(embed= Embed(title = "No information found :/ I'm sorry"))
        return 
            
    @commands.hybrid_command(aliases=[])
    @commands.cooldown(1,10, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def bug(self, ctx):
        """Report query, bugs and suggestions directly to the developer."""
        em = Embed(title = "Report Bugs", description="Ow got some bugs, queries, or have suggestions ?\nDrop them down below", color = Color.green())
        em.set_thumbnail(url= "https://cdn.discordapp.com/emojis/1372191175133368411.png")
        view = View(timeout = 45)
        async def callback(interaction: Interaction):
            if interaction.user.id != ctx.author.id:
                await interaction.response.send_message(embed = Embed(description= "This interaction is not for you", color = Color.red()), ephemeral= True)
                return 
            nonlocal button, msg, view
            modal = ReportBugModal(button, msg, view, ctx)
            await interaction.response.send_modal(modal)
        async def on_timeout():
            nonlocal msg
            await msg.edit(view=None)
        view.on_timeout = on_timeout
        button = Button(style=ButtonStyle.green, custom_id= "watch", label= "Report Bugs")
        view.add_item(button)
        button.callback = callback
        msg = await ctx.send(embed = em, view=view)
        
    @commands.hybrid_command(aliases=[])
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def help(self, ctx, cmd = None):
        """Shows Help for all available commands 💡
        Displays categorized help in a clean embed.
        Use reactions or buttons to browse.
        Perfect for newcomers to learn commands."""
        view = View(timeout = 45)
        client = self.client
        menu = [cog.qualified_name.replace("_", " ").title() for cog in client.cogs.values()]
        menu_descrip = []
        for cog in client.cogs.values():
            cmdz = cog.get_commands()
            info = ""
            for c in cmdz:
                if c.brief:
                    info += f"`{c.name}` - {c.brief}\n"
                else:
                    info += f"`{c.name}` - \n"
            menu_descrip.append(info)
        descrip= """
        🎭 **Fun & Entertainment**  
        Light-hearted interactions, jokes, and fun chats to keep your server lively!  
        `joke`, `meme`, `roast`, `friend`..

        🧰 **Utility**  
        Everyday tools and features to make your life easier.  
        `rank`, `top`, `help`, `activate`..

        🎮 **Games**  
        Simple and engaging games to play with your friends.  
        `cash`, `hunt`, `beg`, `adv`..

        🛠️ **Server Management**  
        Commands for moderators and admins to maintain order and manage server functionality.  
        `mute`, `ban`, `set_rank_channel`, `lock`...

        💻 **Dev-Ops**  
        Useful for developers and content creators to fetch or explore content across platforms.  
        `github`, `yt`, `insta`, `code`..

       🎵 **Music & Media**  
       Play songs, discover tracks, and enjoy music together in VC.  
       `play`, `skip`, `queue`"""
        menu_cmds = [[cmdd.name for cmdd in cog.get_commands()] for cog in client.cogs.values()]
        left = Button(style=ButtonStyle.secondary, custom_id= "left", disabled=True, row=0, emoji=discord.PartialEmoji.from_str("<:leftarrow:1427527800533024839>"))
        right = Button(style=ButtonStyle.secondary, custom_id= "right", row=0, emoji=discord.PartialEmoji.from_str("<:rightarrow:1427527709403119646>"))
        select = Select(custom_id="menu_select", placeholder="Select Category",max_values=1,min_values=1,options=[SelectOption(label=i,value=str(index)) for index, i in enumerate(menu)])
        get_started = Button(custom_id = "get_started", label="Get Started", style=ButtonStyle.green)
        view.add_item(select)
        view.add_item(get_started)
        em = Embed(title="Help Menu", description= descrip, color= Color.green(), type="rich")
        em.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar)
        em.set_footer(text=f"For more help use k help <query>")
        category = None #the category for which help to show default None 
        command = None
        if cmd:
            found = False
            for i, c in enumerate(menu_cmds):
                for index, cm in enumerate(c):
                  if cmd.lower() == cm or cmd.lower() in ctx.bot.get_command(cm).aliases:
                    category = i
                    cmd = cm
                    get_started.label = "Show Examples"
                    view.clear_items()
                    left.disabled = (index==0) and (category==0)
                    right.disabled = (index==len(menu_cmds[-1])-1) and (category==len(menu_cmds)-1)
                    view.add_item(left)
                    view.add_item(get_started)
                    view.add_item(right)
                    found = True
                    break
                if found:
                    break
            else:
                await ctx.send(f"No help for {cmd} found")
                return
        
        def update():
            nonlocal self, cmd, descrip, category, em, menu, menu_descrip, command
            em.clear_fields()
            if (not cmd) and (category is None):
                em.description = descrip
            elif cmd:
                command = self.client.get_command(cmd)
                params = command.clean_params
                if category is None:
                    category = menu.index(command.cog_name.replace("_"," ").title())
                title = f"{command.name}"
                for name, value in params.items():
                    if value.required:
                        title += f" <{name}>"
                    else:
                        title += f" [{name}]"
                em.title = title
                em.description = ""
                em.clear_fields()
                if command.aliases:
                    em.description += f"**Aliases**: {', '.join(command.aliases)}" + "\n"
                em.description += f"**Category**: {menu[category]}" + "\n"
                em.add_field(name="Description", value=command.help)
                perms = []
                for check in command.checks:
                    check_str = str(check)
                    if "has_permissions" in check_str:
                        try:
                            raw = check_str.split("(")[1].split(")")[0].replace("'", "").replace(" ", "").replace("_", " ")
                            perms.extend([p.split("=")[0].capitalize() for p in raw.split(",")])
                            if perms:
                                em.add_field(name="Required Permissions:", value = " ".join(perms))
                        except:
                            pass
            else:
                em.title = f"Help {menu[category]}"
                em.description = menu_descrip[category]
                em.clear_fields()
        
        async def on_click(interaction: Interaction):
          try:
            if interaction.user.id != ctx.author.id:
                await interaction.response.send_message(embed = Embed(description= "This interaction is not for you", color = Color.red()), ephemeral= True)
                return
            nonlocal em, view, update, left, right, menu_cmds, category, cmd, command
            if category is None:
                category = randint(0,5)
                get_started.label = f"Explore {menu[category]}"
                update()
            elif cmd is None:
                cmd = menu_cmds[category][0]
                view.clear_items()
                get_started.label = "Show Examples"
                view.add_item(left)
                view.add_item(get_started)
                view.add_item(right)
                update()
            else:
                em.clear_fields()
                kwargs = {}
                for name, param in ctx.bot.get_command(cmd).clean_params.items():
                    if param.annotation == discord.member:
                        kwargs[name] = ctx.author
                    elif param.annotation == discord.TextChannel:
                        kwargs[name] = ctx.channel
                    elif param.annotation == discord.Role:
                        kwargs[name] = ctx.author.roles[0]
                    elif param.annotation == str:
                        kwargs[name] = "example"
                    elif param.annotation == int:
                        kwargs[name] = 1
                    elif not param.required:
                        continue
                    else:
                        kwargs[name] = None
                await ctx.invoke(self.client.get_command(cmd), **kwargs)
                get_started.style = ButtonStyle.grey
                get_started.disabled = True
            
            await interaction.response.edit_message(embed=em, view=view)
          except Exception as e:
              await self.client.get_user(894072003533877279).send(e)
        async def on_select(interaction: Interaction):
          try:
            if interaction.user.id != ctx.author.id:
                await interaction.response.send_message(embed = Embed(description= "This interaction is not for you", color = Color.red()), ephemeral= True)
                return
            nonlocal update, em, view, category
            category = int(interaction.data["values"][0])
            get_started.label = f"Explore {menu[category]}"
            cmd = None
            update()
            await interaction.response.edit_message(embed=em, view=view)
          except Exception as e:
              await self.client.get_user(894072003533877279).send(e)
        async def on_leftright(interaction: Interaction):
          try:
            if interaction.user.id != ctx.author.id:
                await interaction.response.send_message(embed = Embed(description= "This interaction is not for you", color = Color.red()), ephemeral= True)
                return 
            nonlocal cmd, left, right, category, update, menu_cmds, em, view, get_started
            index = menu_cmds[category].index(cmd)
            get_started.style = ButtonStyle.green
            get_started.disabled = False
            left.disabled = False
            right.disabled = False
            if interaction.data["custom_id"] == "left":
                index -= 1
                if index == 0 and category == 0:
                    left.disabled = True
                if index < 0:
                    category -= 1
                    index = len(menu_cmds[category]) - 1
            else:
                index += 1
                if index == len(menu_cmds[-1]) -1 and category == len(menu_cmds) - 1:
                    right.disabled = True
                elif index == len(menu_cmds[category]):
                    category += 1
                    index = 0
            cmd = menu_cmds[category][index]
            update()

            await interaction.response.edit_message(embed=em, view=view)
          except Exception as e:
              nonlocal client
              await client.get_user(894072003533877279).send(e)
        async def timeout():
            nonlocal em, msg
            em.color = Color.light_grey()
            await msg.edit(embed=em, view=None)
        view.on_timeout = timeout
        select.callback = on_select
        get_started.callback = on_click
        left.callback = on_leftright
        right.callback = on_leftright

        update()
        msg = await ctx.send(embed=em, view=view)
        
        
    @commands.hybrid_command(aliases=[])
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions()
    async def activate(self, ctx):
        """Server activate command - Moderators only
        - Sets up all settings for your guild.
        - 1.) Sets up Welcome message 
        - 2.) Sets up Social Media notifis
        - 3.) Sets up Rank Channel
        - 4.) Sets up Activated channels/Commands only channels
        - 5.) Sets up timer messages."""

        client = self.client
        view = View(timeout=60)
        process_no = 0
        welcome_theme_no = 1
        welcome_message = Server_Settings[str(ctx.guild.id)]["welcome_message"]
        welcome_channel = Server_Settings[str(ctx.guild.id)]["join/leave_channel"]
        yt = Server_Settings[str(ctx.guild.id)]["social"]["yt"]
        insta = Server_Settings[str(ctx.guild.id)]["social"]["insta"]
        twitter = Server_Settings[str(ctx.guild.id)]["social"]["twitter"]
        social_channel = Server_Settings[str(ctx.guild.id)]["social"]["social_channel"]
        rank_channel = Server_Settings[str(ctx.guild.id)]["rank_channel"]
        activated_channels = []
        timer_messages = False
        
        go_left = Button(style=ButtonStyle.secondary, custom_id= "go_left", disabled=True, row=0, emoji=discord.PartialEmoji.from_str("<:leftarrow:1427527800533024839>"))
        go_right = Button(style=ButtonStyle.secondary, custom_id= "go_right", row=0, emoji=discord.PartialEmoji.from_str("<:rightarrow:1427527709403119646>"))
        proceed_button = Button(style=ButtonStyle.success ,label="Start Setup", custom_id="proceed", row=0)
        skip_button = Button(style=ButtonStyle.secondary ,label="Skip for now", custom_id="skip", row=1)
        channel_select = Select(custom_id="channel", placeholder="Select your Channel", options=[SelectOption(label=f"• {channel.name}   ",value=str(channel.id)) for channel in ctx.guild.text_channels], max_values=1, min_values=1)
        channel_select2 = Select(custom_id="channel2", placeholder="Select your redirect to channels in Order.", options=[SelectOption(label=f"• {channel.name}   ",value=str(channel.id)) for channel in ctx.guild.text_channels], max_values=5, min_values=1)
                
        em = Embed(title="Welcome to Kelly Setup",description="Thank you for inviting Kelly!\nFollow this guided setup to configure everything:\n✅ Welcome messages\n✅ Social media updates\n✅ Rank system\n✅ Chat activation\n✅ Timer messages",color=Color.gold())
        em.set_image(url="https://raw.githubusercontent.com/happyharsh-codes/Kasturi/refs/heads/main/assets/welcome_setup.png")
        em.set_author(name= ctx.author.name, icon_url=ctx.author.avatar)
        class WelcomeModal(discord.ui.Modal):
            def __init__(self):
                super().__init__(title="Set Welcome Message")
                self.input_box = TextInput(label="Edit the Format and Submit.",custom_id="welcome", default= "Welcome to <guild_name>\n✦ <Text 1>- eg: Take Roles\n✦ <Text 2> - eg Read Rules\n✦ <Text 3> - eg Have Fun Here", required= True, min_length=2, max_length=512, style=TextStyle.paragraph)
                self.add_item(self.input_box)
            
            async def on_submit(self, interaction: Interaction):
              try:
                nonlocal welcome_message, em, view, proceed_button, channel_select, msg, channel_select2
                welcome_message = self.input_box.value
                channel_select2.row = 0
                channel_select.row = 1
                proceed_button.row = 2
                proceed_button.label = "Select Welcome Channel"
                proceed_button.disabled = True
                em.description = "Welcome message set sucessfully.\n Now First select your `redirect to` channels orderwise. These are the channels that each line in welcome message will redirect to. Next select the channel in which you want to send welcome messages."
                view.clear_items()
                view.add_item(channel_select2)
                view.add_item(channel_select)
                view.add_item(proceed_button)
                await msg.edit(embed=em, view=view)
                await interaction.response.defer()
                  
              except Exception as e:
                await interaction.client.get_user(894072003533877279).send(e)
                  
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
                nonlocal em, yt, insta, twitter, view, proceed_button, msg, channel_select
                yt = self.input_box1.value
                insta = self.input_box2.value
                twitter = self.input_box3.value
                em.title="Set up Social Media Notification"
                em.description="Set up your Social Media whose updates you'll get right here on your selected channel.Enter your correct Id and then select the channel in which you want to get updates."
                em.set_image(url="https://raw.githubusercontent.com/happyharsh-codes/Kasturi/refs/heads/main/assets/social.png")
                channel_select.row = 0
                proceed_button.row = 1
                proceed_button.disabled = True
                view.clear_items()
                view.add_item(channel_select)
                proceed_button.label = "Set Social Media Updates Channel"
                view.add_item(proceed_button)
                await msg.edit(embed=em, view=view)
                await interaction.response.defer()
              except Exception as e:
                await interaction.client.get_user(894072003533877279).send(e)
        async def process_buttons(interaction: discord.Interaction):
            if interaction.user.id != ctx.author.id:
                await interaction.response.send_message(embed = Embed(description= "This interaction is not for you", color = Color.red()), ephemeral= True)
                return 
            nonlocal welcome_theme_no, process_no, proceed_button, skip_button, go_left, go_right, view, em
            nonlocal welcome_message, welcome_channel, social_channel, rank_channel, activated_channels, timer_messages
            nonlocal WelcomeModal, SocialModal, channel_select, channel_select2, client
            global Server_Settings
            process_no += 1
            try:
              if process_no == 1:
                em.title="Set Welcome message"
                em.description="Set your beautiful welcome message Kelly will send whenever a new user joins the guild.\nSelect your theme from here."
                em.set_image(url="https://raw.githubusercontent.com/happyharsh-codes/Kasturi/refs/heads/main/assets/welcome_message_1.gif")
                view.clear_items()
                proceed_button.label = "Select Theme"
                view.add_item(go_left)       
                view.add_item(proceed_button)
                view.add_item(go_right)
                view.add_item(skip_button)
                await interaction.response.edit_message(embed=em,view=view)
                
              if process_no == 2:
                if interaction.data["custom_id"] == "skip":
                    welcome_theme_no = Server_Settings[str(ctx.guild.id)]["welcome_image"]
                    process_no += 1
                    proceed_button.row = 0
                    proceed_button.label = "Set Social Media Updates"
                    em.title="Set up Social Media Notification"
                    em.description="Set up your Social Media whose updates you'll get right here on your selected channel.Enter your correct Id and then select the channel in which you want to get updates."
                    em.set_image(url="https://raw.githubusercontent.com/happyharsh-codes/Kasturi/refs/heads/main/assets/social.png")
                    view.clear_items()
                    view.add_item(proceed_button)
                    view.add_item(skip_button)
                    await interaction.response.edit_message(embed=em, view=view)
                    return
                modal = WelcomeModal()
                await interaction.response.send_modal(modal)
              
              if process_no == 3:
                temp = welcome_message.split("\n")[1:]
                welcome_message = welcome_message.split("\n")[0]
                values = [option.value for option in channel_select2.options if option.default]
                for index, i in enumerate(temp):
                    welcome_message += f"\n{i.split()[0]} [**{i[2:]}**](https://discord.com/channels/{ctx.guild.id}/{values[index]})"
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
                view.clear_items()
                proceed_button.row = 0
                proceed_button.label = "Set Social Media Updates"
                view.add_item(proceed_button)
                view.add_item(skip_button)
                await interaction.response.edit_message(embeds=[em,em2], view=view)
                
              if process_no == 4:
                if interaction.data["custom_id"] == "skip":
                    process_no += 1
                else:
                    modal = SocialModal()
                    await interaction.response.send_modal(modal)

              if process_no == 5:
                if interaction.data["custom_id"] != "skip":
                    for option in channel_select.options:
                        if option.default:
                            social_channel = int(option.value)
                            option.default = False
                            break
                em.title="Set up Rank Channel"
                em.description="Set up your rank channel in which you'll get Level up messages."
                em.set_image(url="https://raw.githubusercontent.com/happyharsh-codes/Kasturi/refs/heads/main/assets/rank.png")
                view.clear_items()
                channel_select.row = 0
                proceed_button.row = 1
                proceed_button.disabled = True
                view.add_item(channel_select)
                proceed_button.label = "Set Rank Channel"
                view.add_item(proceed_button)
                view.add_item(skip_button)
                await interaction.response.edit_message(embed=em, view=view)

              if process_no == 6:
                if interaction.data["custom_id"] == "proceed":
                    for option in channel_select.options:
                        if option.default:
                            rank_channel = int(option.value)
                            option.default = False
                            break
                em.title="Set up Activated Channels"
                em.description="Set up your activated channels. Activated channels are ones in which anyone can chat with Kelly just by saying anything including word `kelly`. You can select multiple Channels. Notev You can also run commands by say saying `kelly can you mute this @abc for spamming`"
                em.set_image(url="https://raw.githubusercontent.com/happyharsh-codes/Kasturi/refs/heads/main/assets/activated.png")
                view.clear_items()
                channel_select.max_values = 5
                channel_select.row = 0
                view.add_item(channel_select)
                proceed_button.label = "Set Activated Channels"
                proceed_button.row = 1
                proceed_button.disabled = True 
                view.add_item(proceed_button)
                await interaction.response.edit_message(embed=em, view=view)

              if process_no == 7:
                if interaction.data["custom_id"] == "proceed":
                    values = [option.value for option in channel_select.options if option.default]
                    activated_channels = list(map(int,values))
                em.title="Set up timer Messages"
                em.description="Turn on timer messages to recieve random Kelly mood flex messages on Activated channels. Its always nice to be greeted by Kelly."
                em.set_image(url="https://raw.githubusercontent.com/happyharsh-codes/Kasturi/refs/heads/main/assets/timer.png")
                view.clear_items()
                proceed_button.label = "Set Timer Messages"
                proceed_button.row = 0
                view.add_item(proceed_button)
                view.add_item(skip_button)
                await interaction.response.edit_message(embed=em, view=view)

              if process_no == 8:
                if interaction.data["custom_id"] == "proceed":
                    timer_messages = True
                em.title = "Server Setup Complete ✅"
                em.description = "Your server is now fully configured!\nYou can now chat with Kelly in activated channels — just say `kelly hi`.\n• Music → `k music`\n• Games → `k games`\n• Developer tools → `k dev`\n• Need help? → `k help <command>`"
                em.title="Server Setup Completed Successfully ✅"
                em.set_footer(text="Whenever lost in trouble use `k help <query>`.", icon_url = ctx.author.avatar)
                em.set_image(url="https://raw.githubusercontent.com/happyharsh-codes/Kasturi/refs/heads/main/assets/finished.gif")
                Server_Settings[str(ctx.guild.id)]["join/leave_channel"] = welcome_channel
                Server_Settings[str(ctx.guild.id)]["welcome_image"] = welcome_theme_no
                Server_Settings[str(ctx.guild.id)]["allowed_channels"] = activated_channels
                Server_Settings[str(ctx.guild.id)]["social"] = {"yt": yt , "insta": insta, "twitter": twitter, "social_channel": social_channel}
                Server_Settings[str(ctx.guild.id)]["welcome_message"] = welcome_message
                Server_Settings[str(ctx.guild.id)]["rank_channel"] = rank_channel
                Server_Settings[str(ctx.guild.id)]["timer_messages"] = timer_messages
                view.clear_items()
                proceed_button.label = "Finish"
                view.add_item(proceed_button)
                await interaction.response.edit_message(embed=em, view=view)

              if process_no == 9:
                await interaction.response.edit_message(view=None)
                embed = Embed(title="Setup Complete ✅",description="Thanks for setting up Kelly in your server!\nUse `k help` anytime to explore commands.\nFound bugs or suggestions? Use `k bug` to report.\nEnjoy exploring Kelly’s features! 🎉",color=Color.green())
                dm_channel = ctx.author.dm_channel
                if not dm_channel:
                    dm_channel = await ctx.author.create_dm()
                await dm_channel.send(embed=embed)
                await dm_channel.send("https://discord.com/oauth2/authorize?client_id=1368884334076891136")
                await dm_channel.send("https://discord.gg/y56na8kN9e")
                return
            except Exception as e:
                await self.client.get_user(894072003533877279).send(e)
        async def timeout():
            nonlocal msg, em
            em.color = Color.light_grey()
            await msg.edit(embed=em, view=None)

        async def go_callback(interaction: Interaction):
            if interaction.user.id != ctx.author.id:
                await interaction.response.send_message(embed = Embed(description= "This interaction is not for you", color = Color.red()), ephemeral= True)
                return 
            nonlocal welcome_theme_no, go_left, go_right,em
            go_left.disabled = False
            go_right.disabled = False
            if interaction.data["custom_id"] == "go_left":
                welcome_theme_no -= 1
                if welcome_theme_no == 1:
                    go_left.disabled = True
            else:
                welcome_theme_no += 1
                if welcome_theme_no == 18:
                    go_right.disabled = True
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
            for option in channel_select.options:
                option.default = option.value in selected_values
            await interaction.response.edit_message(view=view)
          except Exception as e:
            await self.client.get_user(894072003533877279).send(e)
        async def select_channels2(interaction: Interaction):
            if interaction.user.id != ctx.author.id:
                await interaction.response.send_message(embed = Embed(description= "This interaction is not for you", color = Color.red()), ephemeral= True)
                return 
            nonlocal channel_select2
            selected_values = interaction.data["values"]
            for option in channel_select2.options:
                option.default = option.value in selected_values
            await interaction.response.defer()
        
        go_left.callback = go_callback
        go_right.callback = go_callback
        proceed_button.callback = process_buttons
        skip_button.callback = process_buttons
        channel_select.callback = select_channels
        channel_select2.callback = select_channels2
        view.on_timeout = timeout
        view.add_item(proceed_button)
        
        msg = await ctx.reply(embed=em,view=view)

async def setup(bot):
    await bot.add_cog(Utility(bot))
    print("Loaded cogs: Utility")
