import os
import sys
import re
import time
import math
import asyncio
import requests
import builtins
import traceback
import flask
import threading
import typing
import http.server
from datetime import datetime, UTC, timedelta, timezone
from json import load, dump, loads
from random import choice, randint, choices

import discord
from discord.ext import commands, tasks
from discord.ui import View, Button, Select, TextInput
from discord import Guild, Interaction, ButtonStyle, Embed, Color, SelectOption, TextStyle

from openai import OpenAI
from huggingface_hub import InferenceClient
import instaloader
from apify_client import ApifyClient

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import yt_dlp
import sclib
from lyricsgenius import Genius

import pytz
from pymongo import MongoClient
from collections.abc import MutableMapping

from dotenv import load_dotenv
load_dotenv()

with open("assets/info.json", "r") as f:
    DATA = load(f)
    EMOJI = DATA.get("emoji")
    EMOJI2 = DATA.get("emoji2")
    TIP = DATA.get("tips")
        
# ===== Setting Mongo Db ====

class MongoNestedDict(MutableMapping):
    def __init__(self, collection, doc_id, data=None, root=None, default=None):
        self.collection = collection
        self.doc_id = doc_id
        self.root = root if root else self
        self._data = data if data is not None else {}
        self.default = default

    # ---------- Sync database ----------
    def _sync(self):
        if self.root is self:  # only root writes
            self.collection.update_one(
                {"_id": self.doc_id},
                {"$set": {"data": self._data}},
                upsert=True
            )

    # ---------- Get ----------
    def __getitem__(self, key):
        if key not in self._data:
            return self.default
        value = self._data[key]

        if isinstance(value, dict):
            return MongoNestedDict(
                collection=self.collection,
                doc_id=self.doc_id,
                data=value,
                root=self.root
            )
        return value

    # ---------- Set ----------
    def __setitem__(self, key, value):
        if isinstance(value, dict):
            value = dict(value)
        self._data[key] = value
        self._sync()

    # ---------- Delete ----------
    def __delitem__(self, key):
        if key not in self._data:
            return
        del self._data[key]
        self._sync()

    # ---------- Required mapping methods ----------
    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return repr(self._data)
          
mongo = MongoClient(os.getenv("MONGO_URI"))
db = mongo["KellyBotDB"]

def load_mongo_dict(name, part="server", default=None):
    col = db[part]
    doc = col.find_one({"_id": name})

    if doc:
        print(f"Loaded: {name}")
        return MongoNestedDict(col, name, doc["data"], default=default)
    
    print(f"Created new: {name}")
    col.insert_one({"_id": name, "data": {}})
    return MongoNestedDict(col, name, default=default)


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
default_sv_settings = {
    "name": "N/A",
    "allowed_channels": [],
    "premium": 100,
    "invite_link": "N/A",
    "owner": "N/A",
    "moderators": [],
    "banned_words": [],
    "block_list": [],
    "muted": {},
    "invites": {},
    "rank": {},
    "rank_channel": 0,
    "rank_reward": {},
    "automod": {},
    "protections": {},
    "welcome_channel": 0,
    "welcome_message": "",
    "welcome_image": 1,
    "social": {
        "yt": None,
        "insta": None,
        "twitter": None,
        "social_channel": 0
    },
    "timer_messages": False,
    "afk": [],
    "warn": {},
    "warn_action": {},
    "logging": 0
}

Profiles         = load_mongo_dict("profiles", "server", default_profiles)
Server_Settings  = load_mongo_dict("server_settings", "server", default_sv_settings)
Invite_Cache     = load_mongo_dict("invite_cache", "server")
Guild_Invites    = load_mongo_dict("guild_invites", "server")

Relation         = load_mongo_dict("relations", "kellymemory")
Chats            = load_mongo_dict("chats", "kellymemory")
Memory           = load_mongo_dict("memory", "kellymemory")
Database         = load_mongo_dict("database", "kellymemory")
Persona          = load_mongo_dict("personality", "kellymemory")
Behaviours       = load_mongo_dict("behaviors", "kellymemory")

# ===== Setting up Clients =====

CLIENT0 = InferenceClient(token= os.getenv("HF_KEY"))
CLIENT1 = OpenAI(base_url="https://openrouter.ai/api/v1",api_key= os.getenv("KEY"))#ai model connection
CLIENT2 = OpenAI(base_url="https://openrouter.ai/api/v1",api_key= os.getenv("KEY2"))#ai model connection
CLIENT3 = OpenAI(base_url="https://openrouter.ai/api/v1",api_key= os.getenv("KEY6"))
CLIENT4 = OpenAI(base_url="https://openrouter.ai/api/v1",api_key= os.getenv("KEY3"))#ai model connection
CLIENT5 = OpenAI(base_url="https://openrouter.ai/api/v1",api_key= os.getenv("KEY4"))#ai model connection
CLIENT6 = OpenAI(base_url="https://openrouter.ai/api/v1",api_key= os.getenv("KEY5"))#ai model connection
CLIENT7 = ApifyClient(os.getenv("KEYZ"))
GENIUS = Genius(os.getenv("GENIUS"))

clients = [CLIENT0, CLIENT1, CLIENT2, CLIENT3, CLIENT4, CLIENT5, CLIENT6]

# ===== Geting AI Repaonse =====

def getResponse(usermessage, prompt, assistant="", client=0):
    """Universal AI Response Provider"""
    global client_lastRequest
    messages = [{"role":"system","content": prompt}]
    
    if assistant != "":
        #adding history
        for msg in assistant.split("\n"):
            user = msg.split(":")
            if user[0] == "User":
                messages.append({"role":"user","content":user[1]})
            else:
                messages.append({"role":"assistant","content":user[1]})
    #adding current message
    messages.append({"role":"user","content": usermessage})
    #setting model
    if client == 0:
        if "roleplay" in prompt.lower() or "giyu" in prompt.lower():
            model = "meta-llama/Meta-Llama-3-8B-Instruct"
        else:
            model = "deepseek-ai/DeepSeek-V3-0324"
    elif "roleplay" in prompt.lower() or "giyu" in prompt.lower():
        model = "meta-llama/llama-3.3-70b-instruct:free"
    else:
        model = "deepseek/deepseek-chat-v3-0324:free "
    try:
        response = clients[client].chat.completions.create(
            messages= messages,
            temperature=1.0,
            top_p=1.0,
            max_tokens=200,
            model= model
        )
        if not response.choices:
            print("Model Changed")
            next_client = client+1
            if next_client == 7:
                print("All clients failed")
                return
            return getResponse(usermessage, prompt, assistant, client=next_client)
    except:
        print("Model Changed")
        next_client = client+1
        if next_client == 7:
            print("All clients failed")
            return
        return getResponse(usermessage, prompt, assistant, client=next_client)

        
    print(f"#==========Response==========#\nModel: {model}\n\nINPUT: {messages}\nOUTPUT: {response.choices[0].message.content}\n#============================#")
    return response.choices[0].message.content
        
def timestamp(ctx):
    tz = None
    if not ctx.author:
        return "Aura++"
    locale = getattr(ctx.author, "locale", None)
    if locale:
        locale = ctx.author.locale.lower()
        tz_map = {
            "en-us": "America/New_York",
            "en-gb": "Europe/London",
            "en-in": "Asia/Kolkata",
            "hi": "Asia/Kolkata",
            "fr": "Europe/Paris",
            "de": "Europe/Berlin"
        }
        if locale in tz_map:
            tz = pytz.timezone(tz_map[locale])

    if not tz:
        tz = pytz.utc

    now = datetime.now(tz)
    formatted = now.strftime("%d %B %Y — %I:%M %p")

    return formatted
    
# ===== Utility Functions =====

async def safe_dm(member: discord.Member, embed: discord.Embed = None, message = None, view = None):
    """Safely tries to DM a user, fallback to channel if DMs are closed."""
    try:
        if not member.dm_channel:
            await member.create_dm()
        msg = await member.dm_channel.send(content = message,embed=embed, view = view)
    except:
        # if dm not possible then ping in server and message
        return False
    return msg

def action_embed(ctx: commands.Context, title: str = "", desc: str = "",  member=None, color=Color.pink(), text = None, thumbnail = None, url = None):
    """Creates a consistent embed style for actions."""
    embed = Embed(title=title, description=desc, color=color)
    if text:
        embed.set_footer(text=f"{text} | {timestamp(ctx)}", icon_url=ctx.author.avatar)
    if member:
        embed.set_author(name=member.name, icon_url=member.avatar)
    if thumbnail:
        embed.set_thumbnail(url = thumbnail)
    if url:
        embed.url = url
    return embed
        
# ===== BugReportView =====

class BugReportView(View):
    def __init__(self, button, message, view, ctx, replymsg = None):
        super().__init__(timeout=None)  # No timeout ✅
        self.buttom = button
        self.msg = message
        self.view = view
        self.ctx = ctx
        self.replymsg = replymsg
    
    @discord.ui.button(label="Reply", style=discord.ButtonStyle.green, custom_id="approve_btn")
    async def approve(self, interaction, button):
        modal = ReportBugModal(self.buttom, self.msg, self.view, self.ctx, self.replymsg, True) #reply
        await interaction.response.send_modal(modal)
        
class ReportBugModal(discord.ui.Modal):
    def __init__(self, button, message, view, ctx, replymsg = None, reply= False):
        super().__init__(title="Submit Your Report")
        self.button = button
        self.view = view
        self.ctx = ctx
        self.message = message
        self.replymsg = replymsg
        self.reply = reply
        if not reply:
            self.input_box = TextInput(label="Enter your Bug/Query/Suggestion:",custom_id="query", required= True, min_length=2, max_length=512, style=TextStyle.paragraph)
        else:
            self.input_box = TextInput(label="Enter Reply",custom_id="reply", required= True, min_length=2, max_length=512, style=TextStyle.paragraph)
        self.add_item(self.input_box)
            
    async def on_submit(self, interaction: Interaction):
      try:
        button = self.button
        msg = self.message
        view = self.view
        ctx = self.ctx
        if self.reply:
            query = interaction.message.embeds[0].description.split("```")[1]
            em = Embed(title = "Reply for your Bug/Query/Suggestion Submit", description= f"**Your Query**:\n```{query}```\n**Response**:\n```{self.input_box.value}```", color = Color.green())
            em.set_thumbnail(url = ctx.bot.get_user(894072003533877279).avatar)
            em.set_footer(text= f"Replied by happy__harsh | 894072003533877279")
            dm_channel = ctx.author.dm_channel
            if not dm_channel:
                dm_channel = await ctx.author.create_dm()
            await dm_channel.send(embed = em)
            if self.replymsg:
                view = View()
                view.add_item(Button(style=ButtonStyle.green, label = "Replied", custom_id= "button", disabled = True))
                await self.replymsg.edit(view=view)
            await interaction.response.defer()
            return 
                
        button.disabled = True
        await msg.edit(view=view)
        await interaction.channel.send(f"{ctx.author.mention}",embed= Embed(title= "Your Response has been recored successfully", color = Color.green()))
        em = Embed(title = f"Bug Reported by {ctx.author.display_name}", description= f"**Username**: {ctx.author.name}\n**Id**: {ctx.author.id}\n**Guild**: [{ctx.guild.name}]({Server_Settings[str(ctx.guild.id)]['invite_link']})\n**Report**: ```{self.input_box.value}```", color = Color.green())
        em.set_thumbnail(url = ctx.author.avatar)
        em.set_footer(text= f"Reported by {ctx.author.name} | {timestamp(ctx)}", icon_url = ctx.author.avatar)
        view = BugReportView(button, msg, view, ctx)
        msg = await interaction.client.get_user(894072003533877279).send(embed = em, view = view)
        view.replymsg = msg
        await interaction.response.defer()
      except Exception as e:
        await interaction.client.get_user(894072003533877279).send(e)
        
# ===== Kelly Enoji ====
def kemoji():
    return EMOJI[choice(list(EMOJI.keys()))]
    
print("__init__ was runned")
