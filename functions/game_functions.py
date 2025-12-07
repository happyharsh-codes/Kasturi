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


async def perform_task(task, uid, client):
    
    if task["name"] == "studying":
        em = Embed(title="Currently Studying", description= f"Ayoo user you are currently studying", color = Color.orange())
        em.set_footer(text = f"{task['name'].title()} - {remaining//task['duration']}% Completed")
        channel = client.get_channel(task["channel"])
    
    if not channel:
        try:
            channel = await client.fetch_channel(task["channel"])
        except:
            return -1
    await channel.send(embed= em, view= view)

async def perform_reminder(reminder, uid, client):
    
    if task["name"] == "studying":
        em = Embed(title="Currently Studying", description= f"Ayoo user you are currently studying", color = Color.orange())
        em.set_footer(text = f"{task['name'].title()} - {remaining//task['duration']}% Completed")
        channel = client.get_channel(task["channel"])
    
    if not channel:
        try:
            channel = await client.fetch_channel(task["channel"])
        except:
            return -1
    await channel.send(embed= em, view= view)
    
async def run_all_tasks(client):
    """Runs all the task from all users that hit the time limit
    includes task like - travel, working, studying, crafting, exploring, mining, mob spawn."""
    for id, profile in Profiles.items():
        if profile["tasks"]:
            for due, task in profile["tasks"]:
                if datetime.now() > datetime.fromisoformat(due):
                    await perform_task(task, id, client)

async def run_all_reminders(client):
    """Runs all reminders from all user that hit the limit. Reminders are usually for very long tasks.
    Reminders includes - quests, marriage wishes, tips, build, etc"""
    for id, profile in Profiles.items():
        if profile["reminders"]:
            for due, reminder in profile["reminders"]:
                if datetime.now() > datetime.fromisoformat(due):
                    await perform_reminder(reminder, id, client)

    
def inv_searcher(id, item, amt):
    category= ["foods", "tools", "assets", "plants", "animals", "vehicles", "weapons", "emotes"]
    for categ in category:
        inv = Profiles[id][categ]
        if inv[item] and inv[item] >= amt:
            return True
    return False 
    
def inv_manager(id, item, amt):
    category= ["foods", "tools", "assets", "plants", "animals", "vehicles", "weapons", "emotes"]
    for categ in category:
        inv = Profiles[id][categ]
        if inv[item]:
            Profiles[id][categ][item] += amt
            if Profiles[id][categ][item] == 0:
                del Profiles[id][categ][item]
        else:
            Profiles[id][categ][item] = amt
                
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
        
        return False
    return commands.check(predicate)

def not_busy()
    async def predicate(ctx):
        uid = str(ctx.author.id)
        activity = Profiles[uid]["activity"]
        tasks = Profiles[uid]["tasks"]
        for due, t in tasks.items():
            if t["name"] == activity:
                task = t
                duration = due
                break
        else:
            return True
        remaining = datetime.now() - datetime.fromisoformat(duration)
        remaining_seconds = remaining.total_seconds()
        minutes, seconds = divmod(remaining_seconds, 60)
        percentage_completed = (remaining_seconds//task["duration"])*100
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
        em.set_footer(text = f"{task['name'].title()} - {percentage_completed}% Completed")
        
        view = View(timeout=45)
        async timeout():
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
        if inv_searcher(str(ctx.author.id), item, value):
            return True 
        await ctx.send(embed=Embed(description=f"Ayoo You must need `{item.title()}` in your inventory to perform this."), color= Color.gold())
        return False
    return commands.check(predicate)
    
def at_the_location(loc):
    async def predicate(ctx):
        if Profiles[str(ctx.author.id)]["location"] == loc:
            return True
        await ctx.reply(f"You must be at `{loc.title()}` to run this command")
        return False
    return commands.check(predicate)

def skills_searcher(ctx, skill, percentage):
    skills = Profiles[str(id)]["skills"]
    if skill in skills and skills[skill] >= percentage:
        return True
    return False

def skills_manager(id: str, skill, percentage):
    skills = Profiles[id]["skills"]
    if skill in skills:
        Profiles[id]["skills"][skill] += percentage
    else:
        Profile[id]["skills"][skill] = percentage
    if Profile[id]["skills"][skill] > 100:
        Profile[id]["skills"][skill] = 100
    elif Profile[id]["skills"][skill] <= 0:
        del Profile[id][
        "skills"][skill]
    
def skills_searcher(ctx, skill, percentage):
    skills = Profiles[str(id)]["skills"]
    if skills[skill] and skills[skill] >= percentage:
        return True
    return False

def skills_manager(id: str, skill, percentage):
    skills = Profiles[id]["skills"]
    if skills[skill]:
        Profiles[id]["skills"][skill] += percentage
    else:
        Profile[id]["skills"][skill] = percentage
    if Profile[id]["skills"][skill] > 100:
        Profile[id]["skills"][skill] = 100
    elif Profile[id]["skills"][skill] <= 0:
        del Profile[id]["skills"][skill]
    
def location_searcher(id, location):
    loc = Profiles[id]["loc"]
    if loc == location:
        return True
    return False

async def place_manager(ctx, place):
    id = str(ctx.author.id)
    if Profiles[id]["places"][place]:
        Profiles[id]["places"][place] += randint(1,10)
        if Profiles[id]["places"][place] > 100:
            Profiles[id]["places"][place] = 100
    else:
        Profiles[id]["places"][place] = 100
        await ctx.send(f"{ctx.author.mention} you found a new location: ft. {place.replace('_','').title()}")
