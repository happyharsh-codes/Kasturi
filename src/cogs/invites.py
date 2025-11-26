from __init__ import *

class Invites_Tracker(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.hybrid_command(name="Invites", description="Shows your invite profile")
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.bot_has_permissions(manage_guild = True)
    async def invites(self, ctx: commands.Context):
        """Shows how many users have Joines using your invite link."""
        invites = Server_Settings.get(str(ctx.guild.id)).get("invites", None)
        if not invites:
            await ctx.send(embed = Embed(title= "No Record Found for this Guild"))
            return
            
        invited_ids = []
        for invite in await ctx.guild.invites():
            if invite.inviter.id == ctx.author.id:
                invited_ids.extend(invites.get(str(invite.code)), [])
        
        if not invited_ids:
            em = Embed(title="Showing Invites Profile", description= f"**Total People Invited**: 0\n**Invitees**: N\A", color = Color.purple())
            em.set_thumbnail(url= ctx.author.avatar)
            em.set_footer(text=f"Requested by {ctx.author.name} at {timestamp(ctx)} Aura++", icon_url= ctx.author.avatar)
            await ctx.send(embed=em)
            return
            
        invited_text = ""
        for index, id in enumerate(invited_ids):
            try:
                user = await ctx.guild.fetch_member(id)
                invited_text += f"{user.mention} "
            except:
                invited_text += f"@unknown"
            if index > 9:
                break
                
        em = Embed(title="Showing Invites Profile", description= f"**Total People Invited**: {len(invited_ids)}\n**Invitees**: {invited_text}", color = Color.purple())
        em.set_thumbnail(url= ctx.author.avatar)
        em.set_footer(text=f"Requested by {ctx.author.name} at {timestamp(ctx)} Aura++", icon_url= ctx.author.avatar)
        await ctx.send(embed = em)

async def setup(bot):
    await bot.add_cog(Invites_Tracker(bot))
    print("Loaded cogs: Moderation")
