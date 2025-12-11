import random
import discord
from discord.ext import commands
from __init__ import*

'''
default_profiles = {
    "name": "No name noob",
    "activity": "sleeping",
    "health": 100,
    "hunger": 100,
    "location": "home",
    "aura":0,
    "skills": {},
    "foods": {},
    "plants": {},
    "animals": {},
    "assets": {
        "cash": 100,
        "gem": 50,
        "orbs": 1
    },
    "tools": {},
    "weapons": {},
    "vehicles": {},
    "quests": {},
    "places": {},
    "jobs": {},
    "tasks": {},
    "reminders": {}
}
'''

import random

def weighted_choice(choices: list):
    if not choices:
        raise ValueError("choices list cannot be empty")
    
    total = sum(w for _, w in choices)
    if total <= 0:
        return random.choice([item for item, w in choices])
    
    r = random.random() * total
    upto = 0
    for item, w in choices:
        if upto + w >= r:
            return item
        upto += w
    return choices[-1][0]

def rewards_descrip(rewards):
    level1 = "<:common:> "
    level2 = "<:unique:> "
    level3 = "<:rare:> "
    level4 = "<:epic:> "
    level5 = "<:legendary:> "
    random.shuffle(rewards)
    for category, item_key, qty, level in rewards:
        emoji = DATA["id"].get(item_key, "")
        if level == "Level1":
            level1 += emoji * qty
        elif level == "Level2":
            level2 += emoji * qty
        elif level == "Level3":
            level3 += emoji * qty
        elif level == "Level4":
            level4 += emoji * qty
        elif level == "Level5":
            level5 += emoji * qty

    description = ""
    if level1 != "<:common:> ":
        description += f"{level1}\n"
    if level2 != "<:unique:> ":
        description += f"{level2}\n"
    if level3 != "<:rare:> ":
        description += f"{level3}\n"
    if level4 != "<:epic:> ":
        description += f"{level4}\n"
    if level5 != "<:legendary:> ":
        description += f"{level5}"
    return description.strip()

async def perform_task(task, uid, client):
    profile = GameProfile(uid)
    profile.activity = "sleeping"
    channel = client.get_channel(task["channel"])
    if not channel:
        try:
            channel = await client.fetch_channel(task["channel"])
        except:
            return -1
    if task["name"] == "working":
        sal = task["salary"]
        profession = task["profession"]
        profile.inv_manager("cash", sal)
        em = Embed(title= f"Work Finished", description = f"You fished your work today. Great work at job. \n**Salary Recived:** {sal}", color = Color.green())
        em.set_footer(text= f"Salary transferred to your bank account")
        await channel.send(f"<@{uid}>", embed= em)
        
    elif task["name"] == "studying":
        subject = task["subject"]
        gain = randint(1, 5)
        profile.skills_manager(str(ctx.author.id), selected.value, gain)
        progress = profile.skills.get(subject, 0)
        em = Embed(title = f"{subject.title()} Class Completed", description= f"You studied {subject} {task['emoji']} and gained {gain}%. Progress: {progress}%.", color = Color.green())
        em.set_footer(text= f"Class ▓▓▓▓▓▓▓▓▓▓100% Completed | Skill++")
        await channel.send(f"<@{uid}>", embed= em)

    elif task["name"] == "travelling":
        await channel.send(f"<@{uid}> You have reached {task['destination'].title()}")
        profile.location = task["destination"]

    elif task["name"] == "crafting":
        item = task["item"]
        amt = task["amount"]
        profile.inv_manager(item, amt)
        await channel.send(f"<@{uid}> You have crafted {DATA['id'][item]} {item} x {amt} successfully")

    elif task["name"] == "exploring":
        place = task["destination"]
        profile.location = place
        rewards = profile.reward_player(task["drops"])  
        em = Embed(title="Explore",description=f"You explored around {new_loc.capitalize()} and got:\n{rewards}",color=Color.green())  
        try:
            msg = await channel.fetch_message(task["message"])
            ctx = client.get_context(msg)
            await profile.place_manager(ctx, place)
            em.set_footer(text=f"Explore by {ctx.author.display_name} | At {timestamp(ctx)}",icon_url=ctx.author.avatar)  
        except:
            profile.places[place] = min(profile.place.get(place, 0) + randint(1,6), 100)
        await channel.send(f"<@{uid}> Exploration Finished: You found a {place}! You can adventure here now using `k adventure`", embed=em)
        
    else:
        rewards = reward_player(profile["aura"], profile["location"], task["rewards"])
        em = Embed(title=f"{task['name']} Finished ❕", description= f"Ayoo user you finished your task and you recieved:\n{rewards}", color = Color.green())
        em.set_footer(text = f"{task['name'].title()} - ▓▓▓▓▓▓▓▓▓▓100% Completed")
        await channel.send(f"<@{uid}>", embed= em)
        
async def perform_reminder(reminder, uid, client):
    channel = client.get_channel(reminder["channel"])
    if not channel:
        try:
            channel = await client.fetch_channel(reminder["channel"])
        except:
            return -1

    em = Embed(title="", description= "", color= Color.green())
    await channel.send(embed= em)
    
async def run_all_tasks(client):
    """Runs all the task from all users that hit the time limit
    includes task like - travel, working, studying, crafting, exploring, mining, mob spawn."""
    for id, profile in Profiles.items():
        if profile["tasks"]:
            for due, task in profile["tasks"].items():
                if datetime.now() > datetime.fromisoformat(due):
                    await perform_task(task, id, client)

async def run_all_reminders(client):
    """Runs all reminders from all user that hit the limit. Reminders are usually for very long tasks.
    Reminders includes - quests, marriage wishes, tips, build, etc"""
    for id, profile in Profiles.items():
        if profile["reminders"]:
            for due, reminder in profile["reminders"].items():
                if datetime.now() > datetime.fromisoformat(due):
                    await perform_reminder(reminder, id, client)

def has_profile():
    async def predicate(ctx):
        if Profiles[str(ctx.author.id)]:
            Profiles[str(ctx.author.id)]["aura"] += 2
            return True
        code = choice(['i will work under kelly',"i will obey kelly from now on", "i will always bow down to kelly"])
        emoji = EMOJI[f"kelly{choice(['blush', 'thinking', 'laugh', 'gigle', 'waiting', 'idontcare'])}"]
        await ctx.reply(f"**{emoji} | ** you dont even have a profile\n**{choice(['📃','📜','📄','📑','📰','🗞','📚','📙','📕','📖','📗','📘','✒','✏','🖋','📝','📋'])} | **Type this to create new profile `{code}`")
        try:
            msg = await ctx.bot.wait_for("message", check= lambda x: x.author.id == ctx.author.id, timeout= 120)
        except asyncio.TimeoutError:
            return False 
        if msg.content.lower() == code:
            Profiles[str(ctx.author.id)] = {"name": ctx.author.name, "activity": "sleeping", "health": 100,"hunger": 100, "location": "home", "aura":0, "skills": {}, "foods": {}, "plants": {}, "animals": {}, "assets": {"cash": 100,"gem": 50,"orbs": 1}, "tools": {}, "weapons": {}, "vehicles": {}, "emotes": {}, "quests": {}, "places": {}, "jobs": {}, "tasks": {}, "reminders": {}}
            em = Embed(title="Profile Created Successfully", description=f"{ctx.author.mention} your profile created successfully. Start playing eith game commands now: `hunt`, `chop`, `adv`, `mine`, `work`, `school`, `craft`, `use`, `eat` .., .\n:white_check_mark: You obatained bonous ₹100 cash 💵\n:white_check_mark: You obtained 50 gem 💎 and 1 Dark Magic Orb 🔮\nUse `k help games` to get more help and info.",color=Color.green())
            em.set_footer(text=f"{ctx.author.name} created acc at {timestamp(ctx)}", icon_url= ctx.author.avatar)
            await ctx.send(embed = em)
        else:
            emoji = EMOJI[f"kelly{choice(['annoyed', 'laugh', 'gigle', 'waiting', 'idontcare', 'chips', 'bweh', 'bweh'])}"]
            await msg.reply(f"**{emoji} | ** you dont even do a single thing properly disgusting!! Dont ever come to me again")
        
        raise commands.CheckFailure("New Profile Created")
    return commands.check(predicate)

def not_busy():
    async def predicate(ctx):
        uid = str(ctx.author.id)
        if not Profiles[uid]:
            raise commands.CheckFailure("Profile does not exist")
        activity = Profiles[uid]["activity"]
        tasks = Profiles[uid]["tasks"]
        for due, t in tasks.items():
            if t["name"] == activity:
                task = t
                duration = due
                break
        else:
            return True
        remaining = datetime.fromisoformat(duration) - datetime.now()
        remaining_seconds = remaining.total_seconds()
        minutes, seconds = divmod(remaining_seconds, 60)
        percentage_completed = min(100, max((remaining_seconds//task["duration"])*100, 0))
        percentage_bar = "▓" * (percentage_completed//10) + "░" * (10 - (percentage_completed//10))
        if activity == "sleeping":
            return True 
        elif activity == "working":
            em = Embed(title="Currently Busy Working", description= f"Ayoo user you are currently **Working**. You cant perform that command now. Wait until your office hour ends to claim the Rewards.\n**Time Remaining**: {minutes:.0f}:{seconds:02.0f}", color = Color.orange())
        elif activity == "studying":
            em = Embed(title="Currently Studying", description= f"Ayoo user you are currently **Studying**. You cant perform that command now. Wait until you finish classes to claim the Rewards.\n**Time Remaining**: {minutes:.0f}:{seconds:02.0f}", color = Color.orange())
        elif activity == "travelling":
            em = Embed(title="Currently Traveling", description= f"Ayoo user you are currently **Travelling**. You cant perform that command now. Wait until you reach the destination .\n**Time Remaining**: {minutes:.0f}:{seconds:02.0f}", color = Color.orange())
        elif activity == "exploring":
            em = Embed(title="Currently Out Exploring", description= f"Ayoo user you are currently **Exploring**. You cant perform that command now. Wait until you finish to claim the Rewards.\n**Time Remaining**: {minutes:.0f}:{seconds:02.0f}", color = Color.orange())
        em.set_footer(text = f"{task['name'].title()} - {percentage_bar}{percentage_completed}% Completed")
        
        view = View(timeout=45)
        async def timeout():
            nonlocal em, view, msg
            em.color = Color.light_grey()
            for children in view.children:
                children.disabled = True
            await msg.edit(embed=em, view=view)
        view.on_timeout = timeout

        cancel = Button(label="✖️ Cancel", custom_id = activity, style = ButtonStyle.secondary)
        async def on_cancel(inter: Interaction):
            if inter.user.id != ctx.author.id:
                await inter.response.send_message(embed=Embed(description="This interaction is not for you", color=Color.red()),ephemeral=True)
                return
            nonlocal view, cancel 
            cancel.disabled = True
            cancel.label = "🚫 Cancelled"
            view.timeout = None
            for due, task in Profiles[uid]["tasks"].items():
                if task["name"] == inter.data["custom_id"]:
                    del Profiles[uid]["tasks"][due]
                    Profiles[uid]["activity"] = "sleeping"
                    Profiles[uid]["location"] = "home"
            await inter.response.edit_message(embed=em, view= view)
        cancel.callback = on_cancel
        view.add_item(cancel)
        msg = await ctx.reply(embed=em, view= view)
        return False
    return commands.check(predicate)
    
def has_in_inventory(item, value = 0):
    async def predicate(ctx):
        profile = GameProfile(ctx.author.id)
        if profile.inv_searcher(item, value):
            return True 
        await ctx.send(embed=Embed(description=f"Ayoo You must need `{item.title()}` in your inventory to perform this."), color= Color.gold())
        return False
    return commands.check(predicate)
    
def at_the_location(loc):
    async def predicate(ctx):
        uid = str(ctx.author.id)
        if not Profiles[uid]:
            raise commands.CheckFailure("Profile does not exist")
        
        if Profiles[str(ctx.author.id)]["location"] == loc:
            return True
        await ctx.reply(f"You must be at `{loc.title()}` to run this command")
        return False
    return commands.check(predicate)

class GameProfile:

    def __init__(self, uid):
        self.uid = str(uid)
        self.__fetch_data__()
    
    def __fetch_data__(self):
        if self.uid in Profiles:
            self._data = Profiles[self.uid]
        else:
            raise ValueError(f"Profile UID {self.uid} not found in global Profiles dictionary.")

    def __setattr__(self, name, value):
        if name in ('uid', '_data'):
            object.__setattr__(self, name, value)
        else:
            self._data[name] = value
            
    def __getattr__(self, name):
        if name in self._data:
            return self._data[name]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
        
    def inv_searcher(self, item, amt):
        category = ["foods", "tools", "assets", "plants", "animals", "vehicles", "weapons", "emotes"]
        for categ in category:
            inv = self._data[categ]
            if item in inv and inv[item] >= amt:
                return True
        return False 

    def inv_manager(self, item, amt):
        category = ("foods", "tools", "assets", "plants", "animals", "vehicles", "weapons", "emotes")
        for categ in category:
            if item in DATA[categ]:
                category = categ
                break    
        inv = self._data[category]
        if item in inv or amt > 0:
            inv[item] = inv.get(item, 0) + amt
            if inv[item] <= 0:
                del inv[item]
                
    def skills_searcher(self, skill, percentage):
        skills = self.skills
        if skill in skills and skills[skill] >= percentage:
            return True
        return False

    def skills_manager(self, skill, percentage):
        skills = self.skills
        skills[skill] = skills.get(skill, 0) + percentage
        if skills[skill] > 100:
            skills[skill] = 100
        elif skills[skill] <= 0:
            del skills[skill]
            
    def location_searcher(self, location):
        loc = self.location
        if loc == location:
            return True
        return False

    async def place_manager(self, ctx, place):
        places = self.places
        if place in places:
            places[place] += randint(1, 6)
        else:
            places[place] = randint(1,6)
            await ctx.send(f"{ctx.author.mention} you found a new location: ft. **{place.replace('_','').title()}**")
        
        if places[place] > 100:
            places[place] = 100
    
    def add_task(self, name, duration, channel, message, **info):
        due = datetime.now() + timedelta(seconds=duration)
        due_str = due.isoformat()
        self.tasks[due_str] = {"name": name, "duration": duration, "channel": channel, "message": message, **info}

    def add_reminder(self, name, duration, channel, message, **info):
        due = datetime.now() + timedelta(seconds=duration)
        due_str = due.isoformat()
        self.reminders[due_str] = {"name": name, "duration": duration, "channel": channel, "message": message, **info}

    def add_rewards(self, rewards):
        for category, item, qty, level in rewards:
            self.inv_manager(item, qty)

    def reward_player(self, drops, count_range=(3, 7)):
        """Rewards players with drops and count range, rewards based on user location and aura.
        Adds Rewards to player inventory and return the reward description"""
        rewards = []
        aura = self.aura
        location= self.location
        # weights per aura-band -> level keys
        levels_choice = {
            200: {"Level1": 0.6, "Level2": 0.25, "Level3": 0.10, "Level4": 0.04, "Level5": 0.01},
            400: {"Level1": 0.4, "Level2": 0.4, "Level3": 0.14, "Level4": 0.04, "Level5": 0.02},
            600: {"Level1": 0.2, "Level2": 0.2, "Level3": 0.4, "Level4": 0.12, "Level5": 0.08},
            800: {"Level1": 0.1, "Level2": 0.1, "Level3": 0.2, "Level4": 0.4, "Level5": 0.2},
            1000: {"Level1": 0.05, "Level2": 0.05, "Level3": 0.1, "Level4": 0.3, "Level5": 0.5},
        }
        # count tweak for super-aura
        if aura > 999:
            count_range = (5, 8)

        # expand category weights into a list used by weighted_choice helper
        # expected signature: weighted_choice(list_of_(value, weight))
        cat_weight_list = list(drops.items())

        # decide which aura band to use
        def aura_band(a):
            if a <= 200:
                return 200
            elif a <= 400:
                return 400
            elif a <= 600:
                return 600
            elif a <= 800:
                return 800
            return 1000

        band = aura_band(aura)
        level_weight_list = list(levels_choice[band].items())

        for _ in range(randint(*count_range)):
            category = weighted_choice(cat_weight_list)
            level = weighted_choice(level_weight_list)

            # DATA["places"][location][category][level] is list of item-keys
            if location not in DATA["places"]:
                continue
            if category not in DATA["places"][location]:
                continue
            if level not in DATA["places"][location][category]:
                continue

            available = DATA["places"][location][category][level]
            if not available:
                continue

            item_key = choice(available)
            qty = randint(1, 3)
            if aura > 999:
                qty = randint(3, 5)

            rewards.append((category, item_key, qty, level))
        self.add_rewards(rewards)
        return rewards_descrip(rewards)
