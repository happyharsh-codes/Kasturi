from __init__ import*

class MuiskMedia(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command(aliases=["p"])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def play(self, ctx):
        await ctx.send("This command is yet to be made :/")

    @commands.command(aliases=["q"])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def queue(self, ctx):
        await ctx.send("This command is yet to be made :/")

    @commands.command(aliases=["set yt notifis"])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def set_yt_notifis(self, ctx):
        await ctx.send("This command is yet to be made :/")


async def setup(bot):
    await bot.add_cog(MuiskMedia(bot))
    print("Loaded cogs: MusikMedia")
