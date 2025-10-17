from __init__ import*
import math

class Utility(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command(aliases=["r"])
    @commands.cooldown(1,10, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def rank(self, ctx, user=None):
        if not user:
            user = ctx.author
        rank_channel = Server_Settings[str(ctx.guild.id)]["rank_channel"]
        if not ctx.channel.id == rank_channel:
            await ctx.send("This command only works in rank channel!!", delete_after=5)
            return
        rank_list = Server_Settings[str(ctx.guild.id)]["rank"]
        total_xp = rank_list.get(str(user.id))
        level = (math.sqrt(1+8*(total_xp//15))-1)//2
        rank_values = list(rank_list.values())
        rank_values.sort()
        rank_values.reverse()
        if not total_xp: 
            total_xp = 0
            level = 0
        em = Embed(title=f"{user.name}'s Rank", description=f"LEVEl: {int(level)}\nXP: {int(total_xp)}\nRank: {rank_values.index(total_xp) + 1}", color=Color.dark_gold())
        await ctx.send(embed=em)

    @commands.command(aliases=[])
    @commands.cooldown(1,10, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def top(self, ctx):
        rank_channel = Server_Settings[str(ctx.guild.id)]["rank_channel"]
        if rank_channel == 0 or rank_channel is None:
            await ctx.send("This Server does not have Rank Channels set. Please set using `k set_rank_channel <#channel>", delete_after=6)
            return
        if not ctx.channel.id == rank_channel:
            await ctx.send(f"This command only works in rank channel!!\nPlease go to <#{rank_channel}>.", delete_after=5)
            return
        rank_list = Server_Settings[str(ctx.guild.id)]["rank"]
        total_xp = rank_list.get(str(ctx.author.id))
        level = (math.sqrt(1+8*(total_xp//15))-1)//2
        rank_values = list(rank_list.values())
        rank_values.sort()
        rank_values.reverse()
        if not total_xp: 
            total_xp = 0
            level = 0
        em = Embed(title=f"{ctx.guild.name} Rank Leaderboard", description=[f"**{index+1}** {rank_values.index(i)+1} - {i}xp" for index, i in enumerate(rank_values[:10]) ].join("\n"), color=Color.dark_gold())
        em.set_footer(text=f"{ctx.author.name} at #{rank_values.index(total_xp) +1} - {total_xp}xp", icon_ur= ctx.author.avatar)
        em.set_author(name=ctx.author.id, icon_url=ctx.author.url)
        await ctx.send(embed=em)
        
            
    @commands.command(aliases=[])
    @commands.cooldown(1,10, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def invite(self, ctx):
        await ctx.send("[Meet Kelly here](https://top.gg/bot/1368884334076891136?s=0332b997edcc8)")

    @commands.command(aliases=[])
    @commands.cooldown(1,10, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def vote(self, ctx):
        await ctx.send("This command is yet to be made :/")

    @commands.command(aliases=[])
    @commands.cooldown(1,10, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def afk(self, ctx, time, reason):
        Server_Settings[str(ctx.guild.id)]["afk"].append(ctx.author.id)
        await ctx.send(f"{ctx.author.mention} has gone afk for **{time}** : {reason}. Dont ping him unnecessarily")
        await ctx.send("Dont worry I'll notify everyone in your absense not to disturb you...")

    @commands.command(aliases=[])
    @commands.cooldown(1,10, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def avatar(self, ctx, user: discord.Member):
        if user is None:
            user = ctx.author
        em = Embed(title=f"{user.display_name}'s Avatar", timestamp=datetime.now(UTC))
        em.set_image(url=user.display_avatar)
        await ctx.send(embed=em)

    @commands.command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def info(self, ctx, item):
        await ctx.send("This command is yet to be made :/")


    @commands.command(aliases=[])
    @commands.cooldown(1,10, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def premium(self, ctx):
        await ctx.send("This command is yet to be made :/")

    @commands.command(aliases=[])
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def help(self, ctx, cmd = None):
        '''Help command'''
        view = View(timeout = 45)
        menu= ["Fun & Entertainment", "Utility", "Games", "Server Management", "Dev-Ops", "Music & Media"]
        menu_descrip= [
    "🎭 **Fun & Entertainment**\n`joke` – Get a random joke.\n`friends` – See your friend list.",
    "🧰 **Utility**\n`rank` – Check your level.\n`top` – View leaderboard.\n`help` – Show all commands.",
    "🎮 **Games**\n`rolldice` – Roll a dice for fun.",
    "🛠️ **Server Management**\n`mute`\`unmute` - Mute\Unmute someone\n`kick` - kick someone out\n`ban`\`unban` - ban\unban someone from guild\n`deafen`\`undefen` - deafen\undefen someone from VC\n`warn` - give warning to someone\n`lock`\`unlock` - locks\unlocks the channel\n`set_welcome_channel` - sets welcome messages channel\n`set_rank_channel` - sets rank updates channel\n`set_social_channel` - Sets up social media updated for the server.",
    "💻 **Dev-Ops**\n`github` – View GitHub Profile.\n`yt` – Search on YouTube.\n`insta` – Seacrh on Instagram.",
    "🎵 **Music & Media**\n`play` – Play songs.\n`queue` – Add songs in queue and View upcoming tracks."
        ]
        menu_cmds = [["joke", "friends"], ["rank", "top", "help"],["rolldice"], ["mute", "kick", "ban", "deafen", "unban", "undefen", "warn", "unmute", "lock", "unlock", "set_welcome_channel", "set_rank_channel", "set_social_channel"],["github","yt" ,"insta"], ["play", "queue"]]
        left = Button(style=ButtonStyle.secondary, custom_id= "left", disabled=True, row=0, emoji=discord.PartialEmoji.from_str("<:leftarrow:1427527800533024839>"))
        right = Button(style=ButtonStyle.secondary, custom_id= "right", row=0, emoji=discord.PartialEmoji.from_str("<:rightarrow:1427527709403119646>"))
        select = Select(custom_id="menu_select", placeholder="Select Category",max_values=1,min_values=1,options=[SelectOption(label=i,value=str(index)) for index, i in enumerate(menu)])
        get_started = Button(custom_id = "get_started", label="Get Started", style=ButtonStyle.green)
        view.add_item(select)
        view.add_item(get_started)
        em = Embed(title="Help Menu", color= Color.green(), type="rich")
        em.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar)
        em.set_footer(text=f"For more help use k help <query>")
        category = None #the category for which help to show default None 
        command = None
        
        def update():
            nonlocal self, cmd, category, em, menu, menu_descrip, command
            em.clear_fields()
            if not cmd and not category:
                em.add_field(name="Fun & Entertainment", value="`joke`,`friends`")
                em.add_field(name="Utility", value="`rank`, `top`, `help`")
                em.add_field(name="Games", value="`rolldice`")
                em.add_field(name="Server Management", value="`mute`, `kick`, `ban`, `deafen`, `unban`, `undefen`, `warn`, `unmute`, `lock`, `unlock`, `set_welcome_channel`, `set_rank_channel`, `set_social_channel`")
                em.add_field(name="Dev-ops", value="`github`,`yt`, `insta`")
                em.add_field(name="Music & Media", value="`play`, `queue`")
            elif cmd:
                for commands in self.client.get_commands():
                    if cmd in commands.name or cmd in commands.aliases:
                        command = commands
                        break
                params = command.clean_params
                title = f"{command.name}"
                for name, value in params.items():
                    if value.required:
                        title += f" <{name}>"
                    else:
                        title += f" [{name}]"
                em.title = title
                if command.aliases:
                    em.description = f"**Aliases**: {command.aliases.join(", ")}\n"
                if command.cooldown:
                    em.description = f"**Cooldown**: {command.cooldown.get_retry_after()}\n"
                em.description = f"**Category**: {menu[category]}\n"
                em.add_field(name="Description", value=command.brief)
                
            elif category:
                em.title = f"Help {menu[category]}"
                em.description = menu_descrip[category]
        
        async def on_click(interaction: Interaction):
            nonlocal em, view, update, left, right, menu_cmds, category, cmd, command
            if not category:
                category = randint(0,5)
                get_stated.label = f"Explore {menu[category]}"
                update()
            elif not cmd:
                cmd = menu_cmds[category][0]
                view.clear_items()
                get_started.label = "Know more"
                view.add_item(left)
                view.add_item(get_started)
                view.add_item(right)
                update()
            else:
                em.clear_fields()
                em.add_field(name="Description", value=command.help)
                get_started.style = ButtonStyle.grey
                get_started.disabled = True 
            
            await interaction.response.edit_message(embed=em, view=view)
        async def on_select(interaction: Interaction):
            nonlocal update, em, view, category
            category = int(interaction.data["values"][0])
            update()
            await interaction.response.edit_message(embed=em, view=view)
        async def on_leftright(interaction: Interaction):
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
                    index == 0
            cmd = menu_cmds[category][index]
            update()

            await interaction.response.edit_message(embed=em, view=view)
                
        async def timeout():
            nonlocal em, msg
            em.color = Color.light_grey()
            await msg.edit(embed=em, view=None)
        view.on_timeout = timeout
        select.on_callback = on_select
        get_started.on_callback = on_click

        update()
        msg = await ctx.send(embed=em, view=view)
        
        
    @commands.command(aliases=[])
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions()
    async def activate(self, ctx):
        '''Server activate command - Moderators only
        - Sets up all settings for your guild.
        - 1.) Sets up Welcome message 
        - 2.) Sets up Social Media notifis
        - 3.) Sets up Rank Channel
        - 4.) Sets up Activated channels/Commands only channels
        - 5.) Sets up timer messages.'''

        client = self.client
        view = View(timeout=60)
        process_no = 0
        welcome_theme_no = 1
        welcome_message = ""
        welcome_channel = 0
        yt = None
        insta = None 
        twitter = None
        social_channel = None
        rank_channel = 0
        activated_channels = []
        timer_messages = False
        
        go_left = Button(style=ButtonStyle.secondary, custom_id= "go_left", disabled=True, row=0, emoji=discord.PartialEmoji.from_str("<:leftarrow:1427527800533024839>"))
        go_right = Button(style=ButtonStyle.secondary, custom_id= "go_right", row=0, emoji=discord.PartialEmoji.from_str("<:rightarrow:1427527709403119646>"))
        proceed_button = Button(style=ButtonStyle.success ,label="Start Setup", custom_id="proceed", row=0)
        skip_button = Button(style=ButtonStyle.secondary ,label="Skip for now", custom_id="skip", row=1)
        channel_select = Select(custom_id="channel", placeholder="Select your Channel", options=[SelectOption(label=channel.name,value=str(channel.id)) for channel in ctx.guild.text_channels], max_values=1, min_values=1)
        channel_select2 = Select(custom_id="channel2", placeholder="Select your redirect to channels in Order.", options=[SelectOption(label=channel.name,value=str(channel.id)) for channel in ctx.guild.text_channels], max_values=5, min_values=1)
                
        em = Embed(title="Welcome to Kelly Bot Setup", description="We are glad that you invited our bot to your server. Follow these simple instructions to set up settings and start chatting with Kelly right now. Thanks for inviting Kelly.", color = Color.gold(), type = "rich")
        em.set_image(url="https://raw.githubusercontent.com/happyharsh-codes/Kasturi/refs/heads/main/assets/welcome_setup.png")
        em.set_author(name= ctx.author.name, icon_url=ctx.authot.avatar)
        class WelcomeModal(discord.ui.Modal):
            def __init__(self):
                super().__init__(title="Set Welcome Message")
                self.input_box = TextInput(label="Edit the Format and Enter.",custom_id="welcome", default= "♡Welcome to <guild_name>\nText 1- eg: Take roles\nText 2 - eg Read Rules\nText 3", required= True, min_length=2, max_length=512, style=TextStyle.paragraph)
                self.add_item(self.input_box)
            async def on_submit(self, interaction: Interaction):
              try:
                nonlocal welcome_message, em, view, proceed_button, channel_select, msg, channel_select2
                welcome_message = self.input_box.value
                channel_select2.row = 0
                channel_select.row = 1
                proceed_button.row = 2

                view.clear_items()
                view.add_item(channel_select2)
                view.add_item(channel_select)
                view.add_item(proceed_button)
                await msg.edit(embed=em, view=view)
                await interaction.response.defer()
                  
              except Exception as e:
                nonlocal client
                await client.get_user(894072003533877279).send(e)
                  
        class SocialModal(discord.ui.Modal):
            def __init__(self):
                super().__init__(title="Set Social Media/ Leave blank for none")
                self.input_box1 = TextInput(label="YouTube Link", custom_id="yt", placeholder="Enter your YouTube Channel Link:", required= False, min_length=0, max_length=50, style=TextStyle.short)
                self.input_box2 = TextInput(label="Insta Id", custom_id="insta", placeholder="Enter your Insta id", required= False, min_length=0, max_length=20, style=TextStyle.short)
                self.input_box3 = TextInput(label="Twitter Id", custom_id="twitter", placeholder="Enter your Twitter Id: ", required= False, min_length=0, max_length=20, style=TextStyle.short)
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
                view.clear_items()
                view.add_item(channel_select)
                proceed_button.label = "Set Social Media Updates Channel"
                view.add_item(proceed_button)
                await msg.edit(embed=em, view=view)
                await interaction.response.defer()
              except Exception as e:
                nonlocal client
                await client.get_user(894072003533877279).send(e)
        async def process_buttons(interaction: discord.Interaction):
            nonlocal welcome_theme_no, process_no, proceed_button, skip_button, go_left, go_right, view, em
            nonlocal welcome_message, welcome_channel, social_channel, rank_channel, activated_channels, timer_messages
            nonlocal WelcomeModal, SocialModal, channel_select, channel_select2, client
            global ServerSettings
            process_no += 1
            try:
              if process_no == 1:
                em.title="Set Welcome message"
                em.description="Set your beautiful welcome message Kelly well send whenever a new user joins the guild.\nSelect your theme from here."
                em.set_image(url="https://raw.githubusercontent.com/happyharsh-codes/Kasturi/refs/heads/main/assets/welcome_message_1.gif")
                view.clear_items()
                proceed_button.label = "Select Theme"
                view.add_item(go_left)       
                view.add_item(proceed_button)
                view.add_item(go_right)
                await interaction.response.edit_message(embed=em,view=view)
                
              if process_no == 2:
                modal = WelcomeModal()
                await interaction.response.send_modal(modal)
              
              if process_no == 3:
                temp = welcome_message.split("\n")[1:]
                welcome_message = welcome_message.split("\n")[0]
                for index, i in enumerate(temp):
                    welcome_message += f"\n[{i}](https://discord.com/channels/{ctx.guild.id}/{channel_select2.values[index]})"
                welcome_channel = int(channel_select.values[0])
                em.description= "Welcome channel set up perfectly.\nYoi can have a preview here:\n"+ welcome_message
                em.set_image(url=None)
                view.clear_items()
                proceed_button.row = 0
                proceed_button.label = "Set Social Media Updates"
                view.add_item(proceed_button)
                await interaction.response.edit_message(embed=em, view=view)
                
              if process_no == 4:
                modal = SocialModal()
                await interaction.response.send_modal(modal)

              if process_no == 5:
                social_channel = int(channel_select.values[0])
                em.title="Set up Rank Channel"
                em.description="Set up your rank channel in which you'll get Level up messages."
                em.set_image(url="https://raw.githubusercontent.com/happyharsh-codes/Kasturi/refs/heads/main/assets/rank.png")
                view.clear_items()
                channel_select.row = 0
                proceed_button.row = 1
                view.add_item(channel_select)
                proceed_button.label = "Set Rank Channel"
                view.add_item(proceed_button)
                view.add_item(skip_button)
                await interaction.response.edit_message(embed=em, view=view)

              if process_no == 6:
                if interaction.data["custom_id"] == "proceed":
                    rank_channel = int(channel_select.values[0])
                em.title="Set up Activated Channels"
                em.description="Set up your activated channels. Activated channels are ones in which anyone can chat with Kelly just by saying anything including word `kelly`. You can select multiple Channels. Notev You can also run commands by say saying `kelly can you mute this @abc for spamming`"
                em.set_image(url="https://raw.githubusercontent.com/happyharsh-codes/Kasturi/refs/heads/main/assets/activated.png")
                view.clear_items()
                channel_select.max_values = 5
                channel_select.row = 0
                view.add_item(channel_select)
                proceed_button.label = "Set Activated Channels"
                proceed_button.row = 1
                view.add_item(proceed_button)
                await interaction.response.edit_message(embed=em, view=view)

              if process_no == 7:
                if interaction.data["custom_id"] == "proceed":
                    activated_channels = list(map(int,channel_select.values))
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
                em.title="Server Setup Completed Successfully ✅"
                em.description="Hurray you completed the server setup. Start Chatting with Kelly, just say `kelly hi`.\n\nExplore music with `k music`\nCheck out fun games with `k games`\nExciting social media search with `k dev`\n"
                em.set_footer(text="Whenever lost in trouble use `k help <query>`.", icon_url = ctx.author.avatar)
                em.set_image(url="https://raw.githubusercontent.com/happyharsh-codes/Kasturi/refs/heads/main/assets/finished.gif")
                ServerSettings[str(ctx.guild.id)]["join/leave_channel"] = welcome_channel
                ServerSettings[str(ctx.guild.id)]["welcome_image"] = welcome_theme_no
                ServerSettings[str(ctx.guild.id)]["allowed_channels"] = activated_channels
                ServerSettings[str(ctx.guild.id)]["social"] = {"yt": yt , "insta": insta, "twitter": twitter, "social_channel": social_channel}
                ServerSettings[str(ctx.guild.id)]["welcome_message"] = welcome_message
                ServerSettings[str(ctx.guild.id)]["rank_channel"] = rank_channel
                ServerSettings[str(ctx.guild.id)]["timer_messages"] = timer_messages
                view.clear_items()
                proceed_button.label = "Finish"
                view.add_item(proceed_button)
                await interaction.response.edit_message(embed=em, view=view)

              if process_no == 9:
                await interaction.response.edit_message(view=None)
                cmd = client.get_command("hi")
                await ctx.invoke(cmd)
                return
            except Exception as e:
                await self.client.get_user(894072003533877279).send(e)
        async def timeout():
            nonlocal msg, em
            em.color = Color.light_grey()
            await msg.edit(embed=em, view=None)

        async def go_callback(interaction: Interaction):
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
            await interaction.response.defer()
        
        go_left.callback = go_callback
        go_right.callback = go_callback
        proceed_button.callback = process_buttons
        skip_button.callback = process_buttons
        channel_select.callback = select_channels
        channel_select2.callback = select_channels
        view.on_timeout = timeout
        view.add_item(proceed_button)
        
        msg = await ctx.reply(embed=em,view=view)

async def setup(bot):
    await bot.add_cog(Utility(bot))
    print("Loaded cogs: Utility")
