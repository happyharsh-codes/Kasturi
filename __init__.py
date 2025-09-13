import os
import time
import asyncio
import requests
from datetime import datetime, UTC, timedelta
import discord
from discord.ext import commands, tasks
from discord.ui import View, Button, Select
from discord import ButtonStyle, Embed, Color, SelectOption
from json import load, dump, loads
from random import choice, randint, choices
from openai import OpenAI

from dotenv import load_dotenv
load_dotenv()

with open("assets/info.json", "r") as f:
    DATA = load(f)
    EMOJI = DATA.get("emoji")

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

CLIENT1 = OpenAI(base_url="https://openrouter.ai/api/v1",api_key= os.getenv("KEY"))#ai model connection
CLIENT2 = OpenAI(base_url="https://openrouter.ai/api/v1",api_key= os.getenv("KEY2"))#ai model connection
CLIENT3 = OpenAI(base_url="https://openrouter.ai/api/v1",api_key= os.getenv("KEY6"))
CLIENT4 = OpenAI(base_url="https://openrouter.ai/api/v1",api_key= os.getenv("KEY3"))#ai model connection
CLIENT5 = OpenAI(base_url="https://openrouter.ai/api/v1",api_key= os.getenv("KEY4"))#ai model connection
CLIENT6 = OpenAI(base_url="https://openrouter.ai/api/v1",api_key= os.getenv("KEY5"))#ai model connection

clients = [CLIENT1, CLIENT2, CLIENT3, CLIENT4, CLIENT5, CLIENT6]

def getResponse(usermessage, prompt, assistant="", client=3):
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
    model= "deepseek/deepseek-chat-v3-0324:free"
    if prompt.startswith("Roleplay Kelly"):
        model="meta-llama/Llama-Vision-Free"
    try:
        response = clients[client-1].chat.completions.create(
            messages= messages,
            temperature=1.0,
            top_p=1.0,
            max_tokens=200,
            model= model
        )
        if not response.choices:
            print("Model Changed")
            next_client = client+1
            elif next_client == 7:
                print("All clients failed !!")
                return
            return getResponse(usermessage, prompt, assistant, client=next_client)
    except:
        print("Model Changed")
        next_client = client+1
        elif next_client == 7:
            print("All clients failed !!")
            return
        return getResponse(usermessage, prompt, assistant, client=next_client)

        
    print(f"#==========Response==========#\nModel: {model}\n\nINPUT: {messages}\nOUTPUT: {response.choices[0].message.content}\n#============================#")
    return response.choices[0].message.content

print("__init__ was runned")
