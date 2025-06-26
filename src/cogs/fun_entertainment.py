from __init__ import*

class Fun(commands.Cog):

    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def joke(self, ctx):
        joke = getResponse("get me a quick joke", "you are a joke master", client=3)
        emoji = choice(["laugh", "gigle", "blush", "bweh", "chips", "juice"])
        emoji = EMOJI[f"kelly{emoji}"]
        await ctx.send(f"{emoji} **|** {joke}")

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
        mock_response = getResponse(f"Mock {ctx.author.name} for me", "you are mocker expert (in 20 words)", client=3)
        await ctx.send(f"{user.mention} {mock_response}")

    @commands.command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def ask(self, ctx, question):
        answer = getResponse(question, "You are intelligent guy answer ther user question with sarcasm (in 20 words)", client=3)
        await ctx.reply(answer)

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
