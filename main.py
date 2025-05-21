import discord
from discord.ext import commands, tasks
from discord.ui import View, Button, Select
from discord import ButtonStyle, Embed, Color, SelectOption
from res.kellycore.kellycore import Kelly
from bot import Bot
from web import app
from datetime import datetime, UTC
import os
import asyncio
from json import load, dump
import flask
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading

def run_web():
    server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
    server.serve_forever()

intents = discord.Intents(messages = True, moderation = True, guilds = True, dm_messages = True, members = True, presences = True, dm_reactions = True, reactions = True, emojis = True, emojis_and_stickers = True, message_content = True)
client = commands.Bot(command_prefix=None,case_insensetive=True,help_command=None,intents=intents)
client.remove_listener(client.on_message)

async def start():
    try:
        for file in os.listdir("res/cogs/"):
            if file.endswith(".py") and not file.startswith("__"):
                await client.load_extension("res.cogs."+file[:-3])
        client.add_listener(bot.on_ready)
        client.add_listener(bot.on_message)
        client.add_listener(bot.on_guild_join)
        client.add_listener(bot.on_guild_remove)
        client.add_listener(bot.on_command_error)
        client.add_listener(bot.on_error)
        client.add_listener(bot.on_disconnect)
        await client.start(os.getenv("TOKEN"))
    except Exception as error:
        me = client.get_user(894072003533877279)
        await me.send(f"Erron on Kelly Bot: {error}")

print("kelly.py runned")
if __name__ == "__main__":
    kelly = Kelly("kelly", client)
    bot = Bot(client, kelly)
    threading.Thread(target=run_web).start()
    asyncio.run(start())
    




