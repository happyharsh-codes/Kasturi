from res.cogs.__init__ import*

class Fun(commands.Cog):

    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def joke(self, ctx):
        await ctx.send("This command is yet to be made :/")

    @commands.command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def picture(self, ctx, promt):
        await ctx.send("This command is yet to be made :/")

    @commands.command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def mock(self, ctx, user:discord.Member):
        await ctx.send("This command is yet to be made :/")

    @commands.command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def ask(self, ctx, question):
        pass

    @commands.command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def heck(self, ctx, user:discord.Member):
        import random, time
        def get_heckstring():
            res = ""
            for i in range(random.randint(3,8)):
                res += random.choice(["$","#","@", "*", "^", "₹", "&","!", "?"])
            return res
        msg = await ctx.reply(f"{ctx.author.name} hecked on {user.mention} : **{get_heckstring()}**")
        for i in range(50):
            await msg.edit(content=f"{ctx.author.name} hecked on {user.mention} : **{get_heckstring()}**")
            time.sleep(0.01)

async def setup(bot):
    await bot.add_cog(Fun(bot))
    print("Loaded cogs: Fun")
