from __init__ import*

class Moderation(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def mute(self, ctx):
        em = Embed(title="", description="", color=Color.light_gray())
        em.set_footer(text=f"Requested by {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')}", icon_url= ctx.author.avatar)

        await ctx.send(embed=em)

    @commands.command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def unmute(self, ctx):
        em = Embed(title="", description="", color=Color.light_gray())
        em.set_footer(text=f"Requested by {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')}", icon_url= ctx.author.avatar)

        await ctx.send(embed=em)
    
    @commands.command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def kick(self, ctx, user:discord.Member, reason="None"):
        em = Embed(title="Kasturi Kicked a Member", description=f"Kasturi and {ctx.author.name} successfully managed to kick {user.name} out of the server.\n A great milestone achived!!", color=Color.pink())
        em.set_footer(text=f"Requested by {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')}", icon_url= ctx.author.avatar)
        await ctx.guild.kick(user=user, reason=reason)
        await ctx.send(embed=em)

    @commands.command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def ban(self, ctx, user:discord.Member, reason, delete_prev_message_days):
        em = Embed(title="Kasturi Banned a Member", description=f"Kasturi and {ctx.author.name} successfully managed to ban {user.name} from the server.\n A great milestone achived!!\n***Reason:*** {reason}", color=Color.pink())
        em.set_footer(text=f"Requested by {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')}", icon_url= ctx.author.avatar)
        await ctx.guild.ban(user=user, reason=reason, delete_message_days= delete_prev_message_days)
        await ctx.send(embed=em)

    @commands.command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def unban(self, ctx, user:discord.Member, reason="None"):
        em = Embed(title="Kasturi Unbanned a Member", description=f"{user.name} was unbanned by {ctx.author.name}\n***Reason:*** {reason}", color=Color.pink())
        em.set_footer(text=f"Requested by {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')}", icon_url= ctx.author.avatar)
        await ctx.guild.ban(user=user, reason=reason)
        await ctx.send(embed=em)

    @commands.command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def assignrole(self, ctx, user, role):
        pass

    @commands.command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def deafen(self, ctx):
        await ctx.send("This command is yet to be made :/")

    @commands.command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def clean(self, ctx, amount=1):
        await ctx.send("This command is yet to be made :/")

    @commands.command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def slowmode(self, ctx, channel, slowmode):
        await ctx.send("This command is yet to be made :/")

    @commands.command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def purge(self, ctx):
        await ctx.send("This command is yet to be made :/")
        

async def setup(bot):
    await bot.add_cog(Moderation(bot))
    print("Loaded cogs: Moderation")
