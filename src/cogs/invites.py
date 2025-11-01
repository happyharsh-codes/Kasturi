from __init__ import *

class Invites_Tracker(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command(aliases=[])
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def invites(self, ctx: commands.Context):
        """Shows how many users have Joines using your invite link."""
        server = INVITER.get(str(ctx.guild.id), None)
        if not server:
            await ctx.send(embed = Embed(title= "No Record Found for this Guild"))
        invited = []
        for invited, inviter in server.items():
            if inviter == ctx.author.id:
                invited.append(int(invited))
        em = Embed(title="Showing Invites Profile", description= f"**Total People Invited**: {len(invited)}\n", color = Color.purple())
        em.set_thumbnail(url= ctx.author.avatar)
        if invited:
            if len(invited) > 5:
                invited = invited[:5]
            for id in invited:
                user = self.client.get_user(int(id))
                if user:
                    em.description += f"{user.mention}\n"
                else:
                    em.description += f"@unknown"
        em.set_footer(text=f"Requested by {ctx.author.name} at {timestamp(ctx)}", icon_url= ctx.author.avatar)
        await ctx.send(embed = em)

async def setup(bot):
    await bot.add_cog(Invites_Tracker(bot))
    print("Loaded cogs: Moderation")
