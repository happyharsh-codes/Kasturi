from __init__ import* 

def has_profile():
    async def predicate(ctx):
        if str(ctx.author.id) in Profiles:
            Profiles[str(ctx.author.id)]["aura"] += 2
            return True
        return False
    return commands.check(predicate)

class Games(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command(aliases=['c'])
    @commands.cooldown(1,10, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    @has_profile()
    async def cash(self, ctx):
        amt = Profiles.get(str(ctx.author.id)).get("cash")
        emoji = EMOJI[f"kelly{choice(["hiding", "interesting", "owolove", "heart", "simping"])}"]
        await ctx.reply(f"**{emoji} | ** {ctx.author.name} you have ₹{amt} cash {EMOJI.get("cash")}")

    @commands.command(aliases=['g', 'gem'])
    @commands.cooldown(1,10, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    @has_profile()
    async def gems(self, ctx):
        amt = Profiles.get(str(ctx.author.id)).get("gem")
        emoji = EMOJI[f"kelly{choice(["hiding", "interesting", "owolove", "heart", "simping"])}"]
        await ctx.reply(f"**{emoji} | ** {ctx.author.name} you have {EMOJI.get("gem")} {amt} gems")

    @commands.command(aliases=["inventory"])
    @commands.cooldown(1,10, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    @has_profile()
    async def inv(self, ctx):
        '''Views users inventory'''
        inv = Profiles.get(str(ctx.author.id)).get("inv")
        tools = Profiles.get(str(ctx.author.id)).get("tools")
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
    @has_profile()
    async def give(self, ctx, user, item, amount=0):
        user_profile = Profiles.get(str(ctx.author.id))
        if Profiles.get(str(user)) is None:
            await ctx.send("Given User profile not found")
        if  isinstance(item, int):
            if item <= 0:
                emoji = EMOJI[f"kelly{choice(["annoyed", "bweh", "watching"])}"]
                await ctx.send(f"**{emoji} | **Invalid Cash amount")
                return
            user_cash = user_profile.get("cash")
            if user_cash >= item:
                Profiles[str(user)]["cash"] += item
                Profiles[str(ctx.author.id)]["cash"] -= item
                emoji = EMOJI[f"kelly{choice(["heart", "owolove", "salute"])}"]
                await ctx.send(f"**{emoji} | **{ctx.author.mention} gave ₹{item} to {self.client.get_user(user).mention}")
            else:
                emoji = EMOJI[f"kelly{choice(["thinking", "bweh", "watching"])}"]
                await ctx.send(f"**{emoji} | **You dont own that much money what are you doing")
        if item in DATA["inv_items"]:
            if amount <= 0:
                emoji = EMOJI[f"kelly{choice(["annoyed", "bweh", "watching"])}"]
                await ctx.send(f"**{emoji} | **Invalid amount given")
                return
            if user_profile["inv"][item] >= amount:
                Profiles[str(ctx.author.id)]["inv"][item] -= amount
                if item in Profiles[str(user)]["inv"]:
                    Profiles[str(user)]["inv"][item] += amount
                else:
                    Profiles[str(user)]["inv"][item] = amount
                emoji = EMOJI[f"kelly{choice(["heart", "owolove"])}"]
                await ctx.send(f"**{emoji}| **{ctx.author.mention} gave {amount} {item.capitalize()} {EMOJI.get(item)} to {self.client.get_user(user).mention}")
            else:
                emoji = EMOJI[f"kelly{choice(["annoyed", "bweh", "watching"])}"]
                await ctx.send(f"**{emoji} | **You dont even own that much item what are you doing")
        else:
            emoji = EMOJI[f"kelly{choice(["annoyed", "bweh", "watching"])}"]
            await ctx.reply(f"**{emoji} | **Invalid item given")

    @commands.command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    @has_profile()
    async def use(self, ctx):
        await ctx.send("This command is yet to be made :/")

    @commands.command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    @has_profile()
    async def kill(self, ctx):
        await ctx.send("This command is yet to be made :/")

    @commands.command(aliases=["adv"])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    @has_profile()
    async def adventure(self, ctx):
        await ctx.send("This command is yet to be made :/")

    @commands.command(aliases=['cr'])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    @has_profile()
    async def craft(self, ctx, item, amt=1):
        emoji = EMOJI[f"kelly{choice(["hiding", "ok", "fight", "interesting", "owolove", "interesting", "thinking", "bored", "interesting"])}"]
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
            
    @commands.command(aliases=["brob"])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    @has_profile()
    async def bankrob(self, ctx):
        await ctx.send("This command is yet to be made :/")

    @commands.command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    @has_profile()
    async def beg(self, ctx):
        cash = randint(0, 1000)
        sign = choice(["$", "₹", "₹", "₹", "₹", "₹", "₹", "₹", "₹", "₹", "₹", "₹", "₹", "₹", "₹", "₹", "₹", "₹", "₹", "₹", "₹"])
        value = 1
        if sign == "$":
            value = 86
        Profiles[str(ctx.author.id)]["cash"] += cash * value

        await ctx.send(f"**{EMOJI["kelly"+choice(["embaress","laugh","owolove","hiding"])]} | **You got {sign}{cash}")

async def setup(bot):
    await bot.add_cog(Games(bot))
    print("Loaded cogs: Games")
