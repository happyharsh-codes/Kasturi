from __init__ import*

class Fun(commands.Cog):

    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.hybrid_command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def joke(self, ctx):
        """Tells a random joke to brighten your day 😄  
        Pulls from a large list of one-liners and puns."""
        joke = getResponse("get me a quick joke", "you are a joke master", client=0)
        emoji = choice(["laugh", "gigle", "blush", "bweh", "chips", "juice"])
        emoji = EMOJI[f"kelly{emoji}"]
        await ctx.send(f"{emoji} **|** {joke}")

    """@commands.command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def picture(self, ctx, promt):
        await ctx.send("This command is yet to be made :/")
    """
    
    @commands.hybrid_command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def roast(self, ctx, user:discord.Member):
        """Roast somone"""
        mock_response = getResponse(f"Mock {ctx.author.name} for me", "you are roaster expert (in 20 words)", client=0)
        await ctx.send(f"{user.mention} {mock_response}")

    @commands.hybrid_command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def ask(self, ctx, *, question: str):
        """Ask any question"""
        answer = getResponse(question, "You are intelligent guy answer ther user question with sarcasm (in 20 words)", client=0)
        await ctx.reply(answer)

    @commands.hybrid_command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def heck(self, ctx, user:discord.Member):
        """heck someone: legal"""
        import random, time
        def get_heckstring():
            res = ""
            for i in range(random.randint(3,8)):
                res += random.choice(["$","#","@", "*", "^", "₹", "&","!", "?"])
            return res
        msg = await ctx.reply(f"{ctx.author.name} hecked on {user.mention} : **{get_heckstring()}**")
        for i in range(20):
            await msg.edit(content=f"{ctx.author.name} hecked on {user.mention} : **{get_heckstring()}**")
            time.sleep(0.01)

async def setup(bot):
    await bot.add_cog(Fun(bot))
    print("Loaded cogs: Fun")
