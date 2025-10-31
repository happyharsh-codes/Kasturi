import os
import time
import math
import asyncio
import requests
import flask
import threading
import http.server
from datetime import datetime, UTC, timedelta, timezone
from json import load, dump, loads
from random import choice, randint, choices

import discord
from discord.ext import commands, tasks
from discord.ui import View, Button, Select, TextInput
from discord import Interaction, ButtonStyle, Embed, Color, SelectOption, TextStyle

from openai import OpenAI
from huggingface_hub import InferenceClient
import instaloader
from apify_client import ApifyClient

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import yt_dlp
import sclib
from lyricsgenius import Genius

from dotenv import load_dotenv
load_dotenv()

with open("assets/info.json", "r") as f:
    DATA = load(f)
    EMOJI = DATA.get("emoji")
    EMOJI2 = DATA.get("emoji2")
    TIP = DATA.get("tips")
with open("res/server/inviter.json", "r") as f:
    INVITER = load(f)
    print("Loaded: inviter.json")
with open("res/server/help.json", "r") as f:
    HELP = load(f)
    print("Loaded: help.json")
with open("res/server/profiles.json", "r") as f:
    Profiles = load(f)
    print("Loaded: profiles.json")
with open("res/server/server_settings.json", "r") as f:
    Server_Settings = load(f)
    print("Loaded: server_settings.json")

with open("res/kellymemory/relations.json", "r") as f:
    Relation = load(f)
    print("Loaded: relations.json")
with open("res/kellymemory/chats.json", "r") as f:
    Chats = load(f)
    print("Loaded: chats.json")
with open("res/kellymemory/personality.json", "r") as f:
    Persona = load(f)
    print("Loaded: personality.json")
with open("res/kellymemory/behaviors.json", "r") as f:
    Behaviours = load(f)
    print("Loaded: behaviors.json")

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
            time.sleep(1)
            return getResponse(usermessage, prompt, assistant, client=next_client)
    except:
        print("Model Changed")
        next_client = client+1
        if next_client == 7:
            print("All clients failed")
            return
        time.sleep(1)
        return getResponse(usermessage, prompt, assistant, client=next_client)

        
    print(f"#==========Response==========#\nModel: {model}\n\nINPUT: {messages}\nOUTPUT: {response.choices[0].message.content}\n#============================#")
    return response.choices[0].message.content

def timestamp(ctx):
    return ctx.message.created_at.replace(tzinfo=timezone.utc).strftime('%d %B %Y %H:%M UTC')}

class BugReportView(View):
    def __init__(self):
        super().__init__(timeout=None)  # No timeout ✅

    @discord.ui.button(label="Approve", style=discord.ButtonStyle.green, custom_id="approve_btn")
    async def approve(self, interaction, button):
        nonlocal ReportBugModal
        modal = ReportBugModal(True) #reply
        await interaction.response.send_modal(modal)
        
class ReportBugModal(discord.ui.Modal):
    def __init__(self, button, message, view, ctx, reply= False):
        super().__init__(title="Submit Your Report")
        self.reply = reply
        if reply:
            self.input_box = TextInput(label="Enter your Bug/Query/Suggestion:",custom_id="query", required= True, min_length=2, max_length=512, style=TextStyle.paragraph)
        else:
            self.input_box = TextInput(label="Enter Reply",custom_id="reply", required= True, min_length=2, max_length=512, style=TextStyle.paragraph)
        self.add_item(self.input_box)
            
    def on_submit(self, interaction: Interaction):
      try:
        button = self.button
        msg = self.msg
        view = self.view
        ctx = self.ctx
        if self.reply:
            em = Embed(title = "Reply for your Bug/Query/Suggestion Submit", description= f"```{self.input_box.value}```", color = Color.green())
            em.set_footer(text= f"Replied by happy__harsh | 894072003533877279")
            dm_channel = ctx.author.dm_channel
            if not dm_channel:
                dm_channel = await ctx.author.create_dm()
            await dm.channel.send(embed = em)
            return 
                
        button.disabled = True
        await msg.edit(view=view)
        await interaction.channel.send(embed= Embed(title= "Your Response has been recored successfully", color = Color.green()))
        em = Embed(title = f"Bug Reported by {ctx.author.display_name}", description= f"**Username**: {ctx.author.name}\n**Id**: {ctx.author.id}\n**Guild**: [{ctx.guild.name}]({Server_Settings[str(ctx.guild.id)]["invite_link"]})\n**Report**: {self.input_box.value}", color = Color.green())
        em.set_footer(text= f"Reported by {ctx.author.name} | {timestamp(ctx)}", icon_url = ctx.author.avatar)
        view = BugReportView()
        await interaction.client.get_user(894072003533877279).send(embed = em, view = view)
        await interaction.response.defer()
      except Exception as e:
        await interaction.client.get_user(894072003533877279).send(e)
        
print("__init__ was runned")
