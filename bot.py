import discord
from discord.ext import commands, tasks
from datetime import datetime , UTC, timedelta
from json import dump, load
from random import randint
import time
from __init__ import *

class Bot:

    def __init__(self, client, kelly):
        self.client = client
        self.kelly = kelly
        self.last_request = datetime.now()

    @tasks.loop(seconds=3600)
    async def mood_swings(self):
        self.kelly.mood.modifyMood({"happy": -5, "busy": -5, "sleepy": randint(1,15)})

    @tasks.loop(minutes=10)
    async def save_files(self):
        with open("res/server/profiles.json", "w") as f:
            dump(Profiles, f, indent=4)
        with open("res/server/server_settings.json", "w") as f:
            dump(Server_Settings, f, indent=4)
        self.kelly.save()
        print("Files saved")

    async def on_ready(self):
        print(f"Bot is ready. Logged in as {self.client.user}")
        print("We are ready to go!")
        self.mood_swings.start()
        self.save_files.start()
        #await self.client.change_presence(activity=discord.Game(name=""))

    async def on_message(self, message: discord.Message):
        start = time.time()
        id = message.author.id
        guild = message.guild.id
        channel = message.channel.id
        try:
            if self.client.user == message.author or message.author.bot:
                return
            if self.client.user.mention in message.content:
                if "activate" in message.content.lower():
                    if message.channel.permissions_for(message.author).manage_channels:
                        if channel in Server_Settings[str(guild)]["allowed_channels"]:
                            await message.channel.send("Ayo this channel is already activated !! haha")
                        else:
                            Server_Settings[str(guild)]["allowed_channels"].append(channel)
                            await message.channel.send(embed=discord.Embed(title="Channel Activated",description=f"<#{channel}> was succesfully activated !! Start talking with Kelly now.\n\n Use {self.client.user.mention} activate to use me in other channels too!!\nNote now Kasturi will only run in activated channels!!", color= discord.Colour.green()))
                    else:
                        await message.channel.send("Ayoo user you need `manage channels` permission to user this command.")
                    return
                if "deactivate" in message.content.lower():
                    if channel not in Server_Settings[str(guild)]["allowed_channels"]:
                        await message.channel.send("Ayoo that channel isn't even activated!! What are you doing idiot.")
                        return
                    Server_Settings[str(guild)]["allowed_channels"].remove(channel)
                    await message.channel.send(embed=discord.Embed(title="Channel Deactivated",description=f"<#{channel}> was succesfully deactivated !!", color= discord.Colour.green()))
                    return
                em = discord.Embed(title= 'Kasturi/Kelly', description= "Hi I'm Kelly Nice to meet you", colour= discord.Colour.green())
                em.set_thumbnail(url = self.client.user.avatar)
                em.add_field(name= "Help", value="Get Help using `k help` command")
                em.add_field(name= "Chat with me",value=f"Chat with me in activated channel use {self.client.user.mention} ``activate`` ")
                await message.channel.send(embed=em)
                return
            
            #Giving xp
            if Server_Settings[str(guild)]["rank_channel"] != 0:
                if str(id) in Server_Settings[str(guild)]["rank"]:
                    Server_Settings[str(guild)]["rank"][str(id)] += 2
                else: 
                    Server_Settings[str(guild)]["rank"][str(id)] = 2

            #checking for afk user
            for afk in Server_Settings[str(guild)]['afk']:
                if id == afk:
                    Server_Settings[str(guild)]['afk'].remove(afk)
                elif self.client.get_user(afk).mentioned_in(message):
                    await message.channel.send(f"Please dont mention `@{self.client.get_user(afk).name}` they have gone afk!!")

            if Server_Settings[str(guild)]["allowed_channels"] != [] and channel not in Server_Settings[str(guild)]["allowed_channels"]:
                return
            if message.reference and message.reference.message_id:
                try:
                    original = await message.channel.fetch_message(message.reference.message_id)
                    if original.author.id == self.client.user.id:
                        print(f"Reply to Kelly detected: {message.content}")
                        await self.kelly.kellyQuery(message)
                        return
                except discord.NotFound:
                    pass  # original message not found (maybe deleted)
                return

            # Otherwise, only handle messages with valid prefixes
            if not message.content.startswith(("kasturi", "kelly", "k")):
                return
            message.content = message.content.lower()
            message.content = message.content.replace("kelly","").replace("kasturi","").strip()
            if message.content[0] == "k":
                message.content = message.content[1:].strip()
            message.content = "???" + message.content
            print("Processing command on message: "+ message.content)
            await self.client.process_commands(message)
            print("Latency: ", (time.time() - start))
            return
        except Exception as e:
            print(e)

    async def on_guild_join(self, guild: discord.Guild):
        channels = guild.channels 
        invite = None
        for channel in channels:
            if isinstance(channel, discord.TextChannel):
                if "general" in channel.name or "chat" in channel.name:
                    try:         
                        invite = await channel.create_invite(max_age=0, max_uses=0)
                        await channel.send(embed= discord.Embed(title = "Kasturi/Kelly", description=f"Hey Everyone, Thanks for inviting Kelly/Kasturi here.\nType {self.client.user.mention} activate to start convo in a channel\nUse `k help` to get started with user guide.",color = discord.Colour.green()))
                        break
                    except:
                        continue
        else:
            for channel in channels:
                if isinstance(channel, discord.TextChannel):
                    try:
                        invite = await channel.create_invite(max_age=0,max_uses=0)
                        await channel.send(embed= discord.Embed(title = "Kasturi/Kelly", description=f"Hey Everyone, Thanks for inviting Kelly/Kasturi here.\nType {self.client.user.mention} activate to start convo in a channel\nUse `k help` to get started with user guide.",color = discord.Colour.green()))
                        break
                    except:
                        continue
        msg = discord.Embed(title=f"Minecord Joined {guild.name}",description=guild.description if guild.description else "No description", color=discord.Color.green(),url=invite)
        if guild.icon:
            msg.set_thumbnail(url=guild.icon.url)
        msg.set_footer(text=f"joined at {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')}", icon_url= self.client.user.avatar)
        me = self.client.get_user(894072003533877279)  
        await me.send(embed=msg)
        Server_Settings[str(guild.id)] = {"name": guild.name, "allowed_channels": [], "premium": False, "invite_link": str(invite.url),"block_list":[], "rank":{}, "rank_channel": 0, "yt": {}, "join/leave_channel": 0, "afk": []}

    async def on_guild_remove(self, guild: discord.Guild):
        me = self.client.get_user(894072003533877279)  
        await me.send(f"Left a server: {Server_Settings[str(guild.id)]["name"]}\n{Server_Settings[str(guild.id)]["invite_link"]}")
        Server_Settings.pop(str(guild.id))
    

    async def on_command_completion(self, ctx):
        pass


    async def on_command_error(self, ctx, error):
        '''Handelling errors'''
        if isinstance(error, commands.CommandNotFound):
            ctx.message.content = ctx.message.content[3:]
            await self.kelly.kellyQuery(ctx.message)
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.reply("sorry I dont have perms to do that")
        elif isinstance(error, discord.Forbidden):
            pass
        elif isinstance(error,commands.CommandOnCooldown):
          await ctx.reply(embed=discord.Embed(title="Command On Cooldown",description=f"Take a rest, try again after ```{int(error.retry_after)}``` seconds",color= discord.Color.red()).set_footer(text=f"requested by {ctx.author.name} at  {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')}", icon_url=ctx.author.avatar)
        )
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("***Oho*** you are missing an argumemt.\nUse `k help <command>` to get help")
    
        elif isinstance(error, commands.CheckFailure):
            code = choice(['i will work under kelly',"i will obey kelly from now on", "i will always bow down to kelly"])
            emoji = EMOJI[f"kelly{choice(["blush", "thinking", "laugh", "gigle", "waiting", "idontcare"])}"]
            await ctx.reply(f"**{emoji} | ** you dont even have a profile\n**{choice(["📃","📜","📄","📑","📰","🗞","📚","📙","📕","📖","📗","📘","✒","✏","🖋","📝","📋"])} | **Type this to create new profile `{code}`")
            try:
                msg = await ctx.bot.wait_for("message", check= lambda x: x.author.id == ctx.author.id, timeout= 120)
            except asyncio.TimeoutError:
                pass
            if msg.content.lower() == code:
                Profiles[str(ctx.author.id)] = {"name": ctx.author.name, "cash": 100, "gem": 1, "kelly_repect": 0, "inv": {}, "aura":0, "skills": []}
                em = Embed(title="Profile Created Successfully", description=f"{ctx.author.mention} your profile is created successfully you can now start playing will all commands.\n\n:white_check_mark: You obatained bonous ₹100 cash 💵\n:white_check_mark: You obtained 1 gem 💎\n\nUse `k help games` to get more help and info.",color=Color.green())
                em.set_footer(text=f"{ctx.author.name} created acc at {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')}", icon_url= ctx.author.avatar)
                await ctx.send(embed = em)
            else:
                emoji = EMOJI[f"kelly{choice(["annoyed", "laugh", "gigle", "waiting", "idontcare", "chips", "bweh", "bweh"])}"]
                await msg.reply(f"**{emoji} | ** you dont even do a single thing properly disgusting!! Dont ever come to me again")
        else:
            print("Unknown error happened")
            user = self.client.get_user(894072003533877279)
            if user != None:
                await user.send(f"Crash report on command error: {error}")

    async def on_error(self, event_method):
        print(f"Error in event: {event_method}")
        await self.client.get_user(894072003533877279).send(f"Error in event: {event_method}")

    async def on_disconnect(self):
        print("Disconnected")
        with open("res/server/profiles.json", "w") as f:
            dump(Profiles, f, indent=4)
        with open("res/server/server_settings.json", "w") as f:
            dump(Server_Settings, f, indent=4)
        self.kelly.save()
        print("Files saved")

