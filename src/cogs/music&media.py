from __init__ import*

class MuiskMedia(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command(aliases=["p"])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def play(self, ctx, search):
        """Plays the Song music 🎶 on your VC"""
        await ctx.send("This command is yet to be made :/")

    @commands.command(aliases=["q"])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def queue(self, ctx):
        """Shows the songs queue list 🎵"""
        await ctx.send("This command is yet to be made :/")

    @commands.command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def skip(self, ctx):
        """Skips the current playing song. Requires voting from all vc members."""
        pass

    @commands.command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def stop(self, ctx):
        """Stops playing the current song. Requires voting from all vc members."""
        pass
        
async def setup(bot):
    await bot.add_cog(MuiskMedia(bot))
    print("Loaded cogs: MusikMedia")
