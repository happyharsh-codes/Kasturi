import discord
from discord.ext import commands, tasks
from discord.ui import View, Button, Select
from discord import ButtonStyle, Embed, Color, SelectOption
from src.kellycore.kellycore import Kelly
from bot import Bot
from datetime import datetime, UTC
import os
import asyncio
from json import load, dump
import flask
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import openai

def run_web():
    server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
    server.serve_forever()

intents = discord.Intents(messages = True, moderation = True, guilds = True, message_content = True, dm_messages = True, members = True, presences = True, dm_reactions = True, reactions = True, emojis = True, emojis_and_stickers = True, voice_states= True, guild_scheduled_events = True)
client = commands.Bot(command_prefix="???",case_insensetive=True, help_command=None,intents=intents)

async def start():
    for file in os.listdir("src/cogs/"):
        if file.endswith(".py") and not file.startswith("__"):
            await client.load_extension("src.cogs."+file[:-3])
            
    client.add_listener(bot.on_automod_rule_create)
    client.add_listener(bot.on_automod_rule_update)
    client.add_listener(bot.on_automod_rule_delete)
    client.add_listener(bot.on_automod_action)
    client.add_listener(bot.on_guild_channel_delete)
    client.add_listener(bot.on_guild_channel_create)
    client.add_listener(bot.on_guild_channel_update)
    client.add_listener(bot.on_guild_channel_pins_update)
    client.add_listener(bot.on_private_channel_update)
    client.add_listener(bot.on_private_channel_pins_update)
    client.add_listener(bot.on_typing)
    client.add_listener(bot.on_connect)
    client.add_listener(bot.on_disconnect)
    client.add_listener(bot.on_error)
    client.add_listener(bot.on_entitlement_create)
    client.add_listener(bot.on_entitlement_update)
    client.add_listener(bot.on_entitlement_delete)
    client.add_listener(bot.on_ready)
    client.add_listener(bot.on_unavailable)
    client.add_listener(bot.on_guild_unavailable)
    client.add_listener(bot.on_guild_join)
    client.add_listener(bot.on_guild_remove)
    client.add_listener(bot.on_guild_update)
    client.add_listener(bot.on_guild_emojis_update)
    client.add_listener(bot.on_guild_stickers_update)
    client.add_listener(bot.on_audit_log_entry_create)
    client.add_listener(bot.on_invite_create)
    client.add_listener(bot.on_invite_delete)
    client.add_listener(bot.on_integration_create)
    client.add_listener(bot.on_integration_update)
    client.add_listener(bot.on_guild_integrations_update)
    client.add_listener(bot.on_webhooks_update)
    client.add_listener(bot.on_member_join)
    client.add_listener(bot.on_member_remove)
    client.add_listener(bot.on_member_update)
    client.add_listener(bot.on_user_update)
    client.add_listener(bot.on_member_ban)
    client.add_listener(bot.on_member_unban)
    client.add_listener(bot.on_presence_update)
    client.add_listener(bot.on_message)
    client.add_listener(bot.on_message_edit)
    client.add_listener(bot.on_message_delete)
    client.add_listener(bot.on_bulk_message_delete)
    client.add_listener(bot.on_poll_vote_add)
    client.add_listener(bot.on_poll_vote_remove)
    client.add_listener(bot.on_reaction_add)
    client.add_listener(bot.on_reaction_remove)
    client.add_listener(bot.on_guild_role_create)
    client.add_listener(bot.on_guild_role_delete)
    client.add_listener(bot.on_guild_role_update)
    client.add_listener(bot.on_scheduled_event_create)
    client.add_listener(bot.on_scheduled_event_delete)
    client.add_listener(bot.on_scheduled_event_update)
    client.add_listener(bot.on_scheduled_event_user_add)
    client.add_listener(bot.on_scheduled_event_user_remove)
    client.add_listener(bot.on_soundboard_sound_create)
    client.add_listener(bot.on_soundboard_sound_delete)
    client.add_listener(bot.on_soundboard_sound_update)
    client.add_listener(bot.on_stage_instance_create)
    client.add_listener(bot.on_stage_instance_delete)
    client.add_listener(bot.on_stage_instance_update)
    client.add_listener(bot.on_subscription_create)
    client.add_listener(bot.on_subscription_update)
    client.add_listener(bot.on_subscription_delete)
    client.add_listener(bot.on_thread_create)
    client.add_listener(bot.on_thread_join)
    client.add_listener(bot.on_thread_update)
    client.add_listener(bot.on_thread_remove)
    client.add_listener(bot.on_thread_delete)
    client.add_listener(bot.on_thread_member_join)
    client.add_listener(bot.on_thread_member_remove)
    client.add_listener(bot.on_voice_state_update)
    client add_listener(bot.on_voice_channel_effect)
    
    client.after_invoke(bot.after_any_command)
    client.before_invoke(bot.before_any_command)
    client.on_command_error = bot.on_command_error
    client.on_error = bot.on_error
    client.add_listener(bot.on_command_complete)
    
    try:
        await client.start(os.getenv("TOKEN"))
    except Exception as error:
        print(error)
        me = client.get_user(894072003533877279)
        await me.send(f"Erron on Kelly Bot: {error}")

print("kelly.py runned")
if __name__ == "__main__":
    kelly = Kelly("kelly", client)
    bot = Bot(client, kelly)
    threading.Thread(target=run_web).start()
    asyncio.run(start())
    




