from __init__ import*
import requests
from apify_client import ApifyClient

class Dev_Tech_Tools(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.hybrid_command(name="github", description="Seach GitHub Profile/Repo")
    @commands.cooldown(1, 10, type=commands.BucketType.user)
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

    @commands.hybrid_command(name="yt", description="Search Videos on YouTube", aliases=["youtube"])
    @commands.cooldown(1, 30, type=commands.BucketType.user)
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
                url2 = f"https://www.googleapis.com/youtube/v3/channels?part=snippet&id={channel_id}&key=AIzaSyA95DL_DoZMbLZ2brkhWMrfNUq-ErJXYuA"
                response2 = requests.get(url2).json()
                channel_avatar = response2["items"][0]["snippet"]["thumbnails"]["default"]["url"]
                
                vid_info = {
                    "title": video_title,
                    "link": video_link,
                    "thumbnail_url": thumbnail_url,
                    "author": author_name,
                    "avatar_url": channel_avatar
                }
                videos.append(vid_info)

        length = len(videos)
        em = Embed(color=Color.dark_gold())
        if not videos:
            return await ctx.reply("No Video found for the search")

        def updator():
            nonlocal em, videos, page, view, left, right
            current_vid = videos[page-1]
            em.title = f"**{current_vid['title']}**"
            em.url = current_vid["link"]
            em.set_image(url=current_vid["thumbnail_url"])
            em.set_author(name=current_vid["author"], icon_url=current_vid["avatar_url"])
            em.set_footer(text=f"Showing video {page} out of {length} | {ctx.author.id}", icon_url=ctx.author.avatar)
            
            watch = Button(style=ButtonStyle.link, url=current_vid["link"], label="Watch", row=0)
            view.clear_items()
            view.add_item(left)
            view.add_item(watch)
            view.add_item(right)

        left = Button(style=ButtonStyle.secondary, custom_id="left", disabled=True, row=0, emoji=discord.PartialEmoji.from_str("<:leftarrow:1427527800533024839>"))
        right = Button(style=ButtonStyle.secondary, custom_id="right", row=0, emoji=discord.PartialEmoji.from_str("<:rightarrow:1427527709403119646>"))
        view = View(timeout=45)
        updator()

        async def on_timeout():
            nonlocal em, msg
            em.color = Color.greyple()
            await msg.edit(embed=em, view=None)
        view.on_timeout = on_timeout

        async def on_leftright(interaction: Interaction):
            if interaction.user.id != ctx.author.id:
                await interaction.response.send_message(embed = Embed(description= "This interaction is not for you", color = Color.red()), ephemeral= True)
                return
            nonlocal left, right, page, length, updator, em, view
            if interaction.data["custom_id"] == "left":
                page -= 1
            else:
                page += 1
            left.disabled = (page == 1)
            right.disabled = (page == length)
            updator()
            await interaction.response.edit_message(embed=em, view=view)
            
        left.callback = on_leftright
        right.callback = on_leftright
        msg = await ctx.reply(embed=em, view=view)

    @commands.hybrid_command(name="code", description="Enter Code to compile", aliases=["codesnippet"])
    @commands.cooldown(1, 60, type=commands.BucketType.user)
    async def code(self, ctx, language: str = "python", *, code: str = None):
        """Runs your code in any language"""
        if not code:
            await ctx.send("❌ Please provide a code snippet.")
            return
            
        lang = ""
        em = Embed(
            title=f"🧠 Code Snippet ({language})",
            description=f"```{language}\n{snippet[:100]}...```",
            color=Color.blurple()
        )
        em.set_footer(text=f"Shared by {ctx.author.display_name}", icon_url=ctx.author.avatar)
        
        LANG_CONFIG = {"python": {"run": ["python3", "-c"]}, "javascript": {"run": ["node", "-e"]}, "ruby": {"run": ["ruby", "-e"]}, "bash": {"run": ["bash", "-c"]},"php": {"run": ["php", "-r"]}, "cpp": { "compile": ["g++", "-o", "temp_out"],"run": ["./temp_out"],"extension": ".cpp"},  "c": { "compile": ["gcc", "-o", "temp_out"],"run": ["./temp_out"],"extension": ".c"},"java": {"compile": ["javac"], "run": ["java"], "extension": ".java"}}
        
        def execute_code(lang, code):
            if lang not in LANG_CONFIG:
                return f"Language {lang} not supported."
            config = LANG_CONFIG[lang]
            try:
                # HANDLING COMPILED LANGUAGES (C, C++, Java)
                if "compile" in config:
                    filename = f"temp_code{config['extension']}"
                    with open(filename, "w") as f:
                        f.write(code)
                # Compile step
                compile_cmd = config["compile"] + [filename]
                comp = subprocess.run(compile_cmd, capture_output=True, text=True)
                if comp.returncode != 0:
                    return f"Compilation Error:\n{comp.stderr}"
            
                # Run step
                run_cmd = config["run"]
                # Java special case: 'java temp_code' (no extension or path)
                if lang == "java": run_cmd = ["java", "temp_code"]
            
                # HANDLING INTERPRETED LANGUAGES (Python, JS, etc.)
                else:
                    run_cmd = config["run"] + [code]

                # Execute
                result = subprocess.run(run_cmd, capture_output=True, text=True, timeout=5)
                return result.stdout if result.returncode == 0 else result.stderr

            except Exception as e:
                return f"Error: {str(e)}"
            finally:
                # Cleanup temporary files
                for f in ["temp_code.c", "temp_code.cpp", "temp_code.java", "temp_code.class", "temp_out", "temp_out.exe"]:
                    if os.path.exists(f): os.remove(f)
        
        language_select = Select(custom_id="language_select", placeholder="Select Language", required= True, min_values=1, max_values=1, options = [SelectOption(label=i.title(), value=i) for i in list(LAN_CONFIG.keys()))
        compile = Button(style=ButtonStyle.green, label="Run", custom_id="compile", disabled=True)                                                            
        
        async def on_select(inter):
            if inter.user.id != ctx.author.id:
                await inter.response.send_message(embed = Embed(description= "This interaction is not for you", color = Color.red()), ephemeral= True)
                return
            nonlocal language_select, lang
            for option in language_select.options:
                if option.value in inter.data["values"]:
                    option.default = True
                    lang = option.value
                    break
            compile.disabled = False
            await inter.response.edit_message(view=view)

        async def on_compile(inter):
            if inter.user.id != ctx.author.id:
                await inter.response.send_message(embed = Embed(description= "This interaction is not for you", color = Color.red()), ephemeral= True)
                return
            nonlocal execute_code, lang
            output = execute_code(lang, code)
        
        async def on_timeout():
            nonlocal em, msg
            em.color = Color.greyple()
            msg.edit(embed=em, view=None)
            
        view = View(timeout=45)
        view.add_item(language_select)
        view.add_item(compile)
        view.on_timeout = on_timeout
        compile.callback = on_compile
        language_select.callback = on_select
        msg = await ctx.send(embed=em, view=view)

    @commands.hybrid_command(name="insta", description="Search Instagram Profile via Id", aliases=["instagram"])
    @commands.cooldown(1, 30, type=commands.BucketType.user)
    async def insta(self, ctx, username: str):
        """Search for any Instagram Profile"""
        run_input = { "usernames": [username] }

        try:
            run = CLIENT7.actor("dSCLg0C3YEZ83HzYX").call(run_input=run_input)
        except:
            await ctx.reply("Invalid Username Provided")
            return

        posts = []
        data = {}
        page = 1

        for item in CLIENT7.dataset(run["defaultDatasetId"]).iterate_items():
            data.update(item)
        for item in data.get("latestPosts", []):
            posts.append({
                "url": item["url"],
                "caption": item["caption"],
                "likes": item["likesCount"],
                "comments": item["commentsCount"],
                "img": item["displayUrl"]
            })
        em = Embed(
            title="📷 Instagram Lookup",
            description=f"[{data['username']}]({data['url']}) **{data['fullName']}**\n**{data['followersCount']}** Followers **|** **{data['followsCount']}** Following **|** **{data['postsCount']}** Posts\n{data['biography']}",
            color=Color.purple()
        )
        em.set_thumbnail(url=data.get("profilePicUrlHD", None))
        em.set_author(name=username, icon_url=data.get("profilePicUrlHD", None))
        em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar)

        left = Button(style=ButtonStyle.secondary, custom_id="left", disabled=True, row=0, emoji=discord.PartialEmoji.from_str("<:leftarrow:1427527800533024839>"))
        right = Button(style=ButtonStyle.secondary, custom_id="right", row=0, emoji=discord.PartialEmoji.from_str("<:rightarrow:1427527709403119646>"))
        view = View(timeout=45)

        def updator():
            nonlocal em, posts, page, view, left, right
            mypost = posts[page-1]
            em.clear_fields()
            em.add_field(name=f"{mypost['caption'][:64]}", value=f"❤️ {mypost['likes']} 💬 {mypost['comments']}")
            em.set_image(url=mypost["img"])
            watch = Button(style=ButtonStyle.link, url=mypost["url"], label=username, row=0)
            view.clear_items()
            view.add_item(left)
            view.add_item(watch)
            view.add_item(right)

        async def onleftright(interaction: Interaction):
            if interaction.user.id != ctx.author.id:
                await interaction.response.send_message(embed = Embed(description= "This interaction is not for you", color = Color.red()), ephemeral= True)
                return
            nonlocal page, updator, posts, em, view
            left.disabled = (page == 1)
            right.disabled = (page == len(posts))
            if interaction.data["custom_id"] == "left":
                page -= 1
            else:
                page += 1
            updator()
            await interaction.response.edit_message(embed=em, view=view)

        async def on_timeout():
            nonlocal em, msg
            em.color = Color.greyple()
            msg.edit(embed=em, view=None)

        left.callback = onleftright
        right.callback = onleftright
        view.on_timeout = on_timeout
        if posts:
            updator()
        else:
            view = None
        msg = await ctx.send(embed=em, view=view)

async def setup(bot):
    await bot.add_cog(Dev_Tech_Tools(bot))
    print("Loaded cogs: Dev Tech Tools")
