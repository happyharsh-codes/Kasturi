import discord
from discord.ext import commands
from json import load, dump
from random import randint , choice
from discord import ButtonStyle, Embed, Color, SelectOption
from discord.ui import View, Button, Select
from datetime import datetime, UTC
import asyncio

with open("assets/info.json", "r") as f:
    DATA = load(f)
    EMOJI = DATA.get("emoji")

print("__init__ was runned")