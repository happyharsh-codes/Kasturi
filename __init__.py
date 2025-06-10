import os
import time
import asyncio
from datetime import datetime, UTC
import discord
from discord.ext import commands, tasks
from discord.ui import View, Button, Select
from discord import ButtonStyle, Embed, Color, SelectOption
from json import load, dump, loads
from random import choice, randint, choices
from openai import OpenAI
from together import Together
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

commandz = {"ban":[], "kick":[], "mute":[]}

CLIENT1 = OpenAI(base_url="https://openrouter.ai/api/v1",api_key= os.getenv("KEY"))#ai model connection
CLIENT2 = OpenAI(base_url="https://openrouter.ai/api/v1",api_key= os.getenv("KEY2"))#ai model connection
CLIENT3 = Together()

client1_lastRequest = time.time()
client2_lastRequest = time.time()
client3_lastRequest = time.time()


def getResponse(usermessage, prompt, assistant="", client=3):
    global  client1_lastRequest, client2_lastRequest, client3_lastRequest
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

    if client == 3:
        model="meta-llama/Llama-Vision-Free",
        try:
            if time.time() < client3_lastRequest + 5:
                time.sleep(client3_lastRequest + 5 - time.time())
            response = CLIENT3.chat.completions.create(
                model="meta-llama/Llama-Vision-Free",
                messages= messages)
            client3_lastRequest = time.time()
        except:
            print("Model Changed")
            return getResponse(usermessage, prompt, assistant, client=1)
    elif client == 1:
        model= "deepseek/deepseek-prover-v2:free"
        if time.time() < client1_lastRequest + 15:
            time.sleep(client1_lastRequest + 15 - time.time())
        client1_lastRequest = time.time()
        response = CLIENT1.chat.completions.create(
            messages= messages,
            temperature=1.0,
            top_p=1.0,
            max_tokens=200,
            model= "deepseek/deepseek-prover-v2:free"
        )
        if not response.choices:
            print("Model Changed")
            return getResponse(usermessage, prompt, assistant, client=2)
    elif client == 2:
        model= "deepseek/deepseek-prover-v2:free"
        if time.time() < client2_lastRequest + 15:
            time.sleep(client2_lastRequest + 15 - time.time())
        client2_lastRequest = time.time()
        response = CLIENT2.chat.completions.create(
            messages= messages,
            temperature=1.0,
            top_p=1.0,
            max_tokens=200,
            model= "deepseek/deepseek-prover-v2:free"
        )
        if not response.choices:
            print("Model Changed")
            return getResponse(usermessage, prompt, assistant, client=1)
        
        
    print(f"#==========Response==========#\nModel: {model}\nPrompt: {prompt[0:5]}...{prompt[-5:]}\nINPUT: {usermessage}\nOUTPUT: {response.choices[0].message.content}\n#============================#")
    return response.choices[0].message.content

print("__init__ was runned")