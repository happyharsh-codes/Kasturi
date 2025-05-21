from res.cogs.__init__ import* 

async def has_not_profile(client, ctx):
    code = 'i will work under kelly'
    emoji = EMOJI[f"kelly{choice(["blush", "thinking", "laugh", "gigle", "waiting", "idontcare"])}"]
    await ctx.reply(f"**{emoji} | Kelly:** you dont even have a profile\n |         Type this to create new profile `{code}`")
    try:
        msg = await client.wait_for("message", check= lambda x: x.author.id == ctx.author.id, timeout= 120)
    except asyncio.TimeoutError:
        pass
    if msg.content.lower() == code:
        with open("res/server/profiles.json", "r") as f:
            profiles = load(f)
        with open("res/server/profiles.json", "w") as f:
            profiles[str(ctx.author.id)] = {"name": ctx.author.name, "cash": 100, "gem": 1, "kelly_repect": 0, "inv": {}, "aura":0, "skills": []}
            dump(profiles, f, indent=4)
        await ctx.send(f"{ctx.author.mention} your profile is successfully created. You can start playing now\nUse `k help` to get help on more `game` commands")
    else:
        emoji = EMOJI[f"kelly{choice(["annoyed", "laugh", "gigle", "waiting", "idontcare", "chips", "bweh", "bweh"])}"]
        await msg.reply(f"**{emoji} | Kelly:** you dont even do a single thing properly disgusting!! Dont ever come to me again")




class Games(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def cash(self, ctx):
        with open("res/server/profiles.json", "r") as f:
            data = load(f).get(str(ctx.author.id))
        if data is None:
            await has_not_profile(self.client, ctx)
            return
        amt = data.get("cash")
        emoji = EMOJI[f"kelly{choice(["hiding", "interesting", "owolove", "heart", "simping"])}"]
        await ctx.reply(f"**{emoji} | Kelly:** {ctx.author.name} you have ₹{amt} cash {EMOJI.get("cash")}")

    @commands.command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def gems(self, ctx):
        with open("res/server/profiles.json", "r") as f:
            data = load(f).get(str(ctx.author.id))
        if data is None:
            await ctx.send("Your profile not found")
        amt = data.get("gems")
        emoji = EMOJI[f"kelly{choice(["hiding", "interesting", "owolove", "heart", "simping"])}"]
        await ctx.reply(f"**{emoji} | Kelly:** {ctx.author.name} you have {EMOJI.get("gem")} {amt} gems")

    @commands.command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def inv(self, ctx):
        '''Views users inventory'''
        with open("res/server/profiles.json", "r") as f:
            data = load(f).get(str(ctx.author.id))
        if data is None:
            await has_not_profile(self.client, ctx)
            return
        inv = data.get("inv")
        tools = data.get("tools")
        if inv == []:
            await ctx.reply("You don't have anything in your inventory haha 😆")
            return
        em = Embed(title=f"Showing {ctx.author.name}'s Inventory {EMOJI.get("inventory")}")
        breakline = 0
        descrip =  ""
        for items, value in inv.items():
            descrip += f"{EMOJI.get(items)} `{value}` "
            breakline += 1
            if breakline%3 == 0:
                descrip += "\n"
        em.set_footer(text=f"Requested by {ctx.author.name} at {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')}", icon_url= ctx.author.avatar)
        await ctx.reply(embed=em)

    @commands.command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def give(self, ctx, user, item, amount=0):
        with open("res/server/profiles.json", "r") as f:
            profiles = load(f)
        user_profile = profiles.get(str(ctx.author.id))
        if user_profile is None:
            await has_not_profile(self.client, ctx)
            return
        if profiles.get(str(user)) is None:
            await ctx.send("Given User profile not found")
        if  isinstance(item, int):
            if item <= 0:
                emoji = EMOJI[f"kelly{choice(["annoyed", "bweh", "watching"])}"]
                await ctx.send(f"**{emoji} | Kelly: **Invalid Cash amount")
                return
            user_cash = user_profile.get("cash")
            if user_cash >= item:
                profiles[str(user)]["cash"] += item
                profiles[str(ctx.author.id)]["cash"] -= item
                with open("res/server/profiles.json", "w") as f:
                    dump(profiles, f, indent=4)
                emoji = EMOJI[f"kelly{choice(["heart", "owolove", "salute"])}"]
                await ctx.send(f"**{emoji} | Kelly: **{ctx.author.mention} gave ₹{item} to {self.client.get_user(user).mention}")
            else:
                emoji = EMOJI[f"kelly{choice(["thinking", "bweh", "watching"])}"]
                await ctx.send(f"**{emoji} | Kelly: **You dont own that much money what are you doing")
        if item in DATA["inv_items"]:
            if amount <= 0:
                emoji = EMOJI[f"kelly{choice(["annoyed", "bweh", "watching"])}"]
                await ctx.send(f"**{emoji} | Kelly: **Invalid amount given")
                return
            if user_profile["inv"][item] >= amount:
                profiles[str(ctx.author.id)]["inv"][item] -= amount
                if item in profiles[str(user)]["inv"]:
                    profiles[str(user)]["inv"][item] += amount
                else:
                    profiles[str(user)]["inv"][item] = amount
                emoji = EMOJI[f"kelly{choice(["heart", "owolove"])}"]
                await ctx.send(f"**.. | Kelly: **{ctx.author.mention} gave {amount} {item.capitalize()} {EMOJI.get(item)} to {self.client.get_user(user).mention}")
            else:
                emoji = EMOJI[f"kelly{choice(["annoyed", "bweh", "watching"])}"]
                await ctx.send(f"**{emoji} | Kelly: **You dont even own that much item what are you doing")
        else:
            emoji = EMOJI[f"kelly{choice(["annoyed", "bweh", "watching"])}"]
            await ctx.reply(f"**{emoji} | Kelly: **Invalid item given")

    @commands.command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def use(self, ctx):
        await ctx.send("This command is yet to be made :/")

    @commands.command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def kill(self, ctx):
        await ctx.send("This command is yet to be made :/")

    @commands.command(aliases=["adv"])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def adventure(self, ctx):
        await ctx.send("This command is yet to be made :/")

    @commands.command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def craft(self, ctx, item, amt=1):
        emoji = EMOJI[f"kelly{choice(["hiding", "ok", "fight", "interesting", "owolove", "interesting", "thinking", "bored", "interesting"])}"]
        if item not in DATA["craft"]:
            await ctx.send(f"**{emoji} | Kelly:** that isnt a craftable item")
            return
        if amt <= 0:
            await ctx.send(f"**{emoji} | Kelly:** that isnt a valid amount")
            return
        with open("res/server/profiles.json", "r") as f:
            profiles = load(f)
        if str(ctx.author.id) not in profiles:
            await has_not_profile(self.client, ctx)
            return
        descrip = ""
        color = Color.green()
        craft = Button(style=ButtonStyle.green, label="Craft")
        for items, value in DATA["craft"][item]:
            if profiles[str(ctx.author.id)]['inv'][items] >= value*amt:
                descrip += f"`{EMOJI.get(items)} X {value*amt}` :white_check_mark:"
            else:
                descrip += f"`{EMOJI.get(items)} X {value*amt}` :x:"
                craft.disabled = True
                color = Color.red()

        async def on_callback(interaction):
            for items, value in DATA["craft"][item]:
                profiles[str(ctx.author.id)]['inv'][items] -= (value*amt)

        em = Embed(title=f"Crafting {item.capitalize()}", description=descrip, color=color)
        em.set_footer(text=f"Requested by {ctx.author.name} at {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')}", icon_url= ctx.author.avatar)
        view = View(timeout=30)
        view.add_item(craft)
        msg = await ctx.reply(embed=em, view=view)

        async def on_timeout():
            await msg.edit(view=None)
        
        craft.callback = on_callback
        view.on_timeout = on_timeout
            
    @commands.command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def bankrob(self, ctx):
        await ctx.send("This command is yet to be made :/")

    @commands.command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def beg(self, ctx):
        cash = randint(0, 1000)
        sign = choice(["$", "₹", "₹", "₹", "₹", "₹", "₹", "₹", "₹", "₹", "₹", "₹", "₹", "₹", "₹", "₹", "₹", "₹", "₹", "₹", "₹"])
        value = 1
        with open("res/server/profiles.json", "r") as f:
            profiles = load(f)
        if str(ctx.author.id) not in profiles:
            await has_not_profile(self.client, ctx)
            return
        with open("res/server/profiles.json", "w") as f:
            if sign == "$":
                value = 86
            profiles[str(ctx.author.id)]["cash"] += cash * value

        await ctx.send(f"You got {sign}{cash}")
        



async def setup(bot):
    await bot.add_cog(Games(bot))
    print("Loaded cogs: Games")
