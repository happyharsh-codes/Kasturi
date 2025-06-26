from __init__ import*

class Utility(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def invite(self, ctx):
        await ctx.send("[Meet Kelly here](https://discord.com/oauth2/authorize?client_id=1368884334076891136)")

    @commands.command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def vote(self, ctx):
        await ctx.send("This command is yet to be made :/")

    @commands.command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def afk(self, ctx, time, reason):
        Server_Settings[str(ctx.guild.id)]["afk"].append(ctx.author.id)
        await ctx.send(f"{ctx.author.mention} has gone afk for **{time}** : {reason}. Dont ping him unnecessarily, dont worry I'll notify everone...")

    @commands.command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def avatar(self, ctx, user: discord.Member):
        if user is None:
            user = ctx.author
        em = Embed(title=f"{user.display_name}'s Avatar", timestamp=UTC.now())
        em.set_image(url=user.display_avatar)
        await ctx.send(embed=em)

    @commands.command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def info(self, ctx, item):
        await ctx.send("This command is yet to be made :/")


    @commands.command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def premium(self, ctx):
        await ctx.send("This command is yet to be made :/")

    @commands.command(aliases=[])
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def help(self, ctx, cmd = None):
        '''Help command'''
        print(cmd)
        if cmd is None:
            response = Embed(title="Help Menu", color= Color.green())
            response.add_field(name="Fun & Entertainment", value="`joke`,`friends`")
            response.add_field(name="Utility", value="`rank`, `top`, `help`")
            response.add_field(name="Server Management", value="`mute`, `kick`, `ban`, `deafen`, `unban`, `undefen`, `warn`, `unmute`, `lock`, `unlock`, `set channel`, `member join/leave notifis`, `set rank channel`")
            response.add_field(name="Games", value="`rolldice`")
            response.add_field(name="Dev-ops", value="`github`")
            response.add_field(name="Music & Media", value="`play`, `set yt notifis`")
            response.set_footer(text=f"Requested by {ctx.author.name} at {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')}", icon_url=ctx.author.avatar)
            await ctx.reply(embed=response)
            return

        with open("res/server/help.json", "r") as f:
            helps = load(f)
        help_list = helps.get(cmd)
        if help_list is None:
            await ctx.reply("User that isnt a valid command you are looking for!")
            return
        response = Embed(title="Help Menu", color= Color.green())
        response.add_field(name=cmd.capitalize(), value=help_list)
        response.set_footer(text=f"Requested by {ctx.author.name} at {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')}", icon_url=ctx.author.avatar)
        await ctx.reply(embed=response)


async def setup(bot):
    await bot.add_cog(Utility(bot))
    print("Loaded cogs: Utility")
