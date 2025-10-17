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
        em = Embed(title=f"{user.name}'s Rank", description=f"LEVEl: {level}\nXP: {total_xp}\nRank: {rank_values.index(total_xp) + 1}", color=Color.dark_gold())
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
        total_xp = rank_list.get(str(user.id))
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
        view = View()
        menus= ["Fun & Entertainment", "Utility", "Games", "Server Management", "Dev-Ops", "Music & Media"]
        select = Select(custom_id="menu_select", placeholder="Select Category",max_values=1,min_values=1,options=[SelectOption(label=i,value=i.lower) for i in menus])
        get_started = Button(custom_id = "get_started", label="Get Started", style=ButtonStyle.green)
        view.add(select)
        view.add(get_started)
        if cmd is None:
            em = Embed(title="Help Menu", color= Color.green())
            em.add_field(name="Fun & Entertainment", value="`joke`,`friends`")
            em.add_field(name="Utility", value="`rank`, `top`, `help`")
            em.add_field(name="Games", value="`rolldice`")
            em.add_field(name="Server Management", value="`mute`, `kick`, `ban`, `deafen`, `unban`, `undefen`, `warn`, `unmute`, `lock`, `unlock`, `set_welcome_channel`, `notifis(join/leave/social media)`, `set_rank_channel`")
            em.add_field(name="Dev-ops", value="`github`,`yt`, `insta`")
            em.add_field(name="Music & Media", value="`play`, `queue`")
            em.set_footer(text=f"Requested by {ctx.author.name} at {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')}", icon_url=ctx.author.avatar)
            await ctx.reply(embed=response, view=view)
            return

        with open("res/server/help.json", "r") as f:
            helps = load(f)
        help_list = helps.get(cmd)
        if help_list is None:
            await ctx.reply("User that isnt a valid command you are looking for!")
            return
        response = Embed(title="Help Menu", color= Color.green())
        response.add_field(name=cmd.capitalize(), value=help_list)
        response.set_footer(text=f"Requested by {ctx.author.name} at {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')}", icon_url=ctx.author.avatar)
        await ctx.reply(embed=response)

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

        class WelcomeModal(discord.ui.Modal):
            def __init__(self):
                super().__init__(title="Set Welcome Message")
                self.input_box = TextInput(label="Edit the Format and Enter.",custom_id="welcome", default= "♡Welcome to <guild_name>\nText 1- eg: Take roles\nText 2 - eg Read Rules\nText 3", required= True, min_length=2, max_length=512, style=TextStyle.paragraph)
                self.add_item(self.input_box)
            async def on_submit(self, Interaction: Interaction):
              try:
                nonlocal welcome_message, em, view, proceed_button, channel_select, msg, channel_select2
                welcome_message = self.input_box.value
                view.clear_items()
                view.add_item(channel_select2)
                view.add_item(channel_select)
                view.add_item(proceed_button)
                await msg.edit(embed=em, view=view)
              except Exception as e:
                nonlocal client
                await client.get_user(894072003533877279).send(e)
                  
        class SocialModal(discord.ui.Modal):
            def __init__(self):
                super().__init__(title="Set Social Media/ Leave blank for none")
                self.input_box1 = TextInput(label="YouTube Link", custom_id="yt", placeholder="Enter your YouTube Channel Link:", required= None, min_length=2, max_length=50, style=TextStyle.short)
                self.input_box2 = TextInput(label="Insta Id", custom_id="insta", placeholder="Enter your Insta id", required= None, min_length=2, max_length=20, style=TextStyle.short)
                self.input_box3 = TextInput(label="Twitter Id", custom_id="twitter", placeholder="Enter your Twitter Id: ", required= None, min_length=2, max_length=20, style=TextStyle.short)
                self.add_item(self.input_box1)
                self.add_item(self.input_box2)
                self.add_item(self.input_box3)
            async def on_submit(self, Interaction: Interaction):
              try:
                nonlocal em, yt, insta, twitter, view, proceed_button, msg, channel_select
                yt = self.input_box1.value
                insta = self.input_box2.value
                twitter = self.input_box3.value
                em.title="Set up Social Media Notification"
                em.description="Set up your Social Media whose updates you'll get right here on your selected channel.Enter your correct Id and then select the channel in which you want to get updates."
                em.set_image(url="https://raw.githubusercontent.com/happyharsh-codes/Kasturi/refs/heads/main/assets/social.png")
                view.clear_items()
                view.add_item(channel_select)
                proceed_button.label = "Set Social Media Updates Channel"
                view.add_item(proceed_button)
                await msg.edit(embed=em, view=view)     
              
              except Exception as e:
                await self.client.get_user(894072003533877279).send(e)
        async def process_buttons(interaction: discord.Interaction):
            nonlocal welcome_theme_no, process_no, proceed_button, skip_button, go_left, go_right, view, em
            nonlocal welcome_message, welcome_channel, social_channel, rank_channel, activated_channels, timer_messages
            nonlocal WelcomeModal, SocialModal, channel_select, channel_select2
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
                    welcome_message += f"[{i}](https://discord.com/channels/{ctx.guild.id}/{channel_select2.values[index]})"
                welcome_channel = int(channel_select.values[0])
                em.description= "Welcome channel set up perfectly.\nYoi can have a preview here:\n"+ welcome_message
                
                view.clear_items()
                proceed_button.label = "Set Social Media Updates"
                view.add_item(proceed_button)
                await interaction.response.edit_message(embed=em, view=view)
                
              if process_no == 4:
                modal = SocialModal()
                await interaction.response.send_modal(modal)

              if process_no == 4:
                social_channel = int(channel_select.values[0])
                em.title="Set up Rank Channel"
                em.description="Set up your rank channel in which you'll get Level up messages."
                em.set_image(url="https://raw.githubusercontent.com/happyharsh-codes/Kasturi/refs/heads/main/assets/rank.png")
                view.clear_items()
                view.add_item(channel_select)
                proceed_button.label = "Set Rank Channel"
                view.add_item(proceed_button)
                view.add_item(skip_button)
                await interaction.response.edit_message(embed=em, view=view)

              if process_no == 5:
                if interaction.data["custom_id"] == "proceed":
                    rank_channel = int(channel_select.values[0])
                em.title="Set up Activated Channels"
                em.description="Set up your activated channels. Activated channels are ones in which anyone can chat with Kelly just by saying anything including word `kelly`. You can select multiple Channels. Notev You can also run commands by say saying `kelly can you mute this @abc for spamming`"
                em.set_image(url="https://raw.githubusercontent.com/happyharsh-codes/Kasturi/refs/heads/main/assets/activated.png")
                view.clear_items()
                channel_select.max_values = 5
                view.add_item(channel_select)
                proceed_button.label = "Set Activated Channels"
                view.add_item(proceed_button)
                await interaction.response.edit_message(embed=em, view=view)

              if process_no == 6:
                if interaction.data["custom_id"] == "proceed":
                    activated_channels = list(map(int,channel_select.values))
                em.title="Set up timer Messages"
                em.description="Turn on timer messages to recieve random Kelly mood flex messages on Activated channels. Its always nice to be greeted by Kelly."
                em.set_image(url="https://raw.githubusercontent.com/happyharsh-codes/Kasturi/refs/heads/main/assets/timer.png")
                view.clear_items()
                proceed_button.label = "Set Timer Messages"
                view.add_item(proceed_button)
                view.add_item(skip_button)
                await interaction.response.edit_message(embed=em, view=view)

              if process_no == 7:
                if interaction.data["custom_id"] == "proceed":
                    timer_messages = True
                em.title="Server Setup Completed Successfully ✅"
                em.description="Hurray you completed the server setup. Start Chatting with Kelly, just say `kelly hi`.\nExplore music with `k music`\nCheck out fun games with `k games`\nExciting social media search with `k dev`\n\nWhenever lost in trouble use `k help <query>`."
                em.set_image(url="https://raw.githubusercontent.com/happyharsh-codes/Kasturi/refs/heads/main/assets/finished.gif")
                view.clear_items()
                proceed_button.label = "Finish"
                await interaction.response.edit_message(embed=em, view=view)

              if process_no == 8:
                await interaction.response.edit_message(view=None)
                ServerSettings["join/leave_channel"] = welcome_channel
                ServerSettings["welcome_image"] = welcome_theme_no
                ServerSettings["allowed_channels"] = activated_channels
                ServerSettings["social"] = {"yt": yt , "insta": insta, "twitter": twitter, "social_channel": social_channel}
                ServerSettings["welcome_message"] = welcome_message
                ServerSettings["rank_channel"] = rank_channel
                ServerSettings["timer_messages"] = timer_messages
                #await ctx.invoke()
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
         
        go_left.callback = go_callback
        go_right.callback = go_callback
        proceed_button.callback = process_buttons
        skip_button.callback = process_buttons
        view.on_timeout = timeout
        view.add_item(proceed_button)
        
        msg = await ctx.reply(embed=em,view=view)

async def setup(bot):
    await bot.add_cog(Utility(bot))
    print("Loaded cogs: Utility")
