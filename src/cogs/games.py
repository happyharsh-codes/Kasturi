from __init__ import* 

"""Inventory Items:-
Foods: [🍻🍖🌭🍨🌮..]
Plants: [💐🍂🌵🌴🌳🌲🪵..]
Tools: [🗜️🪛🪚🔧🔨🛠️⚒️⛏️]
Assets: [🏛️🕌🕋🛕⛪💒🏩🏯🏰🏗️🏢🏭🏬🏪🏟️🏦🏫🏨🏣🏤🏥🏚️🏠🏡🏘️🛖⛺🏕️🌃]
Animals: [🐎🐯🦁🐼🐨🐷🫎🐲🦮🐈‍⬛🐈🪽🦇🐤🦂🦀🪱🐾🪰🦋]
Vehicles: [🛴🦽🦼🚲🛵🏍️🚙🚗🛻🚚🚐🚜🏎️🚒🚑🚓🚕🛺🚌🚈🚝🚅🚄🚂🚃🚋🚎🚊🚉]
Emotes:  [kellycute, kellyhappy]
Weapons: [🔫⚔️🏹💣🔪🗡️🛡️🤺]
"""

def weighted_choice(choices: list): 
    choices = [(item, weight)] 
    total = sum(w for _, w in choices) 
    r = random() * total 
    upto = 0 
    for item, w in choices:
        if upto + w >= r: 
            return item
        upto += w
    return choices[-1][0]

def has_profile():
    async def predicate(ctx):
        if str(ctx.author.id) in Profiles:
            Profiles[str(ctx.author.id)]["aura"] += 2
            return True
        code = choice(['i will work under kelly',"i will obey kelly from now on", "i will always bow down to kelly"])
        emoji = EMOJI[f"kelly{choice(['blush', 'thinking', 'laugh', 'gigle', 'waiting', 'idontcare'])}"]
        await ctx.reply(f"**{emoji} | ** you dont even have a profile\n**{choice(['📃','📜','📄','📑','📰','🗞','📚','📙','📕','📖','📗','📘','✒','✏','🖋','📝','📋'])} | **Type this to create new profile `{code}`")
        try:
            msg = await ctx.bot.wait_for("message", check= lambda x: x.author.id == ctx.author.id, timeout= 120)
        except asyncio.TimeoutError:
            return False 
        if msg.content.lower() == code:
            Profiles[str(ctx.author.id)] = {"name": ctx.author.name, "cash": 100, "gem": 1, "inv": {}, "health": 100, "hunger": 100, "aura":0, "skills": {}, "foods": {}, "plants": {}, "assets": {}, "tools": {}, "weapons": {}, "vehicles": {}, "quests": {}, "places": {}, "jobs": {} }
            em = Embed(title="Profile Created Successfully", description=f"{ctx.author.mention} your profile created successfully. Start playing eith game commands now: `hunt`, `chop`, `adv`, `mine`, `work`, `school`, `craft`, `use`, `eat` .., .\n:white_check_mark: You obatained bonous ₹100 cash 💵\n:white_check_mark: You obtained 1 gem 💎\n\nUse `k help games` to get more help and info.",color=Color.green())
            em.set_footer(text=f"{ctx.author.name} created acc at {timestamp(ctx)}", icon_url= ctx.author.avatar)
            await ctx.send(embed = em)
        else:
            emoji = EMOJI[f"kelly{choice(['annoyed', 'laugh', 'gigle', 'waiting', 'idontcare', 'chips', 'bweh', 'bweh'])}"]
            await msg.reply(f"**{emoji} | ** you dont even do a single thing properly disgusting!! Dont ever come to me again")
        
        return False
    return commands.check(predicate)
    
def has_in_inventory(item, value = 0):
    async def predicate(ctx):
        if value == 0 and item in Profiles[str(ctx.author.id)].get("inv", []):
            return True
        elif item in Profiles[str(ctx.author.id)].get("inv", []) and Profiles[str(ctx.author.id)][item] >= value:
            return True
        if value:
            await ctx.reply(embed=Embed(description=f"Ayoo You must have `{item.title()} x {value}` in your inventory to do this."), color= Color.gold())
        else:
            await ctx.reply(embed=Embed(description=f"Ayoo You must need `{item.title()}` in your inventory to perform this."), color= Color.gold())
        return False
    return commands.check(predicate)
    
def at_the_location(loc):
    async def predicate(ctx):
        if loc == Profiles[str(ctx.author.id)].get("loc", ""):
            return True
        await ctx.reply(embed=Embed(description=f"Ayoo You must be in `{loc.title()}` to perform this action."), color= Color.gold())
        return False
    return commands.check(predicate)

class Games(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    def reward_player(self, aura: int, location, drops: dict, count_range=(3,7)):
        rewards = []
        levels_choice = {
            200: {"level1": 0.9, "level2": 0.04, "level3": 0.03, "level4": 0.02, "level5": 0.01},
            400: {"level1": 0.3, "level2": 0.64, "level3": 0.03, "level4": 0.02, "level5": 0.01},
            600: {"level1": 0.1, "level2": 0.2, "level3": 0.65, "level4": 0.03, "level5": 0.02},
            800: {"level1": 0.05, "level2": 0.05, "level3": 0.2, "level4": 0.67, "level5": 0.03},
            1000: {"level1": 0.05, "level2": 0.05, "level3": 0.05, "level4": 0.05, "level5": 0.8}
        }
        if aura > 999:
            count_range = (5,8)
        
        for _ in range(randint(*count_range)):
            # pick category by weight
            category = weighted_choice(list(drops.items()))
    
            # pick reward level
            if aura <= 200:
                level = weighted_choice(list(levels_choice[200].items()))
            elif aura <= 400:
                level = weighted_choice(list(levels_choice[400].items()))
            elif aura <= 600:
                level = weighted_choice(list(levels_choice[600].items()))
            elif aura <= 800:
                level = weighted_choice(list(levels_choice[800].items()))
            else:
                level = weighted_choice(list(levels_choice[1000].items()))
       

            # if category missing levels, skip
            if category not in self.master:
                continue
            if level not in self.master[category]:
                continue
    
            available = DATA["location_items"][location][category][level]

            item = choice(available)
            qty = randint(1, 3)
            if aura > 999:
                qty = randint(3,5)

            rewards.append((category, item, qty, level))

        return rewards


    def rewards_descrip(self, rewards):
        level1 = "<:common:> "
        level2 = "<:special:> "
        level3 = "<:unique:> "
        level4 = "<:rare:> "
        level5 = "<:legendary:> "
    
        for category, item, qty, level in rewards:
            if level == "level1":
                level1 += item * qty
            if level == "level2":
                level2 += item * qty
            if level == "level3":
                level3 += item * qty
            if level == "level4":
                level4 += item * qty
            if level == "level5":
                level5 += item * qty
            
        description = f"{level1}\n{level2}\n{level3}\n{level4}\n{level5}"
    
        return description

    def add_rewards(self, id, rewards):
        for category, item, qty, level in rewards:
            if item in Profiles[str(id)][category]:
                Profiles[str(id)][category][item] += qty
            else:
                Profiles[str(id)][category][item] = qty
                
    @commands.hybrid_command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    @has_profile()
    async def chop(self, ctx, user: None):
        """Shows user profile or mentioned user profile"""
        if not user:
            user = ctx.author
        profile = self.get_profile(ctx.guild.id, ctx.author.id, ctx.author.name)

        em = discord.Embed(title=f"{ctx.author.name}'s Profile", color=discord.Color.purple())
        em.set_thumbnail(url=ctx.author.display_avatar.url)
        em.add_field(name="Cash", value=str(profile["cash"]))
        em.add_field(name="Gems", value=str(profile["gem"]))
        em.add_field(name="Aura", value=str(profile["aura"]))
        em.add_field(name="Health", value=str(profile["health"]))
        em.add_field(name="Hunger", value=str(profile["hunger"]))
        await ctx.reply(embed=em)
        
    @commands.hybrid_command(aliases=['c'])
    @commands.cooldown(1,10, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    @has_profile()
    async def cash(self, ctx):
        """Shows your bank cash balance 🏦"""
        amt = Profiles.get(str(ctx.author.id)).get("cash")
        emoji = EMOJI[f"kelly{choice(['hiding', 'interesting', 'owolove', 'heart', 'simping'])}"]
        await ctx.reply(f"**{emoji} | ** {ctx.author.name} you have **₹{amt}** cash <:cash:1433171762668896388>")

    @commands.hybrid_command(aliases=['g', 'gem'])
    @commands.cooldown(1,10, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    @has_profile()
    async def gems(self, ctx):
        """Shows your bank gem balance 🏦""" 
        amt = Profiles.get(str(ctx.author.id)).get("gem")
        emoji = EMOJI[f"kelly{choice(['hiding', 'interesting', 'owolove', 'heart', 'simping'])}"]
        await ctx.reply(f"**{emoji} | ** {ctx.author.name} you have **{amt}** gems <:gem:1433171777017610260>")

    @commands.hybrid_command(aliases=["inventory"])
    @commands.cooldown(1,10, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    @has_profile()
    async def inv(self, ctx):
        '''Shows your full inventory'''
        foods = Profiles.get(str(ctx.author.id)).get("foods")
        tools = Profiles.get(str(ctx.author.id)).get("tools")
        animals = Profiles.get(str(ctx.author.id)).get("animals")
        vehicles = Profiles.get(str(ctx.author.id)).get("vehicles")
        plants = Profiles.get(str(ctx.author.id)).get("plants")
        assets = Profiles.get(str(ctx.author.id)).get("assets")
        weapons = Profiles.get(str(ctx.author.id)).get("weapons")
        emotes = Profiles.get(str(ctx.author.id)).get("emotes")
        
        inv = [i for i in [foods, plants, animals, weapons, tools, emotes, vehicles, assets] if i ]
            
        if not inv:
            await ctx.reply("You don't have anything in your inventory haha 😆")
            return
        em = Embed(title=f"Showing {ctx.author.name}'s Inventory <:chest:1433174074569396416>")
        em.set_footer(text=f"Requested by {ctx.author.name} at {timestamp(ctx)}", icon_url= ctx.author.avatar)
        
        categ = foods
        menu = Select(custom_id = "value_selector",placeholder = "Select Category", max_values= 1, min_values= 1, options = [SelectOptions(item=i, value=i) for i in ["Foods", "Plants", "Animals", "Assets", "Vehicles", "Emotes", "Tools", "Weapons"]])
        def update():
            nonlocal categ, em
            descrip =  ""
            for item, value in categ:
                descrip += f"`{EMOJI.get(item)} {value}` "
            if not categ:
                descrip = "```Nothing here```"
            em.description += descrip
            
        view = View(timeout =45)
        async def timeout():
            nonlocal msg, em, view 
            for children in view.children:
                children.disabled = True
            em.color = Color.light_grey()
            await msg.edit(embed=em, view=view)
        view.on_timeout = timeout
        view.add_item(menu)
        
        async def on_select(interacion: Interaction):
            if interaction.user.id != ctx.author.id:
                await interaction.response.send_message(embed = Embed(description= "This interaction is not for you", color = Color.red()), ephemeral= True)
                return
            nonlocal em, view, menu, categ, update, foods, tools, weapons, emotes, assets, plants, animals, vehicles
            categ = interaction.data.get("values",[])[0]
            if categ == "Foods":
                categ = foods
            if categ == "Animals":
                categ = animals
            if categ == "Tools":
                categ = tools
            if categ == "Weapons":
                categ = weapons
            if categ == "Vehicles":
                categ = vehicles
            if categ == "Assets":
                categ = assets
            if categ == "Plants":
                categ = plants
            if categ == "Emotes":
                categ = emotes
            update()
            await interaction.response.edit_message(embed = em, view = view)
        
        update()
        menu.callback = on_select
        msg = await ctx.reply(embed=em, view=view)

    @commands.hybrid_command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    @has_profile()
    async def give(self, ctx, user, item, amount: int = 0):
        """Transfers inventory item to other user"""
        profile = Profiles.get(str(ctx.author.id))
        if Profiles.get(str(user)) is None:
            await ctx.reply("Given User profile not found")
            return
        if item.isdigit():
            amount = item
            item = "cash"
        item = item.lower()
        category = None
        for categ in ["plants", "foods", "assets", "animals", "tools", "weapons", "emotes", "vehicles"]:
            if item in profile[categ]:
                category = categ
                break
        if not category:
            await ctx.send("Ayoo That item is not in your inventory")
            return
        if amount <= 0 or amount > 1000:
            await ctx.send("Invalid Amount")
            return
        if anount > profile[category][item]:
            await ctx.send("Ayoo you don't have that much amount in your inventory")
            return
        em = Embed(title="💳 Transfer 💱", description= f"Are you Sure want to give {user.mention} {item} X {amount} ?", color = Color.gold())
        confirm_btn = Button(style=ButtonStyle.green, custom_id="confirm", lable = "✅")
        discard_btn = Button(style=ButtonStyle.secondary, custom_id="discard", lable = "❌")
        
        view = View(timeout=45)
        async def timeout():
            nonlocal em, view, msg
            em.color = Color.light_grey()
            for children in view.children:
                children.disabled = True
            await msg.edit(embed=em, view=view)
        view.on_timeout = timeout
        view.add_item(discard_btn)
        view.add_item(confirm_btn)
        
        async def on_confirm(inter: Interaction):
            if inter.user.id != ctx.author.id:
                return await inter.response.send_message(
                    "This is not your interaction.", ephemeral=True
                )
            nonlocal em, view, category
            Profiles[str(ctx.author.id)][category][item] -= amount 
            if Profiles[str(ctx.author.id)][category][item] == 0:
                Profiles[str(ctx.author.id)][category].pop(item)
            
            if item in Profiles[str(user.id)][category]:
                Profiles[str(user.id)][category][item] += amount
            else:
                Profiles[str(user.id)][category][item] = amount
            
            em.description = f"{kemoji()} Sucessfully sent {item} x {amount} to {user.mention}"
            
            await inter.response.edit_message(embed=em, view=None)
            await ctx.send(f"{user.mention} You recieved a gift", embed = Embed(description=f"You have recieved an item from {ctx.author.mention}\n```{item} x {amount}```", color= Color.green()))
        
        async def on_discard(inter: Interaction):
            if inter.user.id != ctx.author.id:
                return await inter.response.send_message(
                    "This is not your interaction.", ephemeral=True
                )
            nonlocal em, view, category
            em.description = "⚠️ You cancelled the transaction"
            await inter.response.edit_message(embed=em, view=None)
           
        confirm_btn.callback = on_confirm
        discard_btn.callback = on_discard
        
        msg = await ctx.reply(embed=em, view=view)
            
            
    @commands.hybrid_command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    @has_profile()
    async def use(self, ctx, item= None):
        """Uses the selected item from inventory"""
        await ctx.send(embed= Embed(description="This command is yet to be made :/"))
        
    @commands.hybrid_command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    @has_profile()
    async def kill(self, ctx):
        """To Kill spawned mob"""
        profile = Profiles[str(ctx.author.id)]
        aura = profile["aura"]
        loc = profile["loc"]
        
        drops = {
            "foods": 1,
            "animals": 2,
            "tools": 1,
            "weapons": 0.5,
            "vehicles": 0.2,
            "emotes": 0.2
        }

        rewards = self.reward_player(aura, loc, drops)
        self.add_rewards(ctx.author.id, rewards)
        em = Embed(title="Adventure", description= f"You went on adventuring in the {location.capitalize()} and got:\n{self.rewards_descrip(rewards)}", color = Color.green())
        em.set_footer(text=f"Adventure by {ctx.author.display_name} | At {timestamp(ctx)}", icon_url=ctx.author.avatar)
        await ctx.reply(embed=em)
        
    @commands.hybrid_command(aliases=["adv"])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    @has_profile()
    async def adventure(self, ctx):
        """To adventure or find new places, results in exciting rewards"""
        profile = Profiles[str(ctx.author.id)]
        aura = profile["aura"]
        loc = profile["loc"]
        #aura to new location find chance
        
        drops = {
            "foods": 2,
            "plants": 1,
            "animals": 2,
            "tools": 1,
            "weapons": 0.5,
            "assets": 1,
            "vehicles": 0.2,
            "emotes": 0.1
        }

        rewards = self.reward_player(aura, loc, drops)
        self.add_rewards(ctx.author.id, rewards)
        em = Embed(title="Adventure", description= f"You went on adventuring in the {location.capitalize()} and got:\n{self.rewards_descrip(rewards)}", color = Color.green())
        em.set_footer(text=f"Adventure by {ctx.author.display_name} | At {timestamp(ctx)}", icon_url=ctx.author.avatar)
        await ctx.reply(embed=em)
        
    @commands.hybrid_command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    @has_profile()
    async def go(self, ctx, *, place:str = None):
        """Travel to a whole different locations that's your have discovered already using `adventure` or `explore`."""
        places = Profiles[str(ctx.author.id)]["places"]
        if not places:
            await ctx.reply(embed = Embed(description= f"{kemoji()} You have to place to go 🤣! Discover new locations using `k adventure` & `k explore` first.", color = Color.blue()))
            return
            
        go_btn = Button(style=ButtonStyle.green, custom_id="go", lable = "🏃 Go", disabled = True)
        return_btn = Button(style=ButtonStyle.secondary, custom_id="return", lable = "↩️ Return", disabled=True)
       
        place_select = Select(custom_id="places", placeholder="Select Location to go", options=[SelectOption(label=i.replace("_"," ").title(),value=i) for i in places], max_values=1, min_values=1)
        if place:
            if place.replace(" ", "_").lower() not in DATA["places"]:
                await ctx.reply(embed=Embed(description="Invalid Location Provided", color= Color.red()))
                return
            for option in place_select.options:
                if place in option.lable.lower():
                    option.default = True
                    go_btn.disabled = False
                    break
        
        em = Embed(title=f"Travel", description= "Select the location in menu where you want to go then confirm.", color= Color.green())
        
        view = View(timeout = 45)
        async def timeout():
            nonlocal em, view, msg
            em.color = Color.light_grey()
            for children in view.children:
                children.disabled = True
            await msg.edit(embed=em, view=view)
        view.on_timeout = timeout
        view.add_item(place_select)
        view.add_item(go_btn)
        view.add_item(return_btn)
        
        async def on_select(inter: Interaction):
            if inter.user.id != ctx.author.id:
                return await inter.response.send_message(
                    "This is not your interaction.", ephemeral=True
                )
            nonlocal go_btn, view, place_select
            go_btn.disabled = False
            for option in place_select.options:
                if option.value == inter.data["values"][0]:
                    option.default = True
                    break
                    
            await inter.response.edit_message(view=view)
                
        async def on_go(inter: Interaction):
            if inter.user.id != ctx.author.id:
                return await inter.response.send_message(
                    "This is not your interaction.", ephemeral=True
                )
            nonlocal em, view, go_btn, return_btn, place_select
            for option in place_select.options:
                if option.default:
                    loc = option.value
                    option.default = False
                    break
            em.description = f"You started your journey to the {loc.replace('_',' ').title()}. Wait untill you reach the destination"
            em.set_img(url = None)
            view.clear_items()
            view.add_item(return_btn)
            view.add_item(go_btn)
            go_btn.disabled = True
            return_btn.disabled = False
            
            await inter.response.edit_message(embed=em, view=view)
        
        async def on_return(inter: Interaction):
            if inter.user.id != ctx.author.id:
                return await inter.response.send_message(
                    "This is not your interaction.", ephemeral=True
                )
            nonlocal em, view
            return_btn.disabled = True
            
            await inter.response.edit_message(embed=em, view=None)
           
        place_select.callback = on_select
        go_btn.callback = on_go
        return_btn.callnack = on_return
        
        msg = await ctx.reply(embed=em, view=view)
        
    @commands.hybrid_command(aliases=['cr'])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    @has_profile()
    async def craft(self, ctx, item, amt=1):
        """Crafts a new item from inventory"""
        emoji = EMOJI[f"kelly{choice(['hiding', 'ok', 'fight', 'interesting', 'owolove', 'interesting', 'thinking', 'bored', 'interesting'])}"]
        if item not in DATA["craft"]:
            await ctx.send(f"**{emoji} | ** that isnt a craftable item")
            return
        if amt <= 0:
            await ctx.send(f"**{emoji} | ** that isnt a valid amount")
            return
        descrip = ""
        color = Color.green()
        craft = Button(style=ButtonStyle.green, label="Craft")
        for items, value in DATA["craft"][item]:
            if Profiles[str(ctx.author.id)]['inv'][items] >= value*amt:
                descrip += f"`{EMOJI.get(items)} X {value*amt}` :white_check_mark:"
            else:
                descrip += f"`{EMOJI.get(items)} X {value*amt}` :x:"
                craft.disabled = True
                color = Color.red()

        async def on_callback(interaction):
            for items, value in DATA["craft"][item]:
                Profiles[str(ctx.author.id)]['inv'][items] -= (value*amt)

        em = Embed(title=f"Crafting {item.capitalize()}", description=descrip, color=color)
        em.set_footer(text=f"Requested by {ctx.author.name} at {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')}", icon_url= ctx.author.avatar)
        view = View(timeout=30)
        view.add_item(craft)
        msg = await ctx.reply(embed=em, view=view)

        async def on_timeout():
            await msg.edit(view=None)
        
        craft.callback = on_callback
        view.on_timeout = on_timeout
            
    @commands.hybrid_command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    @has_profile()
    async def eat(self, ctx):
        """Eat Items from your inventory."""
        await ctx.send(embed= Embed(description="This command is yet to be made :/"))
        
    @commands.hybrid_command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    @has_profile()
    @has_in_inventory("fishing_rod")
    @at_the_location("river")
    async def fish(self, ctx):
        """Catch Fish directly from the river."""
        profile = Profiles[str(ctx.author.id)]
        aura = profile["aura"]
        loc = profile["loc"]
        
        drops = {
            "foods": 3,
            "tools": 1,
            "plants": 1
        }

        rewards = self.reward_player(aura, loc, drops)
        self.add_rewards(ctx.author.id, rewards)
        em = Embed(title="Adventure", description= f"You went on adventuring in the {location.capitalize()} and got:\n{self.rewards_descrip(rewards)}", color = Color.green())
        em.set_footer(text=f"Adventure by {ctx.author.display_name} | At {timestamp(ctx)}", icon_url=ctx.author.avatar)
        await ctx.reply(embed=em)
     
    @commands.hybrid_command(aliases=["brob"])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    @has_profile()
    async def bankrob(self, ctx):
        """Attempts bankrobbing someones account bases on your aura level"""
        await ctx.send(embed= Embed(description="This command is yet to be made :/"))

    @commands.hybrid_command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    @has_profile()
    async def beg(self, ctx):
        """Begs: unexpected rewards"""
        cash = randint(0, 100)
        sign = choice(["$", "₹", "₹", "₹", "₹", "₹", "₹", "₹", "₹", "₹", "₹", "₹", "₹", "₹", "₹", "₹", "₹", "₹", "₹", "₹", "₹"])
        value = 1
        if sign == "$":
            value = 86
        Profiles[str(ctx.author.id)]["cash"] += cash * value

        await ctx.send(f"**{EMOJI['kelly'+choice(['embaress','laugh','owolove','hiding'])]} | **You got {sign}{cash}")

    @commands.hybrid_command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    @has_profile()
    async def hunt(self, ctx):
        """Goes hunting in the woods"""
        profile = Profiles[str(ctx.author.id)]
        aura = profile["aura"]
        loc = profile["loc"]
        
        drops = {
            "animals": 3,
            "foods": 1,
            "plants": 1
        }

        rewards = self.reward_player(aura, loc, drops)
        self.add_rewards(ctx.author.id, rewards)
        em = Embed(title="Adventure", description= f"You went on adventuring in the {location.capitalize()} and got:\n{self.rewards_descrip(rewards)}", color = Color.green())
        em.set_footer(text=f"Adventure by {ctx.author.display_name} | At {timestamp(ctx)}", icon_url=ctx.author.avatar)
        await ctx.reply(embed=em)
        
    @commands.hybrid_command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    @has_profile()
    async def chop(self, ctx):
        """Goes chopping in the woods"""
        profile = Profiles[str(ctx.author.id)]
        aura = profile["aura"]
        loc = profile["loc"]
        
        drops = {
            "foods": 1,
            "plants": 1,
            "animals": 1,
            "tools": 1,
            "weapons": 0.5,
            "assets": 1,
            "vehicles": 0.2,
            "emotes": 1
        }

        rewards = self.reward_player(aura, loc, drops)
        self.add_rewards(ctx.author.id, rewards)
        em = Embed(title="Chopping", description= f"You went on adventuring in the {location.capitalize()} and got:\n{self.rewards_descrip(rewards)}", color = Color.green())
        em.set_footer(text=f"Chop by {ctx.author.display_name} | At {timestamp(ctx)}", icon_url=ctx.author.avatar)
        await ctx.reply(embed=em)
        
    @commands.hybrid_command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    @has_profile()
    async def battle(self, ctx, user: discord.Member = None):
        """Battle someone: Show your strength.
        Amazing rewards.
        Can also mention user to battle with them otherwise opponent will be selected randomly."""
        await ctx.send(embed= Embed(description="This command is yet to be made :/"))

    @commands.hybrid_command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    @has_profile()
    async def buy(self, ctx):
        """Welcome to the Shop: Buy anything using cash or gems"""
        await ctx.send(embed= Embed(description="This command is yet to be made :/"))

    @commands.hybrid_command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    @has_profile()
    async def sell(self, ctx):
        """Welcome to the Shop: Sell anything and its estimated value on Cash or Gem"""
        await ctx.send(embed= Embed(description="This command is yet to be made :/"))

    @commands.hybrid_command(aliases=["quests", "q"])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    @has_profile()
    async def quest(self, ctx):
        """Complete quests to revir exciting rewards: ✓ Daily Quest ✓ Adventure Quest ✓ Burial Treasure Quest ✓ Premium Quest"""
        await ctx.send(embed= Embed(description="This command is yet to be made :/"))
    
    @commands.hybrid_command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    @has_profile()
    async def work(self, ctx):
        """Work in your Job or Get a new Job"""
        profile = Profiles[str(ctx.author.id)]
        aura = profile["aura"]
        loc = profile["loc"]
        
        drops = {
            "foods": 1,
            "plants": 1,
            "animals": 1,
            "tools": 1,
            "weapons": 0.5,
            "assets": 1,
            "vehicles": 0.2,
            "emotes": 1
        }

        rewards = self.reward_player(aura, loc, drops)
        self.add_rewards(ctx.author.id, rewards)
        em = Embed(title="Work", description= f"You went on adventuring in the {location.capitalize()} and got:\n{self.rewards_descrip(rewards)}", color = Color.green())
        em.set_footer(text=f"Work by {ctx.author.display_name} | At {timestamp(ctx)}", icon_url=ctx.author.avatar)
        await ctx.reply(embed=em)
        
    @commands.hybrid_command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    @has_profile()
    async def mine(self, ctx):
        """Go for Moninin the caves"""
        profile = Profiles[str(ctx.author.id)]
        aura = profile["aura"]
        loc = profile["loc"]
        
        drops = {
            "assets": 3,
            "tools": 1,
            "weapons": 1
        }

        rewards = self.reward_player(aura, loc, drops)
        self.add_rewards(ctx.author.id, rewards)
        em = Embed(title="Mine", description= f"You went on adventuring in the {location.capitalize()} and got:\n{self.rewards_descrip(rewards)}", color = Color.green())
        em.set_footer(text=f"Mine by {ctx.author.display_name} | At {timestamp(ctx)}", icon_url=ctx.author.avatar)
        await ctx.reply(embed=em)
    
    @commands.hybrid_command(aliases=["crop", "crops"])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    @has_profile()
    async def farm(self, ctx):
        """Goes for Cropping your farmland"""
        profile = Profiles[str(ctx.author.id)]
        aura = profile["aura"]
        loc = profile["loc"]
        
        drops = {
            "plants": 3,
            "foods": 2,
        }

        rewards = self.reward_player(aura, loc, drops)
        self.add_rewards(ctx.author.id, rewards)
        em = Embed(title="Farm", description= f"You went on adventuring in the {location.capitalize()} and got:\n{self.rewards_descrip(rewards)}", color = Color.green())
        em.set_footer(text=f"Farm by {ctx.author.display_name} | At {timestamp(ctx)}", icon_url=ctx.author.avatar)
        await ctx.reply(embed=em)
        
    @commands.hybrid_command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    @has_profile()
    async def build(self, ctx):
        """Build Your Favourite Structures"""
        await ctx.send(embed= Embed(description="This command is yet to be made :/"))
        
    @commands.hybrid_command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    @has_profile()
    async def steal(self, ctx, user):
        """Steal item from a user very risky unless you have aura and skill ;>"""
        profile = Profiles[str(ctx.author.id)]
        aura = profile["aura"]
        loc = profile["loc"]
        
        drops = {
            "foods": 1,
            "plants": 1,
            "animals": 1,
            "tools": 1,
            "weapons": 0.5,
            "assets": 1,
            "vehicles": 0.2,
            "emotes": 1
        }

        rewards = self.reward_player(aura, loc, drops)
        self.add_rewards(ctx.author.id, rewards)
        em = Embed(title="Steal", description= f"You went on adventuring in the {location.capitalize()} and got:\n{self.rewards_descrip(rewards)}", color = Color.green())
        em.set_footer(text=f"Steal by {ctx.author.display_name} | At {timestamp(ctx)}", icon_url=ctx.author.avatar)
        await ctx.reply(embed=em)
    
    @commands.hybrid_command(aliases=["exp"])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    @has_profile()
    async def explore(self, ctx):
        """Explores a new place each time a bit dangerous. Consumes more energy and food."""
        profile = Profiles[str(ctx.author.id)]
        aura = profile["aura"]
        loc = profile["loc"]
        #New location find must
        
        drops = {
            "foods": 1,
            "plants": 1,
            "animals": 1,
            "tools": 0.3,
            "weapons": 0.5,
            "assets": 0.2,
            "vehicles": 0.1
        }

        rewards = self.reward_player(aura, loc, drops)
        self.add_rewards(ctx.author.id, rewards)
        em = Embed(title="Explore", description= f"You went on adventuring in the {location.capitalize()} and got:\n{self.rewards_descrip(rewards)}", color = Color.green())
        em.set_footer(text=f"Explore by {ctx.author.display_name} | At {timestamp(ctx)}", icon_url=ctx.author.avatar)
        await ctx.reply(embed=em)
        
    @commands.hybrid_command(aliases=["exp"])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    @has_profile()
    async def trade(self, ctx, item, qty):
        pass
        
    @commands.hybrid_command(aliases=["dm", "daily_missions"])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    @has_profile()
    async def daily(self, ctx, item, qty):
        pass
        
    @commands.hybrid_command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def marry(self, ctx, spouse: discord.Member):
        """Marry someone special 😜💓"""
        assets = Profiles[str(ctx.author.id)]["assets"]
        if "ring" not in assets:
            await ctx.send("Ayoo you need a ring in your inventory to marry someone 😉❤️")
            return
        em = Embed(title= f"🤵{ctx.authot.display_name} Weds {spouse.display_name} 👰", description= f"{ctx.author.display_name} you want to marry {spouse.mention} is that correct ? Please confirm your descision", color=Color.purple())
        em.set_footer(text=f"Marriage attended by {randint(1,8192)} discordians | {timestamp(ctx)} | Aura++", icon_url = ctx.author.avatar)
        
        confirm_btn = Button(style=ButtonStyle.green, custom_id="confirm", lable = "✅")
        discard_btn = Button(style=ButtonStyle.secondary, custom_id="discard", lable = "❌")
       
        view = View(timeout = 45)
        async def timeout():
            nonlocal em, view, msg
            em.color = Color.light_grey()
            for children in view.children:
                children.disabled = True
            await msg.edit(embed=em, view=view)
        view.on_timeout = timeout
        
        view.add_item(confirm_btn)
        view.add_item(discard_btn)
        msg = await ctx.send()
        await ctx.send(embed= Embed(description="This command is yet to be made :/"))
        
async def setup(bot):
    await bot.add_cog(Games(bot))
    print("Loaded cogs: Games")
