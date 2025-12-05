import random
import discord
from discord.ext import commands
from __init__ import*

'''
default_profiles = {
    "name": "No name noob",
    "health": 100,
    "hunger": 100,
    "location": "home",
    "aura":0,
    "skills": {},
    "foods": {},
    "plants": {},
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
    "jobs": {}
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
        if inv[item] and inv[item] >= amt:
            Profiles[id][categ][item] -= amt
            if Profiles[id][categ][item] == 0:
                del Profiles[id][categ][item]
                
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
            Profiles[str(ctx.author.id)] = {"name": ctx.author.name, "health": 100,"hunger": 100, "location": "home", "aura":0, "skills": {}, "foods": {}, "plants": {}, "assets": {"cash": 100,"gem": 50,"orbs": 1}, "tools": {}, "weapons": {}, "vehicles": {}, "emotes": {}, "quests": {}, "places": {}, "jobs": {}}
            em = Embed(title="Profile Created Successfully", description=f"{ctx.author.mention} your profile created successfully. Start playing eith game commands now: `hunt`, `chop`, `adv`, `mine`, `work`, `school`, `craft`, `use`, `eat` .., .\n:white_check_mark: You obatained bonous ₹100 cash 💵\n:white_check_mark: You obtained 50 gem 💎 and 1 Dark Magic Orb 🔮\nUse `k help games` to get more help and info.",color=Color.green())
            em.set_footer(text=f"{ctx.author.name} created acc at {timestamp(ctx)}", icon_url= ctx.author.avatar)
            await ctx.send(embed = em)
        else:
            emoji = EMOJI[f"kelly{choice(['annoyed', 'laugh', 'gigle', 'waiting', 'idontcare', 'chips', 'bweh', 'bweh'])}"]
            await msg.reply(f"**{emoji} | ** you dont even do a single thing properly disgusting!! Dont ever come to me again")
        
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
        del Profile[id]["skills"][skill]
    
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
    if Profiles[id]["places"][place]:
        Profiles[id]["places"][place] += randint(1,10)
        if Profiles[id]["places"][place] > 100:
            Profiles[id]["places"][place] = 100
    else:
        Profiles[id]["places"][place] = 100
        await ctx.send(f"{ctx.author.mention} you found a new location: ft. {place.replace('_','').title()}")
