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
    "eatables": {},
    "plants": {},
    "animals": {},
    "minerals": {},
    "builds": {},
    "assets": {
        "cash": 100,
        "gem": 50,
        "orb": 1
    },
    "tools": {},
    "weapons": {},
    "vehicles": {},
    "quests": {},
    "places": {},
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
        profile.skills_manager(subject, gain)
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
        place = task["place"]
        profile.location = place
        rewards = profile.reward_player(task["drops"])  
        em = Embed(title="Explore",description=f"You explored around {place.capitalize()} and got:\n{rewards}",color=Color.green())  
        try:
            msg = await channel.fetch_message(task["message"])
            profile.place_manager(place)
            em.set_footer(text=f"Explore by {ctx.author.display_name} | At {timestamp(ctx)}",icon_url=ctx.author.avatar)  
        except:
            profile.places[place] = min((profile.place.get(place, 0) + randint(1,6)), 100)
        await channel.send(f"<@{uid}> Exploration Finished: You found a {place}! You can adventure here now using `k adventure`.", embed=em)
        
    else:
        rewards = profile.reward_player(task["rewards"])
        em = Embed(title=f"{task['name']} Finished ❕", description= f"Ayoo user you finished your task and you recieved:\n{rewards}", color = Color.green())
        em.set_footer(text = f"{task['name'].title()} - ▓▓▓▓▓▓▓▓▓▓100% Completed")
        await channel.send(f"<@{uid}>", embed= em)
    profile.activity = "sleeping"
    
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
        to_run = [ (due, task) for due, task in profile["tasks"].items() if datetime.now() > datetime.fromisoformat(due) ]
        for due, task in to_run:
            await perform_task(task, id, client)
            del profile["tasks"][due]
    
async def run_all_reminders(client):
    """Runs all reminders from all user that hit the limit. Reminders are usually for very long tasks.
    Reminders includes - quests, marriage wishes, tips, build, etc"""
    for id, profile in Profiles.items():
        to_run = [ (due, reminder) for due, reminder in profile["reminder"].items() if datetime.now() > datetime.fromisoformat(due) ]
        for due, reminder in to_run:
            await perform_reminder(reminder, id, client)
            del profile["reminder"][due]
    
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
            Profiles[str(ctx.author.id)] = {"name": ctx.author.name, "activity": "sleeping", "health": 100,"hunger": 100, "location": "home", "aura":0, "skills": {}, "eatables": {}, "plants": {}, "animals": {}, "assets": {"cash": 100,"gem": 50,"orb": 1}, "builds": {}, "tools": {}, "weapons": {}, "vehicles": {}, "minerals": {}, "quests": {}, "places": {}, "tasks": {}, "reminders": {}}
            em = Embed(title="Profile Created Successfully", description=f"{ctx.author.mention} your profile created successfully. Start playing eith game commands now: `hunt`, `chop`, `adv`, `mine`, `work`, `school`, `craft`, `use`, `eat` ...\n:white_check_mark: You obatained bonous ₹100 cash {GAME['id']['cash']['emoji']}\n:white_check_mark: You obtained 50 gems {GAME['id']['gem']['emoji']} and 1 Dark Magic Orb {GAME['id']['orb']['emoji']}\nUse `k games` to get more help and info.",color=Color.green())
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
        if not Profiles.get(uid) or not Profiles[uid].get("activity"):
            return True

        activity = Profiles[uid]["activity"]
        tasks_dict = Profiles[uid].get("tasks", {})

        # Find the current task
        task = None
        duration_iso = None
        for due, t in tasks_dict.items():
            if t["name"] == activity:
                task = t
                duration_iso = due
                break
        else:
            return True

        remaining = datetime.fromisoformat(duration_iso) - datetime.now()
        remaining_seconds = max(0, remaining.total_seconds())

        # Initialize embed
        def get_embed():
            minutes, seconds = divmod(remaining_seconds, 60)
            percentage_completed = min(100, max(int((task["duration"] - remaining_seconds) / task["duration"] * 100), 0))
            blocks = int(percentage_completed // 10)
            percentage_bar = "▓" * blocks + "░" * (10 - blocks)

            titles = {
                "sleeping": "Currently Sleeping",
                "working": "Currently Busy Working",
                "studying": "Currently Studying",
                "travelling": "Currently Traveling",
                "exploring": "Currently Out Exploring"
            }
            desc = {
                "sleeping": "You are resting. You can perform commands.",
                "working": f"Ayoo user you are currently **Working**. Wait until office hours end.\nTime Remaining: {minutes:.0f}:{seconds:02.0f}",
                "studying": f"Ayoo user you are currently **Studying**. Wait until classes finish.\nTime Remaining: {minutes:.0f}:{seconds:02.0f}",
                "travelling": f"Ayoo user you are currently **Travelling**. Wait until you reach your destination.\nTime Remaining: {minutes:.0f}:{seconds:02.0f}",
                "exploring": f"Ayoo user you are currently **Exploring**. Wait until finished to claim rewards.\nTime Remaining: {minutes:.0f}:{seconds:02.0f}"
            }

            em = Embed(title=titles.get(activity, "Busy"), description=desc.get(activity, ""), color=Color.orange())
            em.set_footer(text=f"{task['name'].title()} - {percentage_bar} {percentage_completed}% Completed")
            return em

        if activity == "sleeping":
            return True

        # Create view with cancel button
        view = View(timeout=None)
        cancel = Button(label="✖️ Cancel", custom_id=activity, style=ButtonStyle.secondary)

        async def on_cancel(inter: Interaction):
            if inter.user.id != ctx.author.id:
                await inter.response.send_message(embed=Embed(description="This interaction is not for you", color=Color.red()), ephemeral=True)
                return

            cancel.disabled = True
            cancel.label = "🚫 Cancelled"
            view.timeout = 1  # stops the update loop

            # Remove task
            for due, t in list(Profiles[uid]["tasks"].items()):
                if t["name"] == inter.data["custom_id"]:
                    del Profiles[uid]["tasks"][due]
                    Profiles[uid]["activity"] = "sleeping"
                    Profiles[uid]["location"] = "home"

            await inter.response.edit_message(embed=get_embed(), view=view)

        cancel.callback = on_cancel
        view.add_item(cancel)

        # Send initial message
        msg = await ctx.reply(embed=get_embed(), view=view)

        # Update loop every 1 seconds for 10 sec max
        sec_count = 0
        while remaining_seconds > 0 and not cancel.disabled:
            await asyncio.sleep(1)
            remaining = datetime.fromisoformat(duration_iso) - datetime.now()
            remaining_seconds = max(0, remaining.total_seconds())
            await msg.edit(embed=get_embed())
            sec_count += 1
            if sec_count > 10:
                return False

        return False

    return commands.check(predicate)
    
def has_in_inventory(item, value = 0):
    async def predicate(ctx):
        if not Profiles[str(ctx.author.id)]:
            return
        profile = GameProfile(ctx.author.id)
        if profile.inv_searcher(item, value):
            return True 
        em = Embed(description=f"Ayoo You must need `{GAME['id'][item]['emoji']} {item.title()}` in your inventory to perform this.", color= Color.gold())
        emoji = GAME["id"][item]["emoji"]
        if emoji.startswith("<a"):
            em.set_thumbnail(url=f"https://cdn.discordapp.com/emojis/{emoji.split(':')[1]}.gif")
        elif emoji.startswith("<"):
            em.set_thumbnail(url=f"https://cdn.discordapp.com/emojis/{emoji.split(':')[1]}.png")
        else:
            em.set_thumbnail(url="https://twemoji.maxcdn.com/v/latest/72x72/" + "-".join(f"{ord(c):x}" for c in emoji) + ".png")
        await ctx.send(embed=em)
        return False
    return commands.check(predicate)
    
def at_the_location(loc):
    async def predicate(ctx):
        uid = str(ctx.author.id)
        if not Profiles[uid]:
            return
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

    def get(self, name, default=None):
        if name in self._data:
            return self._data[name]
        return default
        
    def inv_searcher(self, item, amt):
        category = ("eatables", "assets", "plants", "animals", "vehicles", "minerals", "weapons", "tools", "builds")
        for categ in category:
            inv = self._data[categ]
            if item in inv and inv[item] >= amt:
                return True
        return False 

    def inv_manager(self, item, amt):
        category = ("eatables", "assets", "plants", "animals", "vehicles", "minerals", "weapons", "tools", "builds")
        for categ in category:
            if item in GAME[categ]:
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
        self.skills[skill] = skills.get(skill, 0) + percentage
        if skills[skill] > 100:
            self.skills[skill] = 100
        elif skills[skill] <= 0:
            del self.skills[skill]
            
    def location_searcher(self, location):
        loc = self.location
        if loc == location:
            return True
        return False

    def place_manager(self, place):
        places = self.places
        if place in places:
            self.places[place] += randint(1, 6)
        else:
            self.places[place] = randint(1,6)
            
        if places[place] > 100:
            self.places[place] = 100
    
    def add_task(self, name, duration, channel, message, **info):
        due = datetime.now() + timedelta(seconds=duration)
        due_str = due.isoformat()
        self.tasks[due_str] = {"name": name, "duration": duration, "channel": channel, "message": message, **info}

    def add_reminder(self, name, duration, channel, message, **info):
        due = datetime.now() + timedelta(seconds=duration)
        due_str = due.isoformat()
        self.reminders[due_str] = {"name": name, "duration": duration, "channel": channel, "message": message, **info}

    def add_rewards(self, rewards):
        for item, qty in rewards:
            self.inv_manager(item, qty)

    def reward_player(self, drops, count_range=(3, 7)):
        """Rewards players with drops and count range, rewards based on user location and aura.
        Adds Rewards to player inventory and return the reward description"""
        rewards = []
        aura = self.aura
        location = self.location
        
        # weights per aura-band -> level keys
        levels_choice = {
            200: {1: 0.6, 2: 0.25, 3: 0.10, 4: 0.04, 5: 0.01},
            400: {1: 0.4, 2: 0.4, 3: 0.14, 4: 0.04, 5: 0.02},
            600: {1: 0.2, 2: 0.2, 3: 0.4, 4: 0.12, 5: 0.08},
            800: {1: 0.1, 2: 0.1, 3: 0.2, 4: 0.4, 5: 0.2},
            1000: {1: 0.05, 2: 0.05, 3: 0.1, 4: 0.3, 5: 0.5},
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

            category_obtainables = [item for item in GAME[category] if "places" in GAME["id"][item] and location in GAME["id"][item]["places"] ]

            while level > 0:
                available = [item for item in category_obtainables if level == GAME["id"][item]["level"] ]
                if not available:
                    level -= 1
                    continue
                else:
                    item_key = choice(available)
                    qty = randint(1, 3)
                    if aura > 999:
                        qty = randint(3, 5)
                    rewards.append((item_key, qty))
                    break
        self.add_rewards(rewards)
        return rewards_descrip(rewards)
