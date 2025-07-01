from __init__ import*

class Dev_Tech_Tools(commands.Cog):
    
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def github(self, ctx, username, repo=None):
        user_url = f"https://api.github.com/users/{username}"
        repos_url = f"https://api.github.com/users/{username}/repos?per_page=5&sort=updated"

        user_resp = requests.get(user_url)
        if user_resp.status_code != 200:
            await ctx.send(f"❌ Couldn't find GitHub user `{username}`.")
            return

        user_data = user_resp.json()
        repos_resp = requests.get(repos_url)
        repos_data = repos_resp.json() if repos_resp.status_code == 200 else []

        em = Embed(
            title=f"{user_data.get('name') or username}'s GitHub Profile",
            url=user_data.get("html_url"),
            description=user_data.get("bio") or "No bio available.",
            color=0x24292e
        )
        em.set_thumbnail(url=user_data.get("avatar_url"))
        em.add_field(name="👥 Followers", value=str(user_data.get("followers")), inline=True)
        em.add_field(name="📦 Public Repos", value=str(user_data.get("public_repos")), inline=True)

        if repos_data:
            repo_lines = []
            for repo in repos_data:
                repo_lines.append(f"[{repo['name']}]({repo['html_url']}) ⭐ {repo['stargazers_count']}")
            em.add_field(name="📁 Recent Repositories", value="\n".join(repo_lines), inline=False)
        else:
            em.add_field(name="📁 Recent Repositories", value="No repositories found.", inline=False)

        em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar)
        await ctx.send(embed=em)
        

    @commands.command(aliases=[])
    @commands.cooldown(1,100, type = commands.BucketType.user )
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def yt(self, ctx, search):
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
