from __init__ import*

class Dev_Tech_Tools(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command(aliases=[])
    @commands.cooldown(1, 10, type=commands.BucketType.user)
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
            repo_lines = [
                f"[{repo['name']}]({repo['html_url']}) ⭐ {repo['stargazers_count']}"
                for repo in repos_data
            ]
            em.add_field(name="📁 Recent Repositories", value="\n".join(repo_lines), inline=False)
        else:
            em.add_field(name="📁 Recent Repositories", value="No repositories found.", inline=False)

        em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar)
        await ctx.send(embed=em)

    @commands.command(aliases=["youtube"])
    @commands.cooldown(1, 30, type=commands.BucketType.user)
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def yt(self, ctx, *, search: str):
        em = Embed(
            title="🔍 YouTube Search",
            description=f"Results for `{search}` will be here soon!",
            color=Color.red()
        )
        em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar)
        await ctx.send(embed=em)

    @commands.command(aliases=["codesnippet"])
    @commands.cooldown(1, 60, type=commands.BucketType.user)
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def code(self, ctx, language: str = "python", *, snippet: str = None):
        if not snippet:
            await ctx.send("❌ Please provide a code snippet.")
            return
        em = Embed(
            title=f"🧠 Code Snippet ({language})",
            description=f"```{language}\n{snippet}```",
            color=Color.blurple()
        )
        em.set_footer(text=f"Shared by {ctx.author}", icon_url=ctx.author.avatar)
        await ctx.send(embed=em)

    @commands.command(aliases=["instagram"])
    @commands.cooldown(1, 30, type=commands.BucketType.user)
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def insta(self, ctx, username: str):
        em = Embed(
            title="📷 Instagram Lookup",
            description=f"Feature to lookup Instagram profile `{username}` is under construction.",
            color=Color.purple()
        )
        em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar)
        await ctx.send(embed=em)

async def setup(bot):
    await bot.add_cog(Dev_Tech_Tools(bot))
    print("Loaded cogs: Dev Tech Tools")
