from __init__ import*

class Dev_Tech_Tools(commands.Cog):
    
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def github(self, ctx, gitub, repo=None):
        link = f"github.com/{gitub}"
        if repo is not None:
            pass
        

    @commands.command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def yt(self, ctx):
        await ctx.send("This command is yet to be made :/")

    @commands.command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def code(self, ctx):
        await ctx.send("This command is yet to be made :/")

    @commands.command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def insta(self, ctx):
        await ctx.send("This command is yet to be made :/")

async def setup(bot):
    await bot.add_cog(Dev_Tech_Tools(bot))
    print("Loaded cogs: Dev Tech Tools")
