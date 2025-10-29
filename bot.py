import discord
from discord.ext import commands, tasks
from datetime import datetime , UTC, timedelta
from json import dump, load
from random import randint
import time
import math
from __init__ import *

class Bot:

    def __init__(self, client, kelly):
        self.client = client
        self.kelly = kelly
        self.last_request = datetime.now()

    @tasks.loop(minutes=1)
    async def unmute(self):
        for guild_id, settings in Server_Settings.items():
            for muted_id, duration in list(settings["muted"].items()):
                if datetime.fromisoformat(duration) < datetime.now(UTC):
                    # Remove expired mute
                    settings["muted"].pop(muted_id)

                    try:
                        user = await self.client.fetch_user(int(muted_id))
                        em = Embed(
                            title="You were Unmuted",
                            description="**Reason:** Expired\nYou can again start chatting with Kelly using `kelly hii`.\nPlease be respectful this time.",
                            color=Color.green()
                        )
                        em.set_footer(
                            text=f"{user.id} | {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')}",
                            icon_url=self.client.user.avatar
                        )
                        em.set_author(name=user.name, icon_url=user.avatar)
                        await user.send(embed=em)
                    except Exception as dm_error:
                        print(f"Could not DM {muted_id}: {dm_error}")
                        

    @tasks.loop(minutes=1)
    async def mood_swings(self):
        action = self.kelly.mood.moodSwing()
        for settings in Server_Settings.values():
            if randint(1,7) == 7 and settings["timer_messages"]:
                await self.kelly.reportAction(action)

    @tasks.loop(minutes=100)
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
        self.unmute.start()
        #await self.client.change_presence(activity=discord.Game(name=""))
        for guild in self.client.guilds:
            invite_link = None
            for channel in guild.text_channels:
                try:
                    invite = await channel.create_invite(max_age=0, max_uses=0)  # infinite invite
                    invite_link = str(invite)
                    break
                except:
                    continue
            if str(guild.id) not in Server_Settings:
                Server_Settings[str(guild.id)] = {"name": guild.name,"allowed_channels": [],"premium": False,"invite_link": invite_link,"owner": guild.owner_id, "moderators": [], "banned_words": [],"block_list": [],"muted": {},"rank": {},"rank_channel": 0,"join/leave_channel": 0,"welcome_message": "", "welcome_image": 1, "social": {"yt": None, "insta": None, "twitter": None, "social_channel": 0}, "timer_messages": False, "afk": [],"friends": []}
        for cmd in self.client.commands:
            if not cmd.help and cmd.callback.__doc__:
                cmd.help = cmd.callback.__doc__.strip()
        for cmd_name, brief_text in DATA["brief"].items():
            cmd = self.client.get_command(cmd_name)
            if cmd:
                cmd.brief = brief_text

    
    async def on_message(self, message: discord.Message):
        start = time.time()
        id = message.author.id
        guild = message.guild.id
        channel = message.channel.id
        try:
            #Ignoring Self message
            if self.client.user == message.author or message.author.bot:
                return
            #Deleting banned words
            for word in Server_Settings[str(message.guild.id)]["banned_words"]:
                if word in message.content:
                    try:
                        await message.delete()
                    except:
                        print("No delete message perms")
                    break
            #Handelling Bot mentions
            if self.client.user.mention in message.content:
                if " activate" in message.content.lower():
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
                    total_xp = Server_Settings[str(guild)]["rank"][str(id)]
                    level = (math.sqrt(1+8*(total_xp//15)) -1)//2
                    max_xp = ((level+1)*(level+2)*15)//2
                    total_xp += 2
                    if total_xp > max_xp:
                        channel = await message.guild.fetch_channel(Server_Settings[str(guild)]["rank_channel"])
                        await channel.send(f"{message.author.mention} you reached Level {level+1}") 
                    Server_Settings[str(guild)]["rank"][str(id)] += 2
                else: 
                    Server_Settings[str(guild)]["rank"][str(id)] = 2

            #checking for afk user
            for afk in Server_Settings[str(guild)]['afk']:
                if id == afk:
                    Server_Settings[str(guild)]['afk'].remove(afk)
                elif self.client.get_user(afk).mentioned_in(message):
                    await message.channel.send(f"Please dont mention `@{self.client.get_user(afk).name}` they have gone afk!!")
            #checking for allowed channel
            if Server_Settings[str(guild)]["allowed_channels"] != [] and channel not in Server_Settings[str(guild)]["allowed_channels"] and message.content.lower().startswith(("kasturi", "kelly")):
                return
            #replying to replies i.e messages without prefixes
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
            message.content = message.content.lower()

            if not message.content.startswith(("kasturi", "kelly", "k")):
                if "kasturi" in message.content.lower() or "kelly" in message.content.lower():
                    await self.kelly.kellyQuery(message)
                return
            message.content = message.content.replace("kelly","").replace("kasturi","").strip()
            if message.content[0] == "k":
                message.content = message.content[1:].strip()
                for command in self.client.commands:
                    if message.content.split()[0] in command.name or message.content.split()[0] in command.aliases:
                        break
                else: return
                
            if message.content[0] == " ":
                message.content = "???" + message.content[1:]
            else:
                message.content = "???" + message.content
            print("Processing command on message: "+ message.content)
            await self.client.process_commands(message) #Kelly Process the message ;)
            print("Latency: ", (time.time() - start))
            return
        except Exception as e:
            print("error in on_message: ", e)

    async def on_guild_join(self, guild: discord.Guild):
        channels = guild.channels 
        invite = None
        for channel in channels:
            if isinstance(channel, discord.TextChannel):
                if "general" in channel.name or "chat" in channel.name:
                    try:         
                        invite = await channel.create_invite(max_age=0, max_uses=0)
                        em = Embed(title = f"{EMOJI[choice(list(EMOJI.keys()))]} **Kelly is Here**", description=f"Hey Everyone, Thanks for inviting Kelly here.\nUse `K activate` to complete up Kelly Setup\nUse `k help` to get started with user guide.",color = discord.Colour.green())
                        em.set_author(name= "Kelly", icon_url= f"https://cdn.discordapp.com/emojis/{choice(list(EMOJI.values())).split(":")[1]}")
                        em.thumbnail(url= f"https://cdn.discordapp.com/emojis/{choice(list(EMOJI.values())).split(":")[1]}")
                        em.set_footer(text=f"⟡ {len(self.client.guilds)} Guilds Strong 💪🏻 | At {datetime.now(UTC).strftime('%m-%d %H:%M')}")
                        await channel.send(embed= em)
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
        msg = discord.Embed(title=f"Kelly Joined {guild.name}",description=guild.description if guild.description else "No description", color=discord.Color.green(),url=invite)
        if guild.icon:
            msg.set_thumbnail(url=guild.icon.url)
        msg.set_footer(text=f"joined at {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')}", icon_url= self.client.user.avatar)
        me = self.client.get_user(894072003533877279)  
        await me.send(embed=msg)
        Server_Settings[str(guild.id)] = {
        "name": guild.name,
        "allowed_channels": [],
        "premium": False,
        "invite_link": str(invite),
        "owner": int(guild.owner_id),
        "moderators": [],
        "banned_words": [],
        "block_list": [],
        "muted": {},
        "rank": {},
        "rank_channel": 0,
        "join/leave_channel": 0,
        "afk": [],
        "friends": [],
        "reviver": False
    }

    async def on_guild_remove(self, guild: discord.Guild):
        me = self.client.get_user(894072003533877279)  
        await me.send(f"Left a server: {Server_Settings[str(guild.id)]["name"]}\n{Server_Settings[str(guild.id)]["invite_link"]}")
        Server_Settings.pop(str(guild.id))
    
    async def on_member_join(self, member: discord.Member):
        if Server_Settings[str(member.guild.id)]["join/leave_channel"]:
            welcome_message = Server_Settings[str(member.guild.id)]["welcome_message"]
            em = Embed(title= f"<:heeriye:1428773558062153768> **{welcome_message.split("\n")[0]}**", description="\n".join(welcome_message.split("\n")[1:]), color = Color.dark_gray())
            em.set_author(name= member.name, icon_url= member.avatar)
            em.set_thumbnail(url=member.avatar)
            em.set_image(url= f"https://raw.githubusercontent.com/happyharsh-codes/Kasturi/refs/heads/main/assets/welcome_message_{Server_Settings[str(member.guild.id)]["welcome_image"]}.gif")
            em.set_footer(text=f"﹒ ﹒ ⟡ {member.guild.member_count} Members Strong 💪🏻 | At {datetime.now(UTC).strftime('%m-%d %H:%M')}")
            try:
                channel = await member.guild.fetch_channel(Server_Settings[str(member.guild.id)]["join/leave_channel"])
                await channel.send(f"Welcome {member.mention} <:heart_draw:1428773561904140469>",embed=em)
            except:
                print("No perms allowed")

    async def on_member_remove(self, member: discord.Member):
        if Server_Settings[str(member.guild.id)]["join/leave_channel"]:
            em = Embed(title=f"**{member.name} left the server**", description=f"We are sorry to see you leave!\nHope you'd come back soon.", color= Color.dark_gray())
            em.set_author(name= member.name, icon_url = member.avatar)
            em.thumnail(url= member.avatar)
            em.set_footer(text=f"﹒ ﹒ ⟡ {member.guild.member_count} Members Strong | At {datetime.now(UTC).strftime('%m-%d %H:%M')}")
            try:
                channel = await self.client.fetch_channel(Server_Settings[str(member.guild.id)]["join/leave_channel"])
                await channel.send(embed=em)
            except:
                print("No perms allowed")

    async def on_presence_update(self, before, after):
        try:
            if before.status == discord.Status.offline and after.status != discord.Status.offline:
                if str(before.id) in Relation and Relation[str(before.id)] > 10:
                    if randint(1,5) == 1:
                        for guilds in self.client.guilds:
                            member = guilds.get_member(before.id)
                            if member:
                                allowed_channels = Server_Settings[str(guilds.id)]["allowed_channels"]
                                if allowed_channels != []:
                                    channel = await guilds.fetch_channel(allowed_channels[0])
                                    if channel:
                                        await channel.send(f"{member.mention} " + getResponse(f"*User: {member.name} just got online*", "You are kelly lively discord mod bot with sass and attitude. User just got online send a welcome message in 20 words or less.", client=0))
                                break
        except Exception as e:
            await self.client.get_user(894072003533877279).send("Exception on presence change:" +e)
        
    async def on_command_completion(self, ctx):
        try:
            Profiles[ctx.author.id]["aura"] += 1
        except:
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

        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(f"Ayoo you dont have permissions to do that!! {EMOJI[choice(["kellyidontcare","kellyannoyed", "kellycheekspull", "kellygigle", "kellybweh", "kellywatching"])]}")

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
            await ctx.send("Unknown error happened :/")
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

