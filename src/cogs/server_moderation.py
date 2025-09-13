from __init__ import *

class Moderation(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command()
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def mute(self, ctx: commands.Context, member: discord.Member, *, reason: str = "No reason provided"):
        em = Embed(title="Member Muted", description=f"{member.mention} was muted.\n**Reason:** {reason}", color=Color.light_gray())
        em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def unmute(self, ctx: commands.Context, member: discord.Member):
        em = Embed(title="Member Unmuted", description=f"{member.mention} was unmuted.", color=Color.light_gray())
        em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx: commands.Context, user: discord.Member, *, reason: str = "No reason provided"):
        await ctx.guild.kick(user=user, reason=reason)
        em = Embed(title="Member Kicked", description=f"{user.mention} was kicked by {ctx.author.mention}.\n**Reason:** {reason}", color=Color.pink())
        em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx: commands.Context, user: discord.Member,*, reason: str = "No reason provided"):
        await ctx.guild.ban(user=user, reason=reason, delete_message_days=0)
        em = Embed(title="Member Banned", description=f"{user.name} was banned by {ctx.author.mention}.\n**Reason:** {reason}", color=Color.pink())
        em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def unban(self, ctx: commands.Context, user_tag: str, *, reason: str = "No reason provided"):
        async for entry in ctx.guild.bans():
            if entry.user.name.lower() == user_tag.lower() or entry.user.id == int(user_tag):
                await ctx.guild.unban(entry.user, reason= reason)
                em = Embed(title="Member Unbanned", description=f"{entry.user.name} was unbanned by {ctx.author.mention}.\n**Ban Reason:** {entry.reason}\n**Unban Reason:** {reason}", color=Color.red())
                em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar)
                await ctx.send(embed=em)
                dm_channel = await entry.user.create_dm()
                try:
                    await dm_channel.send(content=f"Hurray! You just got unbanned from the guild `{ctx.guild.name}`.\n Click here to join again:\n{Server_Settings[str(ctx.guild.id)]["invite_link"]}")
                except:
                    pass
                return
        await ctx.send("User not found in ban list.")

    @commands.command()
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def assignrole(self, ctx: commands.Context, member: discord.Member, role: discord.Role):
        await member.add_roles(role)
        em = Embed(title="Role Assigned", description=f"{role.mention} assigned to {member.mention}", color=Color.green())
        em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.has_permissions(deafen_members=True)
    @commands.bot_has_permissions(deafen_members=True)
    async def deafen(self, ctx: commands.Context, member: discord.Member, state: bool):
        await member.edit(deafen=state)
        status = "Deafened" if state else "Undeafened"
        em = Embed(title="Voice Status Changed", description=f"{member.mention} was {status.lower()} by {ctx.author.mention}.", color=Color.light_gray())
        em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def clean(self, ctx: commands.Context, amount: int = 5):
        deleted = await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f"Deleted {len(deleted) - 1} messages.", delete_after=5)

    @commands.command()
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def slowmode(self, ctx: commands.Context, channel: discord.TextChannel, seconds: int):
        await channel.edit(slowmode_delay=seconds)
        await ctx.send(f"Slowmode set to `{seconds}` seconds in {channel.mention}")

    @commands.command()
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def purge(self, ctx: commands.Context, amount: int = 5):
        deleted = await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f"Purged {len(deleted) - 1} messages.", delete_after=5)

    @commands.command()
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def set_rank_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        Server_Settings[str(ctx.guild.id)]["rank_channel"] = channel.id
        em = Embed(title="Rank Channel Set :white_check_mark:", description="Rank channel set successfully.\nNow everyone can start gaining xp point on every message, voice and activities.\nFor more details and customization visit [Kasturi_Methi.com](https://www.kasturi_methi.com/kelly)", color= Color.red())
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def set_welcome_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        Server_Settings[str(ctx.guild.id)]["join/leave_channel"] = channel.id
        em = Embed(title="Welcome Channel Set :white_check_mark:", description=f"Welcome Channel set successfully.\nNow you'll recieve exclusive messages on members joining and leaving the server in {channel.mention}\nFor more details and customization visit [Kasturi_Methi.com](https://www.kasturi_methi.com/kelly)", color= Color.red())
        await ctx.send(embed=em)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
    print("Loaded cogs: Moderation")
