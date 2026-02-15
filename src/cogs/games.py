from __init__ import *
from functions.game_functions import *
from typing import Optional

def action_embed(title, description, color, footer=None, avatar=None):
    em = Embed(title=title, description=description, color=color)
    if footer:
        em.set_footer(text=footer, icon_url=avatar)
    return em
    
class Games(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        
    # ========= PROFILE & WALLET =========

    @commands.hybrid_command(aliases=[])
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @has_profile()
    async def profile(self, ctx, user: Optional[discord.Member] = None):
        if not user:
            user = ctx.author
        try:
            profile = GameProfile(user.id)
        except:
            return await ctx.reply(embed=Embed(description="That user dont even have a game profile!!", color=Color.red()))
        descrip = (
            f"Wallet:\n"
            f"**Cash**: {profile.assets.get('cash', 0)}\n"
            f"**Gems**: {profile.assets.get('gem', 0)}\n"
            f"**Orbs**: {profile.assets.get('orb', 0)}"
        )
        em = action_embed(f"{user.display_name}'s Profile", descrip, Color.green(), f"Profile used by {ctx.author.name}", ctx.author.avatar)
        await ctx.send(embed=em)

    @commands.hybrid_command(aliases=["bal", "wallet", "cash"])
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @has_profile()
    async def balance(self, ctx):
        profile = GameProfile(ctx.author.id)
        if profile.assets.get('cash', 0) < 100:
            descrip = (
            f"<:wallet:1472453144863572032> Wallet:\n"
            f"<:cash:1433171762668896388> **Cash**: {profile.assets.get('cash', 0)} {choice(['<a:lowonmoney:1433171892365168700>','<:broke:1472453147665371267>'])}\n"
            f"<a:gem:1433171777017610260> **Gems**: {profile.assets.get('gem', 0)}\n"
            f"<:orb:1472550711551201300> **Orbs**: {profile.assets.get('orb', 0)}"
            )
        descrip = (
            f"<:wallet:1472453144863572032> Wallet:\n"
            f"<:cash:1433171762668896388> **Cash**: {profile.assets.get('cash', 0)}\n"
            f"<a:gem:1433171777017610260> **Gems**: {profile.assets.get('gem', 0)}\n"
            f"<:orb:1472550711551201300> **Orbs**: {profile.assets.get('orb', 0)}"
        )
        em = action_embed(f"{ctx.author.display_name}'s Wallet",descrip,Color.green(),f"Bal used by {ctx.author.name}",ctx.author.avatar)
        await ctx.send(embed=em)

    # ========= INVENTORY =========

    @commands.hybrid_command(aliases=[])
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @has_profile()
    async def inv(self, ctx):
        """View categorized inventory."""
        categories = ["eatables", "animals", "plants", "assets", "tools", "weapons", "vehicles", "minerals", "builds"]
        profile = GameProfile(ctx.author.id)
        page = 0
        em = action_embed(f"{ctx.author.display_name}'s Inventory","",Color.green(),f"Inv by {ctx.author.name}",ctx.author.avatar)
        
        #buttons
        left_btn = Button(emoji="<:leftarrow:1427527800533024839>", custom_id="left", style=ButtonStyle.blurple, disabled=True)
        expand_btn = Button(label="Show", custom_id="expand", style=ButtonStyle.blurple)
        right_btn = Button(emoji="<:rightarrow:1427527709403119646>", custom_id="right", style=ButtonStyle.blurple)
        
        def update(selected_category):
            nonlocal em, profile, left_btn, right_btn, page
            left_btn.disabled = page == 0
            right_btn.disabled = page == len(categories)-1
            
            descrip = f"**{selected_category.title()}**\n"
            items = profile.get(selected_category, {})
    
            for item_key, val in items.items():
                emoji = GAME["id"][item_key]["emoji"]
                descrip += f"`{emoji} {val}` "
                
            if not descrip:
                descrip += "`No items in this category`"
            em.description = descrip
        category_select = Select(custom_id="category",placeholder="Select Category",options=[SelectOption(label=i.title(), value=i) for i in categories],max_values=1,min_values=1)
        
        async def on_select(inter: Interaction):
            nonlocal update, em, view, categories, page
            if inter.user.id != ctx.author.id:
                return await inter.response.send_message(embed=Embed(description="This interaction is not for you", color=Color.red()),ephemeral=True)
            page = categories.index(inter.data["values"][0])
            update(inter.data["values"][0])
            await inter.response.edit_message(embed=em, view=view)

        async def on_click(inter: Interaction):
            nonlocal left_btn, expand_btn, right_btn, update, em, view, categories, page
            if inter.user.id != ctx.author.id:
                return await inter.response.send_message(embed=Embed(description="This interaction is not for you", color=Color.red()),ephemeral=True)
            
            if inter.data["custom_id"] == "left":
                page -= 1
                update(categories[page])
            elif inter.data["custom_id"] == "right":
                page +=1
                update(categories[page])
            else:
                nonlocal em, profile
                selected_category = categories[page]
                descrip = f"**{selected_category.title()}**\n"
                items = profile.get(selected_category, {})
                
                for item_key, val in items.items():
                    emoji = GAME["id"][item_key]["emoji"]
                    descrip += f"`{item_key}` {emoji} x {val}\n"
                if not descrip:
                    descrip += "`No items in this category`"
                em.description = descrip 
            await inter.response.edit_message(embed=em, view=view)
            
        async def on_timeout():
            nonlocal msg, view, em
            em.color = Color.light_grey()
            for child in view.children:
                child.disabled = True
            await msg.edit(embed=em, view=view)

        view = View(timeout=45)
        view.on_timeout = on_timeout
        view.add_item(category_select)
        view.add_item(left_btn)
        view.add_item(expand_btn)
        view.add_item(right_btn)
        category_select.callback = on_select
        left_btn.callback = on_click
        expand_btn.callback = on_click
        right_btn.callback = on_click
        update("eatables")
        msg = await ctx.send(embed=em, view=view)

    # ========= SIMPLE ECONOMY =========

    @commands.hybrid_command(aliases=[])
    @commands.cooldown(1, 1000, type=commands.BucketType.user)
    @has_profile()
    async def beg(self, ctx):
        profile = GameProfile(ctx.author.id)
        beg_amt = randint(1, 100)
        await ctx.send(f"{ctx.author.mention} You got {beg_amt} <:cash:1433171762668896388> in your bowl!! {kemoji()}")
        profile.inv_manager("cash", beg_amt)

    # ========= WORK / JOBS =========

    @commands.hybrid_command(aliases=["job"])
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @has_profile()
    @not_busy()
    async def work(self, ctx):
        """Work in your Job or get a new Job, for regular wages."""
        profile = GameProfile(ctx.author.id)
        options = [
            SelectOption(label="Doctor", description="The Life saver god; Earns: 1,00,000/hour",emoji=discord.PartialEmoji.from_str("🩺"), value="doctor"),
            SelectOption(label="Engineer", description="New Innovations and Constructions; Earns: 1,00,000/hour",emoji=discord.PartialEmoji.from_str("🧰"), value="engineer"),
            SelectOption(label="Teacher", description="Lead the youth; Earns: 50,000/hour",emoji=discord.PartialEmoji.from_str("📚"), value="teacher"),
            SelectOption(label="Programmer", description="Epitome of technology; Earns: 80,000/hour",emoji=discord.PartialEmoji.from_str("💻"), value="programmer"),
            SelectOption(label="Chef", description="Perfection in Taste; Earns: 34,000/hour",emoji=discord.PartialEmoji.from_str("🍳"), value="chef"),
            SelectOption(label="Blacksmith", description="Always Forging with Metals; Earns: 25,600/hour",emoji=discord.PartialEmoji.from_str("⚒️"), value="blacksmith"),
            SelectOption(label="Farmer", description="The Food provider; Earns: 30,000/hours",emoji=discord.PartialEmoji.from_str("🌾"), value="farmer"),
            SelectOption(label="Fisherman", description="Handy with Fishes; Earns: 19,000/hour",emoji=discord.PartialEmoji.from_str("🎣"), value="fisherman"),
            SelectOption(label="Hunter", description="Classical old Nomad Hunter; Earns: 10,000/hour",emoji=discord.PartialEmoji.from_str("🏹"), value="hunter"),
        ]
        selected = None
        salary = {
            "doctor": 100000,
            "engineer": 100000,
            "teacher": 50000,
            "programmer": 80000,
            "chef": 34000,
            "blacksmith": 25600,
            "farmer": 30000,
            "fisherman": 19000,
            "hunter": 10000,
        }
        category_select = Select(
            custom_id="profession",
            placeholder="Select Profession",
            options=options,
            max_values=1,
            min_values=1,
        )
        work_btn = Button(label="Work", custom_id="work", style=ButtonStyle.green, disabled=True)

        em = action_embed(
            "Professions To Work",
            "Select your profession to work at. It requires specific `skills` for each job. Make sure you have enough skills or learn them at `k school`",
            Color.green(),
            f"Work by {ctx.author.name}",
            ctx.author.avatar,
        )

        def update(option: SelectOption):
            nonlocal em
            if not option:
                em.description = "Select a profession from the menu."
                return
            needed_skills = GAME["jobs"].get(option.value, [])
            descrip = (
                f"**{option.label}** {option.emoji}\n"
                f"{option.description}\n"
                f"**Skills Required**: {', '.join(needed_skills) if needed_skills else 'None'}\n"
                f"**Salary**: {salary[option.value]}"
            )
            em.description = descrip

        view = View(timeout=45)

        async def on_select(inter: Interaction):
            nonlocal profile, selected, work_btn, category_select, em, view, update
            if inter.user.id != ctx.author.id:
                await inter.response.send_message(embed=Embed(description="This interaction is not for you", color=Color.red()),ephemeral=True)
                return
            selected_val = inter.data["values"][0]
            for opt in category_select.options:
                opt.default = (opt.value == selected_val)
                if opt.value == selected_val:
                    selected = opt

            profile_skills = profile.skills
            required = GAME["jobs"].get(selected.value, [])
            if all(skill in profile_skills and profile_skills.get(skill,0) > 0 for skill in required):
                work_btn.disabled = False
                work_btn.label = "Work"
            else:
                work_btn.disabled = True
                work_btn.label = "Job not available"

            view.clear_items()
            view.add_item(category_select)
            view.add_item(work_btn)
            update(selected)
            await inter.response.edit_message(embed=em, view=view)

        async def on_work(inter: Interaction):
            if inter.user.id != ctx.author.id:
                await inter.response.send_message(embed=Embed(description="This interaction is not for you", color=Color.red()),ephemeral=True)
                return
            nonlocal profile, selected, em, salary, msg
            sal = salary[selected.value]
            skill = profile.skills[selected.value]
            if skill < 20:
                sal += randint(-10000,500)
            elif skill < 60:
                sal += randint(-2000, 2000)
            elif skill == 100:
                sal += 10000
            else:
                sal += randint(1,5000)
            em.description = f"You Started Working!!! You'll be notified when you are done."
            await inter.response.edit_message(embed=em, view=None)
            profile.add_task("working", randint(3600,7200), inter.channel_id, inter.message.id, salary = sal, profession = selected.value)
            profile.activity = "working"
            view.timeout = None
            
        async def timeout():
            em.color = Color.light_grey()
            for child in view.children:
                child.disabled = True
            await msg.edit(embed=em, view=view)

        view.on_timeout = timeout
        category_select.callback = on_select
        work_btn.callback = on_work
        view.add_item(category_select)
        update(None)
        msg = await ctx.send(embed=em, view=view)

    # ========= SCHOOL / SKILLS =========

    @commands.hybrid_command(aliases=["skills"])
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @has_profile()
    @not_busy()
    async def school(self, ctx):
        profile = GameProfile(ctx.author.id)
        options = [
            SelectOption(label="Math", description="Integration & Calculus: 2 hours", emoji="➗", value="math"),
            SelectOption(label="Science", description="Innovate & discover: 2 hours", emoji="🔬", value="science"),
            SelectOption(label="Geography", description="Explore the world: ½ hour", emoji="🗺️", value="geography"),
            SelectOption(label="Mechanics", description="Build & design: 3 hours", emoji="🛠️", value="mechanics"),
            SelectOption(label="Cooking", description="Master of flavors: ½ hour", emoji="🍳", value="cooking"),
            SelectOption(label="Programming", description="Code the future: 1 hour", emoji="💻", value="programming"),
            SelectOption(label="Teaching", description="Guide young minds: 1 hour", emoji="📚", value="teaching"),
            SelectOption(label="Farming", description="Grow & harvest: ½ hour", emoji="🌾", value="farming"),
            SelectOption(label="Hunting", description="Track & surviven: 1½ hour", emoji="🏹", value="hunting"),
            SelectOption(label="Fishing", description="Catch & sustain: ½ hour", emoji="🎣", value="fishing"),
        ]
        selected = None
        time_req = {
            "math": 7200,
            "science": 7200,
            "geography": 1800,
            "mechanics": 10800,
            "cooking": 1800,
            "programming": 3600,
            "teaching": 3600,
            "farming": 5400,
            "hunting": 1800,
            "fishing": 1800,
        }
        category_select = Select(
            custom_id="skill",
            placeholder="Select Skill",
            options=options,
            max_values=1,
            min_values=1,
        )
        study_btn = Button(label="Study", custom_id="study", style=ButtonStyle.green, disabled=True)

        em = action_embed(
            "Skills to Learn",
            "Select your skills to learn. It requires time and patience, but helps in `k work`.",
            Color.green(),
            f"School by {ctx.author.name}",
            ctx.author.avatar,
        )

        def update(option: Optional[SelectOption]):
            nonlocal em
            if not option:
                em.description = "Select a skill from the menu."
                return
            jobs = [x for x in GAME["jobs"] if option.value in DATA["jobs"][x]]
            descrip = (
                f"**{option.label}** {option.emoji}\n"
                f"{option.description}\n"
                f"**Jobs Offered**: {', '.join(jobs) if jobs else 'None'}\n"
                f"**Time**: {time_req[option.value]} seconds"
            )
            em.description = descrip

        view = View(timeout=45)

        async def on_select(inter: Interaction):
            nonlocal selected, view, em, study_btn
            if inter.user.id != ctx.author.id:
                await inter.response.send_message(embed=Embed(description="This interaction is not for you", color=Color.red()),ephemeral=True)
                return
            selected_val = inter.data["values"][0]
            for opt in category_select.options:
                opt.default = (opt.value == selected_val)
                if opt.value == selected_val:
                    selected = opt
            study_btn.disabled = False
            view.clear_items()
            view.add_item(category_select)
            view.add_item(study_btn)
            update(selected)
            await inter.response.edit_message(embed=em, view=view)

        async def on_study(inter: Interaction):
            if inter.user.id != ctx.author.id:
                await inter.response.send_message(embed=Embed(description="This interaction is not for you", color=Color.red()),ephemeral=True)
                return
            nonlocal profile, selected, time_req, em, view
            due = time_req[selected.value]
            em.description += "\nYou have started studying. Wait until your classes finish. You wont be able to use many commands in this duration."
            await inter.response.edit_message(embed=em, view=None)
            view.timeout = None
            profile.add_task("studying", due, inter.channel_id, inter.message.id, subject = selected.value)
            profile.activity = "studying"
            
        async def timeout():
            em.color = Color.light_grey()
            for child in view.children:
                child.disabled = True
            await msg.edit(embed=em, view=view)

        view.on_timeout = timeout
        category_select.callback = on_select
        study_btn.callback = on_study
        view.add_item(category_select)
        update(None)
        msg = await ctx.send(embed=em, view=view)

    # ========= ACTIVITY COMMANDS =========

    @commands.hybrid_command(aliases=["h"])
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @has_profile()
    @not_busy()
    async def hunt(self, ctx):
        profile = GameProfile(ctx.author.id)
        loc = profile.location
        drops = {
            "animals": 3,
            "eatables": 1,
            "plants": 1,
            "minerals": 0.1
        }

        rewards = profile.reward_player(drops)
        if not rewards:
            return await ctx.reply(embed=Embed(description=f"{kemoji()} You have got nothing in this place 🤣! Make sure you are at the correct location with `k travel`. Discover new locations using `k explore`.",color=Color.blue()))
            
        await ctx.reply(embed= Embed(title=f"Hunting in the {loc.capitalize()}", description=rewards,color=Color.green()))

    @commands.hybrid_command(aliases=[])
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @has_profile()
    @not_busy()
    async def chop(self, ctx):
        """Goes chopping in the woods."""
        profile = GameProfile(ctx.author.id)
        loc = profile.location
        drops = {
            "eatables": 0.1,
            "plants": 0.9,
            "animals": 0.1
        }

        rewards = profile.reward_player(drops)
        if not rewards:
            return await ctx.reply(embed=Embed(description=f"{kemoji()} You have got nothing in this place 🤣! Make sure you are at the correct location with `k travel`. Discover new locations using `k explore`.",color=Color.blue()))
            
        await ctx.reply(embed= Embed(title=f"Chopping in the {loc.capitalize()}", description=rewards,color=Color.green()))

    @commands.hybrid_command(aliases=[])
    @commands.cooldown(1, 3600, type=commands.BucketType.user)
    @has_profile()
    @at_the_location(["home", "farm"])
    @not_busy()
    async def farm(self, ctx):
        """Goes for cropping and harvesting the farmland."""
        profile = GameProfile(ctx.author.id)
        loc = profile.location
        drops = {
            "crops": 2,
            "eatables": 0.4
        }

        rewards = profile.reward_player(drops)
        if not rewards:
            return await ctx.reply(embed=Embed(description=f"{kemoji()} You have got nothing in this place 🤣! Make sure you are at the correct location with `k travel`. Discover new locations using `k explore`.",color=Color.blue()))
            
        await ctx.reply(embed= Embed(title=f"Farming in the {loc.capitalize()}", description=rewards,color=Color.green()))

    @commands.hybrid_command(aliases=[])
    @commands.cooldown(1, 3600, type=commands.BucketType.user)
    @has_profile()
    @not_busy()
    async def mine(self, ctx):
        """Go for mining rare items in the caves."""
        profile = GameProfile(ctx.author.id)
        loc = profile.location   
        drops = {
            "weapons": 0.02,
            "minerals": 0.98,
            "assets": 0.03
        }

        rewards = profile.reward_player(drops)
        if not rewards:
            return await ctx.reply(embed=Embed(description=f"{kemoji()} You have got nothing in this place 🤣! Make sure you are at the correct location with `k travel`. Discover new locations using `k explore`.",color=Color.blue()))
            
        await ctx.reply(embed= Embed(title=f"Mining in the {loc.capitalize()}", description=rewards,color=Color.green()))

    @commands.hybrid_command(aliases=[])
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @has_profile()
    @has_in_inventory("fishing_rod")
    @not_busy()
    async def fish(self, ctx):
        """Catch fish directly from the river."""
        profile = GameProfile(ctx.author.id)
        loc = profile.location
        drops = {
            "fish": 10,
            "tools": 1,
            "plants": 1,
            "weapons": 1,
        }
        rewards = profile.reward_player(drops)
        if not rewards:
            return await ctx.reply(embed=Embed(description=f"{kemoji()} You have got nothing in this place 🤣! Make sure you are at the correct location with `k travel`. Discover new locations using `k explore`.",color=Color.blue()))
            
        await ctx.reply(embed= Embed(title=f"Fishing in the {loc.capitalize()}", description=rewards,color=Color.green()))

    @commands.hybrid_command(aliases=["adv"])
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @has_profile()
    async def adventure(self, ctx):
        """Adventure or find new places, results in exciting rewards."""
        profile = GameProfile(ctx.author.id)
        loc = profile.location
        drops = {
            "eatables": 2,
            "plants": 1,
            "animals": 2,
            "tools": 1,
            "weapons": 0.5,
            "assets": 1,
            "vehicles": 0.2
        }

        rewards = profile.reward_player(drops)
        if not rewards:
            return await ctx.reply(embed=Embed(description=f"{kemoji()} You have got nothing in this place 🤣! Make sure you are at the correct location with `k travel`. Discover new locations using `k explore`.",color=Color.blue()))
            
        await ctx.reply(embed= Embed(title=f"Adventure in the {loc.capitalize()}", description=rewards,color=Color.green()))

    @commands.hybrid_command(aliases=["exp"])
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @has_profile()
    @not_busy()
    async def explore(self, ctx):
        """Explores a new place each time. A bit dangerous, consumes more energy and food."""
        profile = GameProfile(ctx.author.id)
        loc = profile.location
        places = GAME["places"]
        new_place = weighted_choice(list(places.items()))
        drops = {
            "eatables": 1,
            "plants": 1,
            "animals": 1,
            "tools": 0.3,
            "weapons": 0.5,
            "assets": 0.2,
            "vehicles": 0.1,
        }
        
        if not profile.places or new_place in profile.places:
            explore_time = randint(1,20)
            em = Embed(title="Exploration",description=f"You started your adventurous exploration. Wait until you find something amazing.", color = Color.green())
            em.set_image(url="attachment://travel.gif")
            gif = discord.File("travel.gif")
            profile.location = "exploring"
            profile.activity = "exploring"
            await ctx.send(file=gif, embed=em)
            await asyncio.sleep(explore_time)
            profile.location = new_place
            profile.activity = "sleeping"
            rewards = profile.reward_player(drops)  
            em = Embed(title="Explore",description=f"You explored around {new_place.capitalize()} and got:\n{rewards}",color=Color.green())  
            profile.place_manager(new_place)
            em.set_footer(text=f"Explore by {ctx.author.display_name} | At {timestamp(ctx)}",icon_url=ctx.author.avatar)  
            return await ctx.send(f"{ctx.author.mention} Exploration Finished: You found a {new_place}! You can adventure here now using `k adventure`.", embed=em)
            
        explore_time = randint(1000,3000)
        em = Embed(title="Exploration",description=f"You started your adventurous exploration. Wait until you find something amazing.", color = Color.green())
        em.set_image(url="attachment://travel.gif")
        gif = discord.File("travel.gif")
        msg = await ctx.send(file=gif, embed=em)
        profile.add_task("exploring", explore_time, msg.channel.id, msg.id, drops = drops, place = new_place)
        profile.activity = "exploring"
        profile.location = "exploring"

    # ========= TRAVEL =========

    @commands.hybrid_command(aliases=["go"])
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @has_profile()
    @not_busy()
    async def travel(self, ctx, *, place: Optional[str] = None):
        """Travel to different locations that you have discovered already."""
        profile = GameProfile(ctx.author.id)
        places = list(profile.places.keys())
        location = profile.location
        if location != "home":
            places.append("home")
        if not places:
            return await ctx.reply(embed=Embed(description=f"{kemoji()} You have no place to go 🤣! Discover new locations using `k explore` first.",color=Color.blue()))
        if place:
            loc = place.replace(" ","_").lower()
            if loc not in places:
                return await ctx.send("Invalid Place given")
            travel_time = randint(1,20)
            generate_travel_gif(profile.location.replace("_"," ").title(), place.title(), travel_time, 1, "km")
            em = Embed(title="Travel",description=f"You started your journey to the {place.title()}. Wait until you reach the destination.", color = Color.green())
            em.set_image(url="attachment://travel.gif")
            gif = discord.File("travel.gif")
            
            profile.location = "travelling"
            profile.activity = "travelling"
           
            await ctx.send(file=gif, embed=em)
            await asyncio.sleep(travel_time)
            profile.location = loc
            profile.activity = "sleeping"
            return await ctx.send(f"{ctx.author.mention} you have reached {place.title()}")
                
        go_btn = Button(style=ButtonStyle.green, custom_id="go", label="🏃 Go", disabled=True)
        #return_btn = Button(style=ButtonStyle.secondary, custom_id="return", label="↩️ Return", disabled=True)

        place_select = Select(custom_id="places",placeholder="Select Location to go",options=[SelectOption(label=i.replace('_', ' ').title(), value=i) for i in places],max_values=1,min_values=1,)
        em = Embed(title="Travel",description="Select the location in menu where you want to go then confirm.",color=Color.green())
        view = View(timeout=45)
        async def timeout():
            em.color = Color.light_grey()
            for child in view.children:
                child.disabled = True
            await msg.edit(embed=em, view=view)

        view.on_timeout = timeout
        view.add_item(place_select)
        view.add_item(go_btn)
        #view.add_item(return_btn)

        async def on_select(inter: Interaction):
            if inter.user.id != ctx.author.id:
                return await inter.response.send_message("This is not your interaction.", ephemeral=True)
            nonlocal go_btn, place_select, view
            go_btn.disabled = False
            for option in place_select.options:
                option.default = (option.value == inter.data["values"][0])
            await inter.response.edit_message(view=view)

        async def on_go(inter: Interaction):
          try:
            if inter.user.id != ctx.author.id:
                return await inter.response.send_message("This is not your interaction.", ephemeral=True)
            nonlocal place_select, em, view, msg, profile
            for option in place_select.options:
                if option.default:
                    loc = option.value
                    break
            travel_time = randint(1,20)
            generate_travel_gif(profile.location.title(), loc.title(), travel_time, 1, "km")
            gif = discord.File("travel.gif")
            em.description = f"You started your journey to the {loc.replace('_', ' ').title()}. Wait until you reach the destination."
            em.set_image(url="attachment://travel.gif")
            profile.location = "travelling"
            protile.activity = "travelling"
            view.timeout = None
            await inter.response.edit_message(file=gif, embed=em, view=None)
            await asyncio.sleep(travel_time)
            profile.location = loc
            profile.activity = "sleeping"
            return await ctx.send(f"{ctx.author.mention} you have reached {loc.title()}")
          except Exception as e:
              await inter.client.get_user(894072003533877279).send(str(e))
        async def on_return(inter: Interaction):
            if inter.user.id != ctx.author.id:
                return await inter.response.send_message("This is not your interaction.", ephemeral=True)
            nonlocal em
            #return_btn.disabled = True
            em.description = f"You arrived at {profile.location.replace('_', ' ').title()}."
            await inter.response.edit_message(embed=em, view=None)

        place_select.callback = on_select
        go_btn.callback = on_go
        #return_btn.callback = on_return

        msg = await ctx.reply(embed=em, view=view)

    # ========= FEED / BUILD / STEAL =========

    @commands.hybrid_command(aliases=["eat", "food"])
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @has_profile()
    async def feed(self, ctx, item: Optional[str] = None, amount: int = 1):
        """Eat items from your inventory."""
        profile = GameProfile(ctx.author.id)
        if item and item.lower() not in DATA["eatables"]:
            await ctx.send("Specify a food item to eat.")
            return
        eatables = profile.eatables
        em = Embed(title="Eat Foods", description= f"Health: \n**{health_string(profile.health)}**\nHunger: \n**{hunger_string(profile.hunger)}**", color = Color.green())
        em.set_footer(text=f"Eat by {ctx.author.display_name} {timestamp(ctx)}")
        view = View(timeout=45)
        async def timeout():
            em.color = Color.light_grey()
            for child in view.children:
                child.disabled = True
            await msg.edit(embed=em, view=view)
        view.on_timeout = timeout
        def update():
            nonlocal em, view, on_eat
            em.description= f"Health: \n**{health_string(profile.health)}**\nHunger: \n**{hunger_string(profile.hunger)}**"
            view.clear_items()
            if not eatables:
                em.description += "\nYou have nothing to eat"
            for food in list(eatables.keys())[:25]:
                btn = Button(label= f"{GAME['id'][food]['emoji']} x {eatables[food]}", style=ButtonStyle.blurple, custom_id= f"{food}_{eatables[food]}") 
                btn.callback = on_eat
                view.add_item(btn)
        
        async def on_eat(inter: Interaction):
          try:
            if inter.user.id != ctx.author.id:
                return await inter.response.send_message("This is not your interaction.", ephemeral=True)
            nonlocal eatables, em, view, update
            food = inter.data["custom_id"].split("_")[0]
            profile.inv_manager(food, 1)
            eatables[food] -= 1
            if eatables[food] == 0:
                del eatables[food]
            update()
            await inter.response.edit_message(embed=em, view=view)
          except Exception as e:
            await inter.client.get_user(894072003533877279).send(str(e))
              
        update()
        msg = await ctx.reply(embed=em, view=view)

    @commands.hybrid_command(aliases=[])
    @commands.cooldown(1, 200, type=commands.BucketType.user)
    @has_profile()
    @at_the_location("home")
    async def build(self, ctx, *, item: str):
        """Build your favourite structures."""
        profile = GameProfile(ctx.author.id)
        cards = []
        builds = []
        page = 1
        build_btn = Button(label = "Build", custom_id="build", style=ButtonStyle.green)
        go_left = Button(style=ButtonStyle.secondary, custom_id= "go_left", disabled=True, row=0, emoji=discord.PartialEmoji.from_str("<:leftarrow:1427527800533024839>"))
        go_right = Button(style=ButtonStyle.secondary, custom_id= "go_right", row=0, emoji=discord.PartialEmoji.from_str("<:rightarrow:1427527709403119646>"))
        for build, requirements in DATA["build"].items():
            can_build = True
            em = Embed(title= f"Build {build.replace('_',' ').title()}", description= "Building Recipe Requires:")
            for item, amt in requirements.items():
                if profile.inv_searcher(item, amt):
                    em.description += f"\n✅ `{item}` {DATA['id'][item]} x {amt}"
                else:
                    em.description += f"\n❌ `{item}` {DATA['id'][item]} x {amt}"
                    can_build = False
            if can_build:
                em.color = Color.green()
            else:
                em.color = Color.red()
            cards.append(em)
            time = randint(1800, 10800)
            time_str = f"**{time//3600}**hrs **{time//60}**min"
            em.add_field(name="Time:", value=time_str)
            builds[build] = time

        if item:
            item = item.replace(" ","_").lower() 
            if not item in DATA["build"]:
                return await ctx.reply("Invalid Build item")
            page = list(builds.keys()).index(item) + 1 
        
        async def on_build(inter: Interaction):
          try:  
            if inter.user.id != ctx.author.id:
                return await inter.response.send_message("This is not your interaction.", ephemeral=True)
            nonlocal builds, page, view
            build_item = list(builds.keys())[page-1]
            for item, amt in DATA["build"][build_item]:
                profile.inv_manager(item, -amt)
            view = None
            time = builds[build_item]
            em = cards[page-1]
            em.description = f"You Started Building `{build_item}`. Wait until your build is finished. **Duration**:\n**{time//3600}**hrs **{time//60}**min\n. Build will automatically show in your profile once finished."
            generate_travel_gif("", "", time, 1, "percentage")
            gif = discord.File(f"travel.gif")
            em.set_image(url= f"attachment://travel.gif")
            await inter.response.edit_message(file=gif, embed=em, view=None)
            profile.add_reminder("building", time, inter.channel_id, inter.message.id)
          except Exception as e:
            await inter.client.get_user(894072003533877279).send(str(e))
        
        async def on_go(inter: interaction):
          try:
            if inter.user.id != ctx.author.id:
                return await inter.response.send_message("This is not your interaction.", ephemeral=True)
            nonlocal page, cards, go_left, go_right, view, build_btn
            if inter.data["custom_id"] == "go_left":
                page -= 1
            else: page += 1
            go_left.disabled = page == 1
            go_right.disabled = page == len(cards)
            em = cards[page-1]
            build_btn.disabled = em.color == Color.red()
            await inter.response.edit_message(embed=em, view=view)
          except Exception as e:
            await inter.client.get_user(894072003533877279).send(str(e))
        view = View(timeout=45)
        async def timeout():
            em.color = Color.light_grey()
            for child in view.children:
                child.disabled = True
            await msg.edit(embed=em, view=view)

        view.on_timeout = timeout
        view.add_item(go_left)
        view.add_item(build_btn)
        view.add_item(go_right)
        build_btn.disabled = cards[page-1].color == Color.red()
        msg = await ctx.send(embed=cards[page-1], view=view)
        
    @commands.hybrid_command(aliases=[])
    @commands.cooldown(1, 100, type=commands.BucketType.user)
    @has_profile()
    async def steal(self, ctx, user: discord.Member):
        """Steal item from a user. Very risky unless you have aura and skill."""
        thief_id = str(ctx.author.id)
        victim_id = str(user.id)
        if thief_id == victim_id:
            await ctx.send("You cannot steal from yourself.")
            return
        if victim_id not in Profiles:
            await ctx.send("Target profile not found.")
            return
        thief_aura = Profiles[thief_id]["aura"]
        victim_aura = Profiles[victim_id]["aura"]
        success_chance = max(10, min(90, 50 + (thief_aura - victim_aura) // 10))
        if randint(1, 100) > success_chance:
            fine = min(Profiles[thief_id]["assets"].get("cash", 0), 100)
            inv_manager(thief_id, "cash", -fine)
            await ctx.send(f"You got caught stealing! You paid a fine of {fine}.")
            return
        # pick random non-cash item
        victim_inv = Profiles[victim_id].get("foods", {})
        if not victim_inv:
            await ctx.send("Victim has nothing worth stealing (foods category checked).")
            return
        item_key = choice(list(victim_inv.keys()))
        inv_manager(victim_id, item_key, -1)
        inv_manager(thief_id, item_key, 1)
        await ctx.send(f"You successfully stole {DATA['id'].get(item_key, item_key)} from {user.mention}!")

    # ========= CRAFT / TRADE / GIVE / USE =========

    @commands.hybrid_command(aliases=[])
    @commands.cooldown(1, 100, type=commands.BucketType.user)
    @has_profile()
    async def craft(self, ctx, item: str, qty: int = 1):
        """Craft a new item from inventory."""
        profile = GameProfile(ctx.author.id)
        cards = []
        crafts = []
        page = 1
        build_btn = Button(label = "Build", custom_id="build", style=ButtonStyle.green)
        go_left = Button(style=ButtonStyle.secondary, custom_id= "go_left", disabled=True, row=0, emoji=discord.PartialEmoji.from_str("<:leftarrow:1427527800533024839>"))
        go_right = Button(style=ButtonStyle.secondary, custom_id= "go_right", row=0, emoji=discord.PartialEmoji.from_str("<:rightarrow:1427527709403119646>"))
        for craft, requirements in DATA["build"].items():
            can_build = True
            em = Embed(title= f"Build {build.replace('_',' ').title()}", description= "Building Recipe Requires:")
            for item, amt in requirements.items():
                if profile.inv_searcher(item, amt):
                    em.description += f"\n✅ `{item}` {DATA['id'][item]} x {amt}"
                else:
                    em.description += f"\n❌ `{item}` {DATA['id'][item]} x {amt}"
                    can_build = False
            if can_build:
                em.color = Color.green()
            else:
                em.color = Color.red()
            cards.append(em)
            time = randint(10, 200)
            time_str = f"**{time//3600}**hrs **{time//60}**min"
            em.add_field(name="Time:", value=time_str)
            crafts[craft] = time

        if item:
            item = item.replace(" ","_").lower() 
            if not item in DATA["craft"]:
                return await ctx.reply("Invalid Build item")
            page = list(craft.keys()).index(item) + 1 
        
        async def on_build(inter: Interaction):
            if inter.user.id != ctx.author.id:
                return await inter.response.send_message("This is not your interaction.", ephemeral=True)
            nonlocal crafts, page, view
            build_item = list(crafts.keys())[page-1]
            for item, amt in DATA["build"][build_item]:
                profile.inv_manager(item, -amt)
            view = None
            time = crafts[build_item]
            em = cards[page-1]
            em.description = f"You Started Building `{build_item}`. Wait until your build is finished. **Duration**:\n**{time//3600}**hrs **{time//60}**min\n. Build will automatically show in your profile once finished."
            generate_travel_gif("", "", time, 1, "percentage")
            gif = discord.File(f"travel.gif")
            em.set_image(url= f"attachment://travel.gif")
            await inter.response.edit_message(file=gif, embed=em, view=None)
            profile.add_reminder("building", time, inter.channel_id, inter.message.id)
            
        async def on_go(inter: interaction):
            if inter.user.id != ctx.author.id:
                return await inter.response.send_message("This is not your interaction.", ephemeral=True)
            nonlocal page, cards, go_left, go_right, view, build_btn
            if inter.data["custom_id"] == "go_left":
                page -= 1
            else: page += 1
            go_left.disabled = page == 1
            go_right.disabled = page == len(cards)
            em = cards[page-1]
            build_btn.disabled = em.color == Color.red()
            await inter.response.edit_message(embed=em, view=view)
        
        view = View(timeout=45)
        async def timeout():
            em.color = Color.light_grey()
            for child in view.children:
                child.disabled = True
            await msg.edit(embed=em, view=view)

        view.on_timeout = timeout
        view.add_item(go_left)
        view.add_item(build_btn)
        view.add_item(go_right)
        build_btn.disabled = cards[page-1].color == Color.red()
        msg = await ctx.send(embed=cards[page-1], view=view)
        

    @commands.hybrid_command(aliases=[])
    @commands.cooldown(1, 100, type=commands.BucketType.user)
    @has_profile()
    async def trade(self, ctx, user: discord.Member, item, val: int = 1):
        """Placeholder simple trade: same as give, but both must confirm."""
        await ctx.send("Trade system is basic; use `k give` for direct transfers for now.")

    @commands.hybrid_command(aliases=["transfer"])
    @commands.cooldown(1, 30, type=commands.BucketType.user)
    @has_profile()
    async def give(self, ctx, user: discord.Member, item, amount: int = 1):
        """Transfers inventory item to other user."""
        profile = GameProfile(ctx.author.id)
        if not Profiles[str(user.id)]:
            await ctx.reply("Given user profile not found.")
            return
        if item.isdigit():
            amount = int(item)
            item = "cash"
        item = item.lower().replace(" ","_")
        if item not in DATA["id"]:
            await ctx.send("Invalid item.")
            return
        if amount <= 0 or amount > 100000:
            await ctx.send("Invalid amount.")
            return
        if not profile.inv_searcher(item, amount):
            await ctx.send("That item is not in your inventory in that amount.")
            return

        em = Embed(title="💳 Transfer 💱",description=f"Are you sure you want to give {user.mention} {item} x {amount}?",color=Color.gold(),)
        confirm_btn = Button(style=ButtonStyle.green, custom_id="confirm", label="✅")
        discard_btn = Button(style=ButtonStyle.secondary, custom_id="discard", label="❌")

        view = View(timeout=45)

        async def timeout():
            nonlocal em, view, msg
            em.color = Color.light_grey()
            for child in view.children:
                child.disabled = True
            await msg.edit(embed=em, view=view)

        view.on_timeout = timeout
        view.add_item(discard_btn)
        view.add_item(confirm_btn)

        async def on_confirm(inter: Interaction):
            if inter.user.id != ctx.author.id:
                return await inter.response.send_message("This is not your interaction.", ephemeral=True)
            nonlocal em, view, profile
            profile.inv_manager(item, -amount)
            profile2 = GameProfile(user.id)
            profile2.inv_manager(item, amount)
            em.description = f"{kemoji()} Successfully sent {DATA['id'][item]} {item} x {amount} to {user.mention}."
            view = None
            await inter.response.edit_message(embed=em, view=None)
            await ctx.send(f"{user.mention} You received a gift",embed=Embed(description=f"You have received an item from {ctx.author.mention}\n{DATA['id'][item]} {item} x {amount}",color=Color.green()))

        async def on_discard(inter: Interaction):
            if inter.user.id != ctx.author.id:
                return await inter.response.send_message("This is not your interaction.", ephemeral=True)
            nonlocal em, view
            em.description = "⚠️ You cancelled the transaction."
            view = None
            await inter.response.edit_message(embed=em, view=None)

        confirm_btn.callback = on_confirm
        discard_btn.callback = on_discard

        msg = await ctx.reply(embed=em, view=view)

    @commands.hybrid_command(aliases=[])
    @commands.cooldown(1, 20, type=commands.BucketType.user)
    @has_profile()
    async def use(self, ctx, item):
        """Uses the selected item from inventory."""
        item = item.lower().replace(" ", "_")
        profile = GameProfile(ctx.author.id)
        if not profile.inv_searcher(item, 1):
            return await ctx.send("You do not have that item.")
        
        await ctx.send("This command is yet to be made")

    # ========= SHOP / MARKET / BANK / QUESTS =========

    @commands.hybrid_command(aliases=[])
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @has_profile()
    async def shop(self, ctx):
        """Show basic shop items."""
        descrip = ""
        for item, price in DATA.get("shop", {}).items():
            descrip += f"{DATA['id'].get(item, item)} - {price} cash\n"
        if not descrip:
            descrip = "Shop is empty."
        await ctx.send(embed=Embed(title="Shop", description=descrip, color=Color.green()))

    @commands.hybrid_command(aliases=[])
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @has_profile()
    async def buy(self, ctx, item: Optional[str] = None, amount: int = 1):
        """Welcome to the Shop: Buy anything using cash or gems."""
        if not item:
            await ctx.send("Specify an item to buy.")
            return
        item = item.lower()
        if item not in DATA.get("shop", {}):
            await ctx.send("That item is not sold here.")
            return
        if amount <= 0:
            await ctx.send("Invalid amount.")
            return
        price = DATA["shop"][item] * amount
        if Profiles[str(ctx.author.id)]["assets"].get("cash", 0) < price:
            await ctx.send("You do not have enough cash.")
            return
        inv_manager(str(ctx.author.id), "cash", -price)
        inv_manager(str(ctx.author.id), item, amount)
        await ctx.send(f"You bought {DATA['id'].get(item, item)} x{amount} for {price} cash.")

    @commands.hybrid_command(aliases=[])
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @has_profile()
    async def sell(self, ctx, item: Optional[str] = None, amount: int = 1):
        """Welcome to the Shop: Sell anything for estimated cash value."""
        if not item:
            await ctx.send("Specify an item to sell.")
            return
        item = item.lower()
        if amount <= 0:
            await ctx.send("Invalid amount.")
            return
        if not inv_searcher(str(ctx.author.id), item, amount):
            await ctx.send("You do not have enough of that item.")
            return
        price = DATA.get("sell_price", {}).get(item, DATA.get("shop", {}).get(item, 10)) * amount
        inv_manager(str(ctx.author.id), item, -amount)
        inv_manager(str(ctx.author.id), "cash", price)
        await ctx.send(f"You sold {DATA['id'].get(item, item)} x{amount} for {price} cash.")

    @commands.hybrid_command(aliases=[])
    @commands.cooldown(1, 100, type=commands.BucketType.user)
    @has_profile()
    async def market(self, ctx):
        """Placeholder for global player market."""
        await ctx.send("Player market is not fully implemented yet.")

    @commands.hybrid_command(aliases=["rob"])
    @commands.cooldown(1, 3600, type=commands.BucketType.user)
    @has_profile()
    async def bankrob(self, ctx, user: discord.Member):
        """Attempts bank robbing someone's account based on your aura level."""
        robber_id = str(ctx.author.id)
        victim_id = str(user.id)
        if victim_id not in Profiles:
            await ctx.send("Target profile not found.")
            return
        robber_aura = Profiles[robber_id]["aura"]
        success_chance = max(5, min(70, 30 + robber_aura // 20))
        if randint(1, 100) > success_chance:
            fine = 200
            inv_manager(robber_id, "cash", -fine)
            await ctx.send(f"You failed the bank rob and paid {fine} cash in fines.")
            return
        stolen = min(Profiles[victim_id]["assets"].get("cash", 0) // 2, 5000)
        if stolen <= 0:
            await ctx.send("Victim has no money to steal.")
            return
        inv_manager(victim_id, "cash", -stolen)
        inv_manager(robber_id, "cash", stolen)
        await ctx.send(f"You robbed {stolen} cash from {user.mention}!")

    @commands.hybrid_command(aliases=[])
    @commands.cooldown(1, 3600, type=commands.BucketType.user)
    @has_profile()
    async def quest(self, ctx):
        """Complete quests to receive exciting rewards."""
        await ctx.send("Quest system coming soon: Daily, Adventure, Buried Treasure, Premium.")

    @commands.hybrid_command(aliases=[])
    @commands.cooldown(1, 86400, type=commands.BucketType.user)
    @has_profile()
    async def daily(self, ctx):
        """Claim daily reward."""
        reward = randint(100, 500)
        gems = choice([0,0,0,0,0,0,0,1])
        profile = GameProfile(ctx.author.id)
        profile.inv_manager("cash", reward)
        if not gems:
            await ctx.send(f"You claimed your daily reward of {reward} <:cash:1433171762668896388>.")
        else:
            await ctx.send(f"You claimed your daily reward of {reward} <:cash:1433171762668896388>.")
        
    # ========= BATTLE / KILL / MARRY =========

    @commands.hybrid_command(aliases=["b"])
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @has_profile()
    async def battle(self, ctx, user: Optional[discord.Member] = None):
        """Battle someone; show your strength and get rewards."""
        if user is None or user.bot:
            await ctx.send(embed=Embed(description="Random battle is not yet implemented. Mention a player.", color=Color.red()))
            return
        p1 = Profiles[str(ctx.author.id)]
        p2 = Profiles.get(str(user.id))
        if not p2:
            await ctx.send("Opponent does not have a profile.")
            return
        a1 = p1["aura"]
        a2 = p2["aura"]
        if randint(0, a1 + a2) < a2:
            await ctx.send(f"{user.mention} won the battle!")
        else:
            await ctx.send(f"{ctx.author.mention} won the battle!")

    @commands.hybrid_command(aliases=[])
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @has_profile()
    async def kill(self, ctx, mob: str):
        """To kill spawned mobs only."""
        if not Server_Settings[str(ctx.guild.id)]["spawn"] and mob.lower() in Server_Settings[str(ctx.guild.id)]["spawn"]:
            return await ctx.send(embed=Embed(description="There is no spawned mob or invalid mob given.", color=Color.red()))

        profile = Profiles[str(ctx.author.id)]
        aura = profile["aura"]
        loc = profile["location"]

        drops = {
            "Foods": 1,
            "Animals": 2,
            "Tools": 1,
            "Weapons": 0.5,
            "Vehicles": 0.2,
            "Emotes": 0.2,
        }

        rewards = self.reward_player(aura, loc, drops)
        self.add_rewards(ctx.author.id, rewards)
        em = Embed(
            title="Kill",
            description=f"You killed **{mob}** in the {loc.capitalize()} and got:\n{self.rewards_descrip(rewards)}",
            color=Color.green(),
        )
        em.set_footer(
            text=f"Kill by {ctx.author.display_name} | At {timestamp(ctx)}",
            icon_url=ctx.author.avatar,
        )
        await ctx.reply(embed=em)

    @commands.hybrid_command(aliases=[])
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    @has_profile()
    async def marry(self, ctx, spouse: discord.Member):
        """Marry someone special 😜💓"""
        profile = GameProfile(ctx.author.id)
        assets = profile.assets
        if assets.get("ring", 0) <= 0:
            await ctx.send("You need a ring in your inventory to marry someone 😉❤️")
            return
        em = Embed(
            title=f"🤵 {ctx.author.display_name} Weds {spouse.display_name} 👰",
            description=f"{ctx.author.display_name}, do you want to marry {spouse.mention}? Please confirm your decision.",
            color=Color.purple(),
        )
        em.set_footer(
            text=f"Marriage attended by {randint(1, 8192)} discordians | {timestamp(ctx)} | Aura++",
            icon_url=ctx.author.avatar,
        )

        confirm_btn = Button(style=ButtonStyle.green, custom_id="confirm", label="✅")
        discard_btn = Button(style=ButtonStyle.secondary, custom_id="discard", label="❌")

        view = View(timeout=45)

        async def timeout():
            nonlocal em, view, msg
            em.color = Color.light_grey()
            for child in view.children:
                child.disabled = True
            await msg.edit(embed=em, view=view)

        view.on_timeout = timeout
        view.add_item(confirm_btn)
        view.add_item(discard_btn)

        async def on_confirm(inter: Interaction):
            if inter.user.id != ctx.author.id:
                return await inter.response.send_message("This is not your interaction.", ephemeral=True)
            nonlocal em, view
            Profiles[str(ctx.author.id)]["spouse"] = spouse.id
            Profiles[str(spouse.id)]["spouse"] = ctx.author.id
            assets["ring"] -= 1
            Profiles[str(ctx.author.id)]["aura"] += 10
            em.description = f"💍 {ctx.author.mention} and {spouse.mention} are now married!"
            view.timeout = None
            await inter.response.edit_message(embed=em, view=None)

        async def on_discard(inter: Interaction):
            if inter.user.id != ctx.author.id:
                return await inter.response.send_message("This is not your interaction.", ephemeral=True)
            nonlocal em, view
            em.description = "You cancelled the marriage proposal."
            view.timeout = None
            await inter.response.edit_message(embed=em, view=None)

        confirm_btn.callback = on_confirm
        discard_btn.callback = on_discard
        msg = await ctx.send(embed=em, view=view)


async def setup(bot):
    await bot.add_cog(Games(bot))
    print("Loaded cogs: Games")
