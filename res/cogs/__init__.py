import discord
from discord.ext import commands
from json import load, dump
import random
from discord.ui import View, Button, Select
from discord import ButtonStyle, Embed, Color, SelectOption
from datetime import datetime, UTC

with open("assets/info.json", "r") as f:
    DATA = load(f)
    EMOJI = DATA.get("emoji")

print("__init__ was runned")