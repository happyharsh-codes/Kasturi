from __init__ import*
import requests

class Dev_Tech_Tools(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command(aliases=[])
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def github(self, ctx, username, repo=None):
        """Searches GitHub for repositories 💾  
        Returns repo info, owner, stars, and forks."""
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
        """Searches YouTube for videos 🎬  
        Interactive embed with thumbnails and navigation."""
        search_query = search.replace(" ", "+")
        url = (
            "https://www.googleapis.com/youtube/v3/search?"
            "part=snippet&"
            f"maxResults=10&q={search_query}&"
            "type=video&"
            "key=AIzaSyA95DL_DoZMbLZ2brkhWMrfNUq-ErJXYuA"
            )
        videos = []
        page = 1
        response = requests.get(url).json()
        for item in response.get("items", []):
            if item["id"]["kind"] == "youtube#video":
                video_title = item["snippet"]["title"]
                video_id = item["id"]["videoId"]
                video_link = f"https://www.youtube.com/watch?v={video_id}"
                thumbnail_url = item["snippet"]["thumbnails"]["default"]["url"]
                author_name = item["snippet"]["channelTitle"]
                channel_id = item["snippet"]["channelId"]
                url2 = f'https://www.googleapis.com/youtube/v3/channels?part=snippet&id={channel_id}&key=AIzaSyA95DL_DoZMbLZ2brkhWMrfNUq-ErJXYuA'
                response2 = requests.get(url2).json()
                channel_avatar = response2['items'][0]['snippet']['thumbnails']['default']['url']
                
                vid_info = {"title": video_title, "link": video_link, "thumbnail_url": thumbnail_url, "author":author_name, "avatar_url": channel_avatar}
                videos.append(vid_info)

        length = len(videos)
        em = Embed(color=Color.dark_gold())
        if not videos:
            return await ctx.reply("No Video found for the search")
        def updator():
            nonlocal em, videos, page, watch
            current_vid = videos[page-1]
            em.title = f"**{current_vid["title"]}**"
            em.url = current_vid["link"]
            em.set_image(url= current_vid["thumbnail_url"])
            em.set_author(name= current_vid["author"], icon_url= current_vid["avatar_url"])
            em.set_footer(text=f"Showing video {page} out of {length} | {ctx.author.id}", icon_url = ctx.author.avatar)
            watch.url = current_vid["link"]
        left = Button(style=ButtonStyle.secondary, custom_id= "left", disabled=True, row=0, emoji=discord.PartialEmoji.from_str("<:leftarrow:1427527800533024839>"))
        right = Button(style=ButtonStyle.secondary, custom_id= "right", row=0, emoji=discord.PartialEmoji.from_str("<:rightarrow:1427527709403119646>"))
        watch = Button(style=ButtonStyle.link, custom_id = "watch", row=0, label = "Watch")
        view = View(timeout= 45)
        view.add_item(left)
        view.add_item(watch)
        view.add_item(right)
        updator()

        async def on_timeout():
            nonlocal em, msg
            em.color = Color.greyple()
            await msg.edit(embed = em, view = None)
        view.on_timeout = on_timeout
        async def on_leftright(interaction: Interaction):
            nonlocal left, right, page, length, updator, em, view
            if interaction.data["custom_id"] == "left":
                page -= 1
            else: page += 1
            left.disabled = (page == 1)
            right.disabled = (page == length)
            updator()
            await interaction.response.edit_message(embed = em, view = view)
            
        left.callback = on_leftright
        right.callback = on_leftright
        msg = await ctx.reply(embed= em, view= view)

    @commands.command(aliases=["codesnippet"])
    @commands.cooldown(1, 60, type=commands.BucketType.user)
    @commands.has_permissions()
    @commands.bot_has_permissions()
    async def code(self, ctx, language: str = "python", *, snippet: str = None):
        """Runs your code in any language"""
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
        """Search from any Insta Id"""
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
