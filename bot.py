from __init__ import *
from functions.game_functions import*

UNICODE_EMOJI_RE = re.compile(r"[\U0001F300-\U0001FAFF]")
DISCORD_EMOJI_RE = re.compile(r"<a?:\w+:\d+>")

class Bot:

    def __init__(self, client, kelly):
        self.client = client
        self.kelly = kelly
        self.last_request = datetime.now()
        self.me = None
    # ------------- INTERNAL HELPERS -------------

    async def send_log(self, guild: Guild, embed: discord.Embed):
        """Send an embed to the guild's log channel if logging is enabled."""
        channel_id = Server_Settings[str(guild.id)]["logging"]
        if not channel_id:
            return
        channel = self.client.get_channel(channel_id)
        if not channel:
            try:
                channel = await self.client.fetch_channel(channel_id)
            except:
                return
        try:
            await channel.send(embed=embed)
        except Exception:
            pass

    async def chat_rate_limiter(self, message, session_id, chat_rate_limit):
        count = 0 # no of messages in last 5 seconds
        for time in Last[session_id]:
            if (datetime.now - datetime.fromisoformat(time)).seconds() <= 5:
                count += 1
        if count > limit:
            try:
                async for msg in message.channel.histoty(limit=100):
                    if delete_count >= count:
                        break
                    if msg.author == message.author:
                        await msg.delete()
                        delete_count += 1
            except:
                pass
            await message.channel.send(f"{message.author.mention} You are sending messages too quickly")
            return True
        return False 
        
    async def emoji_spam(self, message, limit):
        content = message.content
        unicode_count = len(UNICODE_EMOJI_RE.findall(content))
        discord_count = len(DISCORD_EMOJI_RE.findall(content))
        total = unicode_count + discord_count
        if total > limit:
            try:
                await message.delete()
            except:
                pass
            await message.channel.send(f"{message.author.mention} Too many emojis! ({total}/{limit})",delete_after= 5 )
            return True
        return False
        
    async def mass_mention_block(self, message, limit):
        if message.mention_everyone:
            await message.delete()
            await message.channel.send(f"{message.author.mention} Mass mention blocked.", delete_after=4)
            return True
            
        if len(message.mentions) > limit:
            await message.delete()
            await message.channel.send(f"{message.author.mention} Too many mentions!", delete_after=4)
            return True  
        return False

    async def caps_block(self, message):
        text = message.content
        if len(text) < 6:   # small messages allowed
            return False
        letters = [c for c in text if c.isalpha()]
        if not letters:
            return True
        caps = sum(1 for c in letters if c.isupper())
        ratio = caps / len(letters)
        if ratio > 0.20:
            try: await message.delete()
            except: pass
            await message.channel.send(f"{message.author.mention} Too many CAPS.", delete_after=4)
            return True
        return False
        
    async def link_filter(self, message, type):
        "type: suspicious links/ all links"
        SUSPICIOUS = ["grabify", "iplogger", "gyatt", "free-nitro", "robux-free"]
        content = message.content.lower()
        has_link = "http://" in content or "https://" in content
        if not has_link:
            return False
        if type == "all":
            await message.delete()
            await message.channel.send(f"{message.author.mention} Links are not allowed.", delete_after= 5)
            return True
        if type == "suspicious":
            if any(bad in content for bad in SUSPICIOUS):
                await message.delete()
                await message.channel.send(f"{message.author.mention} Suspicious link removed.", delete_after=5)
                return True
        return False
        
    async def nsfw_filter(self, message):
        NSFW_WORDS = {"sex", "porn", "xnxx", "xvideos", "nude", "boobs", "dick"}
        content = message.content.lower()
        if any(word in content for word in NSFW_WORDS):
            await message.delete()
            await message.channel.send(f"{message.author.mention} NSFW content detected.", delete_after=5)
            return True
        return False 

    async def duplicate_detector(self, message, session_id):
        duplicate_count = 0
        old_msg_contents = []
        def similar(new_msg, old_msg):
            return new_msg == old_msg
        for time, old_msg in Last[session_id].items():
            if similar(old_msg, message.content):
                duplicate_count += 1
                old_msg_contents.append(old_msg)
        if duplicate_count < 3:
            return False
        delete_count = 0
        try:
            async for msg in channel.history(limit=100):
                if delete_count >= 3:
                    break
                if msg.author == message.author and msg.content in old_msg_contents:
                    await msg.delete()
                    delete_count += 1
        except:
            pass
        await channel.send(f"{author.mention} Duplicate messages Blocked")
        return True

    async def rankReward(self, message, rank_channel, rewards, level):
        prize = rewards.get(int(level), None)
        if not prize:
            return
        amount = prize[1]
        prize = prize[0]

        if prize == "Cash":
            await rank_channel.send(f"{message.author.mention} You recived Cash prize {amount} on Leveling up!! Check your balance now")
            profile = GameProfile(message.author.id)
            profile.inv_manager("cash", amount)
        if prize == "Aura":
            await rank_channel.send(f"{message.author.mention} You recived Aura prize {amount} on Leveling up!! Check your balance now")
            profile = GameProfile(message.author.id)
            profile.inv_manager("aura", amount)
        if prize == "Gem":
            await rank_channel.send(f"{message.author.mention} You recived Gems prize {amount} on Leveling up!! Check your balance now")
            profile = GameProfile(message.author.id)
            profile.inv_manager("gem", amount)
        if prize == "Role":
            role = message.guild.get_role(amount)
            if not role:
                try:
                    role = await message.guild.fetch_role(amount)
                except:
                    return
            await rank_channel.send(f"{message.author.mention} You recived Role prize {role.mention} on Leveling up!! Check your balance now")
            await client.get_context(message).invoke(client.get_command("assignrole"), message.author, role)
        if prize == "Nitro":
            await rank_channel.send(f"{message.author.mention} You recived Cash prize {amount} on Leveling up!! Check your balance now")
            await safe_dm(message.author, message= f"You won Nitro gift code: {amount}")
            
    # ------------- TASK LOOPS -------------

    @tasks.loop(seconds=15)
    async def universal_loop(self):
        #Unmuting users
        for muted_id in list(self.kelly.giyu._giyu["muted"].keys()):
            if datetime.fromisoformat(self.kelly.giyu._giyu["muted"][muted_id]) < datetime.now():
                # Remove expired mute
                del self.kelly.giyu._giyu["muted"][muted_id]
                user = await self.client.fetch_user(int(muted_id))
                em = Embed(title="✅ You’ve Been Unmuted",description="**Reason:** Mute expired.\nYou may chat again. Please follow the server rules and behave.",color=Color.green())
                em.set_footer(text="Please refrain from sending messages like this. Future violations may result in a ban.")
                em.set_author(name=user.name, icon_url=user.avatar)
                await safe_dm(user,em)

        #Tasks and Reminders
        await self.kelly.performTasks()
        await self.kelly.performReminders()

        #clearing cache
        for session_ids, data in Last.items():
            for time, msg in data.items():
                if (datetime.now() - datetime.fromisoformat(time)).seconds > 60:
                    del data[time]
                    if data == {}:
                        del Last[session_ids]
                    break

        #game tasks
        await run_all_tasks(self.client)
        await run_all_reminders(self.client)


    @tasks.loop(minutes=2)
    async def mood_swings(self):
        try:
            #sync all
            #Server_Settings.root._sync()
            #Profiles.root._sync()
            #Last.root._sync()
            #Invite_Cache.root._sync()
            #Guild_Invites.root._sync()
            #self.kelly.memory._memory.root._sync()
            #self.kelly.giyu._giyu.root._sync()
            #self.kelly.ayasaka._ayasaka.root._sync()
        
            mood = self.kelly.mood.moodSwing()
            action_text = None
            message = None

            #Timer Message
            if randint(1,7) == 3:
                text = "Kelly got to revive the ded chat"
                prompt = "Roleplay Kelly, a cute Discord Mod (human like with mood and sass). Generate response activating ded chat in 20 words with 1-4 emojis"
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(None, getResponse, text, prompt, "", 0)
                reply = self.kelly.kellyEmojify(response)
                
                for gid, settings in Server_Settings:
                    if not settings["timer_messages"]:
                        continue
                    for channel_id in settings["activated_channels"]:
                        channel = self.client.get_channel(channel_id)
                        if not channel:
                            try:
                                channel = self.client.fetch_channel(channel_id)
                            except:
                                continue
                        await channel.send(reply)
            
            if mood[0] != mood[1]:
                prev_mood = mood[1]
                new_mood = mood[0]
                action = {"happy": "-# Kelly is so haply now 😃","sleepy": "-# Kelly is sleeping 😴","depressed": "-# Kelly is depressed 😔","angry": "-# Kelly is angry 😡","annoyed": "-# Kelly is very annoyed right now 😣","lazy": "-# Kelly is too lazy to respond now 😪","sad": "-# Kelly is so sad right now 😭","mischievous": "-# Kelly is feeling a little mischievous 😉"}
                if prev_mood == "sleepy":
                    mood_shift = "woke_up"
                elif new_mood == "sleepy":
                    mood_shift = "went_to_sleep"
                else:
                    mood_shift = new_mood
                for channel_id in Kelly_Last:
                    channel = self.client.get_channel(channel_id)
                    if not channel:
                        try:
                            channel = self.client.fetch_channel(channel_id)
                        except:
                            continue
                    await channel.send(action[new_mood], delete_after=150)
                    await channel.send(DATA["kelly_responses"]["mood_flex"][mood_shift], delete_after=150)
            
                
        except Exception as e:
            print("Error on Mood Change")
            await self.me.send(f"Exception on Mood change: {str(e)}")
        
    # ------------- EVENTS -------------

    async def on_automod_rule_create(self, rule):
        guild = rule.guild
        em = Embed(
            title="🛡️ AutoMod Rule Created",
            description=f"Rule: **{rule.name}**\nID: `{rule.id}`",
            color=Color.green()
        )
        await self.send_log(guild, em)

    async def on_automod_rule_update(self, rule):
        guild = rule.guild
        em = Embed(
            title="🛡️ AutoMod Rule Updated",
            description=f"Rule: **{rule.name}**\nID: `{rule.id}`",
            color=Color.yellow()
        )
        await self.send_log(guild, em)

    async def on_automod_rule_delete(self, rule):
        guild = rule.guild
        em = Embed(
            title="🛡️ AutoMod Rule Deleted",
            description=f"Rule: **{rule.name}**\nID: `{rule.id}`",
            color=Color.red()
        )
        await self.send_log(guild, em)

    async def on_automod_action(self, execution):
        guild = execution.guild
        em = Embed(
            title="🛡️ AutoMod Triggered",
            description=f"Rule: **{execution.rule_name}**\nUser: {execution.user} (`{execution.user.id}`)",
            color=Color.red()
        )
        await self.send_log(guild, em)

    async def on_guild_channel_delete(self, channel):
        guild = channel.guild
        em = Embed(
            title="📕 Channel Deleted",
            description=f"Channel: **{channel.name}** (`{channel.id}`)",
            color=Color.red()
        )
        await self.send_log(guild, em)

    async def on_guild_channel_create(self, channel):
        guild = channel.guild
        em = Embed(
            title="📗 Channel Created",
            description=f"Channel: **{channel.name}** (`{channel.id}`)",
            color=Color.green()
        )
        await self.send_log(guild, em)

    async def on_guild_channel_update(self, before, after):
        guild = after.guild
        changes = []
        if before.name != after.name:
            changes.append(f"Name: **{before.name}** → **{after.name}**")
        if before.topic != after.topic:
            changes.append("Topic changed.")
        if not changes:
            return
        em = Embed(
            title="📘 Channel Updated",
            description="\n".join(changes),
            color=Color.yellow()
        )
        em.add_field(name="Channel", value=f"{after.mention} (`{after.id}`)")
        await self.send_log(guild, em)

    async def on_guild_channel_pins_update(self, channel, last_pin):
        guild = channel.guild
        em = Embed(
            title="📌 Pins Updated",
            description=f"Channel: {channel.mention}\nLast pin: {last_pin}",
            color=Color.blue()
        )
        await self.send_log(guild, em)

    async def on_private_channel_update(self, before, after):
        # DM/group DM; no guild log
        pass

    async def on_private_channel_pins_update(self, channel, last_pin):
        pass

    async def on_typing(self, channel, user, when):
        if not Relation[str(user.id)]:
            return
        if randint(1,200) == 101: #Special reward
            self.kelly.ayaka.addReminder("surprise", channel_id=channel.id, user_id= user.id, delay_minutes=20)     
        if randint(1, 50) == 25:
            try:
                prompt = (
                    "Roleplay Kelly, a cute Discord Mod (human like with mood and sass)."
                    "Generate response for new user mentioning them when they show up typing something in 20 words with 1-4 emojis"
                )
                await channel.send(self.kelly.getEmoji(getResponse(f"{user.mention} is typing", prompt)))
            except:
                pass

    async def on_disconnect(self):
        print("Disconnected")

    async def on_error(self, event_method, *args, **kwargs):
        etype, value, tb = sys.exc_info()
        full_error = ''.join(traceback.format_exception(etype, value, tb))
        em = Embed(title= f"⚠️ Error {event_method}", description= f"```{full_error[:1900]}```", color=Color.red())
        for arg in args:
            if isinstance(arg, discord.Message):
                em.add_field(name="Message Content",value=f"`{arg.content[:500]}`",inline=False)
                em.add_field(name="Author",value=f"{arg.author} ({arg.author.id})",inline=False)
            if isinstance(arg, discord.Member):
                em.add_field(name="Member",value=f"{arg} ({arg.id})",inline=False)
            if isinstance(arg, discord.ext.commands.Context):
                em.add_field(name="Message Content",value=f"`{arg.message.content[:500]}`",inline=False)
                em.add_field(name="Author",value=f"{arg.author} ({arg.author.id})",inline=False)
            
        if self.me:
            try:
                await self.me.send(embed=em)
            except:
                pass
        print("".join(traceback.format_exception(etype, value, tb)))

    async def on_entitlement_create(self, entitlement):
        guild = entitlement.guild
        em = Embed(
            title="💳 Entitlement Created",
            description=f"User: {entitlement.user}\nSKU: `{entitlement.sku_id}`",
            color=Color.green()
        )
        await self.send_log(guild, em)

    async def on_entitlement_update(self, entitlement):
        guild = entitlement.guild
        em = Embed(
            title="💳 Entitlement Updated",
            description=f"User: {entitlement.user}\nSKU: `{entitlement.sku_id}`",
            color=Color.yellow()
        )
        await self.send_log(guild, em)

    async def on_entitlement_delete(self, entitlement):
        guild = entitlement.guild
        em = Embed(
            title="💳 Entitlement Deleted",
            description=f"User: {entitlement.user}\nSKU: `{entitlement.sku_id}`",
            color=Color.red()
        )
        await self.send_log(guild, em)

    async def on_ready(self):
        print(f"Bot is ready. Logged in as {self.client.user}")
        print("We are ready to go!")
        self.mood_swings.start()
        self.universal_loop.start()
        self.me = self.client.get_user(894072003533877279)
        if not self.me:
            try:
                self.me = await self.client.fetch_user(894072003533877279)
            except:
                self.me = None
        # saving guilds
        embed = Embed(title="✅ Kelly Updated",description="Kelly has been updated successfully and is running on the latest version 💫",color=Color.green())
        embed.set_footer(text="Kelly System", icon_url=self.client.user.avatar)
        embed.timestamp = datetime.now(UTC)
            
        for guild in self.client.guilds:
            invite = None
            for channel in [x for x in guild.text_channels if x.permissions_for(guild.me).send_messages]:
                if any(x in channel.name.lower() for x in ("general","chat","chill")):
                    await channel.send(embed= embed)
                    break
            else:
                for channel in [x for x in guild.text_channels if x.permissions_for(guild.me).send_messages]:
                    await channel.send(embed=embed)
                    break
            try:
                for open_invites in await guild.invites():
                    if open_invites.max_age == 0 and open_invites.max_uses == 0:
                        invite = open_invite
                        break
            except:
                pass
            if not invite:
                for channel in guild.text_channels:
                    try:
                        invite = await channel.create_invite(max_age=0, max_uses=0)
                        break
                    except:
                        continue
            if invite:
                Guild_Invites[str(guild.id)] = str(invite.code)
            
            #tracking invites
            try:
                Invite_Cache[guild.id] = {
                    invite.code: invite.uses for invite in await guild.invites()
                }
            except:
                pass
        
        # help / brief
        for cmd in self.client.commands:
            if not cmd.help and cmd.callback.__doc__:
                cmd.help = cmd.callback.__doc__.strip()

        for cmd_name, brief_text in DATA["brief"].items():
            cmd = self.client.get_command(cmd_name)
            if cmd:
                cmd.brief = brief_text

        #self.client.add_view(BugReportView())

    async def on_guild_available(self, guild):
        em = Embed(
            title="✅ Guild Available",
            description=f"{guild.name} (`{guild.id}`) is now available.",
            color=Color.green()
        )
        await self.send_log(guild, em)

    async def on_guild_unavailable(self, guild):
        em = Embed(
            title="⚠️ Guild Unavailable",
            description=f"{guild.name} (`{guild.id}`) is now unavailable.",
            color=Color.yellow()
        )
        await self.send_log(guild, em)

    async def on_guild_join(self, guild: discord.Guild):
        kelly = Button(style = ButtonStyle.link, url = "https://discord.gg/y56na8kN9e", label = "Kelly's Homeland")
        developer = Button(style= ButtonStyle.link, url = "https://github.com/happyharsh-codes", label = "Developer")
        view = View()
        view.add_item(kelly)
        view.add_item(developer)
        em = discord.Embed(title = f"{EMOJI[choice(list(EMOJI.keys()))]} **Kelly has Arrived!**", description=f"Thanks for adding me!\n• Say `kelly hi` to talk\n• Use `k activate` to enable chat\n• Use `k help` to view commands\n• Found a bug? Use `k bug`",color = discord.Colour.green())
        em.set_image(url="https://raw.githubusercontent.com/happyharsh-codes/Kasturi/refs/heads/main/assets/welcome_setup.png")
        em.set_thumbnail(url= f"https://raw.githubusercontent.com/happyharsh-codes/Kasturi/refs/heads/main/assets/kellyintro.gif")
        em.set_footer(text=f"⟡ {len(self.client.guilds)} Guilds Strong 💪🏻 | At {datetime.now(UTC).strftime('%m-%d %H:%M')}")

        invite = "N/A"
        for channel in [x for x in guild.text_channels if x.permissions_for(guild.me).send_messages]:
            if any(x in channel.name.lower() for x in ("general","chat","chill")):
                await channel.send("@everyone", embed= em, view=view)
                break
        else:
            for channel in [x for x in guild.text_channels if x.permissions_for(guild.me).send_messages]:
                await channel.send("@everyone", embed= em, view=view)
                break
        for channel in guild.text_channels:
            try:
                invite = await channel.create_invite(max_age=0, max_uses=0)
                invite = f"https://discord.gg/{str(invite.code)}"
                break
            except:
                continue
                
        msg = discord.Embed(title=f"Kelly Joined {guild.name}",description=guild.description if guild.description else "No description", color=discord.Color.green(),url=invite)
        if guild.icon:
            msg.set_thumbnail(url=guild.icon.url)
        msg.set_footer(text=f"joined at {datetime.now(UTC).strftime('%Y-%m-%d %H:%M')}", icon_url= self.client.user.avatar)
        me = self.client.get_user(894072003533877279)  
        await me.send(embed=msg)
        moderators = []
        for member in guild.members:
            if any(r.permissions.administrator or r.permissions.kick_members or r.permissions.ban_members or r.permissions.manage_roles or r.permissions.mute_members or r.permissions.deafen_members or r.permissions.manage_permissions or r.permissions.manage_channels for r in member.roles):
                moderators.append(member.id)
        Server_Settings[str(guild.id)] = {"name": guild.name,"allowed_channels": [],"premium": 100,"invite_link": invite,"owner": guild.owner_id,"moderators": moderators,"banned_words": [],"block_list": [],"muted": {},"invites": {},"rank": {},"rank_channel": 0,"rank_reward": {},"welcome_channel": 0,"welcome_message": "","welcome_image": 1,"social": {"yt": None,"insta": None,"twitter": None,"social_channel": 0},"timer_messages": False, "afk": [],"warn": {},"warn_action": {}, "automod": {}, "protections": {},"logging": 0}
        if invite != "N/A":
            Guild_Invites[str(guild.id)] = invite 
    
    async def on_guild_remove(self, guild: discord.Guild):
        banned_by = None
        try:
            async for entry in guild.audit_logs(limit=5):
                if entry.action == discord.AuditLogAction.bot_add: 
                    continue
                if entry.target.id == self.client.user.id:
                    banned_by = entry.user
                    break
        except:
            pass
        me = self.client.get_user(894072003533877279)
        invite = Server_Settings[str(guild.id)]["invite_link"]
        if invite == "N/A" and Guild_Invites[str(guild.id)]:
            invite = Guild_Invites[str(guild.id)]
            invite = f"https://discord.gg/{invite}"
            del Guild_Invites[str(guild.id)]
        em = Embed(title="Kelly Left a Server",color=Color.red(),description=f"Server: **{guild.name}**\nMembers: {len(guild.members)}")
        if banned_by:
            em.add_field(name="Banned By", value=f"{banned_by} ({banned_by.id})")
        else:
            em.add_field(name="Reason", value="Bot was kicked or server deleted")
        em.add_field(name="Invite Link", value=invite)
        em.set_thumbnail(url=guild.icon)
        if invite != "N/A":
            await me.send(invite, embed=em)
        else:
            await me.send(embed=em)
        del Server_Settings[str(guild.id)]
        
    async def on_guild_update(self, before, after):
        """When guild updates: Name, AFK channels, afk timeout, etc"""
        changes = []
        if before.name != after.name:
            changes.append(f"Name: **{before.name}** → **{after.name}**")
        if before.afk_channel != after.afk_channel:
            changes.append(
                f"AFK Channel: {getattr(before.afk_channel, 'mention', None)} → "
                f"{getattr(after.afk_channel, 'mention', None)}"
            )
        if before.afk_timeout != after.afk_timeout:
            changes.append(f"AFK Timeout: {before.afk_timeout}s → {after.afk_timeout}s")
        if not changes:
            return
        em = Embed(
            title="🏰 Guild Updated",
            description="\n".join(changes),
            color=Color.yellow()
        )
        await self.send_log(after, em)

    async def on_guild_emojis_update(self, guild, before, after):
        added = [e for e in after if e not in before]
        removed = [e for e in before if e not in after]
        if not added and not removed:
            return
        desc = []
        if added:
            desc.append("Added: " + ", ".join(str(e) for e in added))
        if removed:
            desc.append("Removed: " + ", ".join(str(e) for e in removed))
        em = Embed(
            title="😀 Emojis Updated",
            description="\n".join(desc),
            color=Color.blue()
        )
        await self.send_log(guild, em)

    async def on_guild_stickers_update(self, guild, before, after):
        added = [s for s in after if s not in before]
        removed = [s for s in before if s not in after]
        if not added and not removed:
            return
        desc = []
        if added:
            desc.append("Added: " + ", ".join(s.name for s in added))
        if removed:
            desc.append("Removed: " + ", ".join(s.name for s in removed))
        em = Embed(
            title="🏷️ Stickers Updated",
            description="\n".join(desc),
            color=Color.blue()
        )
        await self.send_log(guild, em)

    async def on_audit_log_entry_create(self, entry):
        guild = entry.guild
        em = Embed(
            title="📜 Audit Log Entry",
            description=f"Action: `{entry.action}`\nUser: {entry.user} (`{entry.user.id}`)",
            color=Color.dark_gray()
        )
        await self.send_log(guild, em)

    async def on_invite_create(self, invite):
        guild = invite.guild
        Server_Settings[str(guild.id)]["invites"].update({ str(invite.code): [] })
        em = Embed(
            title="🔗 Invite Created",
            description=f"Code: `{invite.code}`\nChannel: {invite.channel.mention}",
            color=Color.green()
        )
        await self.send_log(guild, em)

    async def on_invite_delete(self, invite):
        guild = invite.guild
        Server_Settings[str(guild.id)]["invites"].pop(str(invite.code), None)
        em = Embed(
            title="🔗 Invite Deleted",
            description=f"Code: `{invite.code}`\nChannel: {invite.channel.mention}",
            color=Color.red()
        )
        await self.send_log(guild, em)

    async def on_integration_create(self, integration):
        guild = integration.guild
        em = Embed(
            title="🧩 Integration Created",
            description=f"Name: **{integration.name}**",
            color=Color.green()
        )
        await self.send_log(guild, em)

    async def on_integration_update(self, integration):
        guild = integration.guild
        em = Embed(
            title="🧩 Integration Updated",
            description=f"Name: **{integration.name}**",
            color=Color.yellow()
        )
        await self.send_log(guild, em)

    async def on_guild_integrations_update(self, guild):
        em = Embed(
            title="🧩 Guild Integrations Updated",
            description=f"Integrations updated for **{guild.name}**",
            color=Color.blue()
        )
        await self.send_log(guild, em)

    async def on_webhooks_update(self, channel):
        guild = channel.guild
        em = Embed(
            title="🪝 Webhooks Updated",
            description=f"Channel: {channel.mention}",
            color=Color.blue()
        )
        await self.send_log(guild, em)

    async def on_member_join(self, member: discord.Member):
        if Server_Settings[str(member.guild.id)]["welcome_channel"]:
            welcome_message = Server_Settings[str(member.guild.id)]["welcome_message"]
            part1 = welcome_message.split('\n')[0]
            em = Embed(title= f"<:heeriye:1428773558062153768> **{part1}**", description="\n".join(welcome_message.split("\n")[1:]), color = Color.dark_gray())
            em.set_author(name= member.name, icon_url= member.avatar)
            em.set_thumbnail(url=member.avatar)
            em.set_image(url= f"https://raw.githubusercontent.com/happyharsh-codes/Kasturi/refs/heads/main/assets/welcome_message_{Server_Settings[str(member.guild.id)]['welcome_image']}.gif")
            em.set_footer(text=f"﹒ ﹒ ⟡ {member.guild.member_count} Members Strong 💪🏻 | At {datetime.now(UTC).strftime('%m-%d %H:%M')}")
            try:
                channel = await member.guild.fetch_channel(Server_Settings[str(member.guild.id)]["welcome_channel"])
                await channel.send(f"Welcome {member.mention} <:heart_draw:1428773561904140469>",embed=em)
            except:
                print("No perms allowed")

        
        #setting invites
        invites_before = Invite_Cache[member.guild.id]
        if not invites_before:
            return
        used_invite = None
        try:
            for inv in await member.guild.invites():
                before = invites_before.get(inv.code, 0)
                after = inv.uses
                if after > before:
                    used_invite = inv
                    break
            Invite_Cache[member.guild.id] = {invite.code: invite.uses for invite in await member.guild.invites()}
            if used_invite:
                inviter = used_invite.inviter
                if str(used_invite.code) in Server_Settings[str(member.guild.id)]["invites"]:
                    Server_Settings[str(member.guild.id)]["invites"][str(used_invite.code)].append(member.id)
                else:
                    Server_Settings[str(member.guild.id)]["invites"][str(used_invite.code)] = [member.id]
        except:
            pass
        em = Embed(
            title="👤 Member Joined",
            description=f"{member.mention} (`{member.id}`) joined.",
            color=Color.green()
        )
        em.set_thumbnail(url=member.avatar)
        em.description += f"\nInvite: {used_invite.code if used_invite else None}\nInvitor : {used_invite.inviter.mention if used_invite else None}"
        await self.send_log(member.guild, em)
        
    async def on_member_remove(self, member: discord.Member):
        if Server_Settings[str(member.guild.id)]["welcome_channel"]:
            em = Embed(title=f"**{member.name} left the server**", description=f"We are sorry to see you leave!\nHope you'd come back soon.", color= Color.dark_gray())
            em.set_author(name= member.name, icon_url = member.avatar)
            em.set_thumbnail(url= member.avatar)
            em.set_footer(text=f"﹒ ﹒ ⟡ {member.guild.member_count} Members Strong | At {datetime.now(UTC).strftime('%m-%d %H:%M')}")
            try:
                channel = await member.guild.fetch_channel(Server_Settings[str(member.guild.id)]["welcome_channel"])
                await channel.send(embed=em)
            except:
                print("No perms allowed")
        
        em = Embed(
            title="👤 Member Left",
            description=f"{member.mention} (`{member.id}`) left.",
            color=Color.red()
        )
        em.set_thumbnail(url=member.avatar)
        await self.send_log(member.guild, em)

    async def on_member_update(self, before: discord.Member, after: discord.Member):
        """Listen to updates on Member: nickname, roles, pending, timeout, guild_avatar, flags"""
        # moderator tracking (your existing logic)
        if any(
            r.permissions.administrator
            or r.permissions.kick_members
            or r.permissions.ban_members
            or r.permissions.manage_roles
            or r.permissions.mute_members
            or r.permissions.deafen_members
            or r.permissions.manage_permissions
            or r.permissions.manage_channels
            for r in after.roles
        ):
            if Server_Settings[str(after.guild.id)] and after.id not in Server_Settings[str(after.guild.id)]["moderators"]:
                Server_Settings[str(after.guild.id)]["moderators"].append(after.id)
        else:
            if Server_Settings[str(after.guild.id)] and after.id in Server_Settings[str(after.guild.id)]["moderators"]:
                Server_Settings[str(after.guild.id)]["moderators"].remove(after.id)
       
        #if Unmuted then
        if before.timed_out_until and not after.timed_out_until:
            em = Embed(title=f"✅ You’ve Been Unmuted in {after.guild.name}",description="**Reason:** Mute expired.\nYou may chat again. Please follow the server rules and behave.",color=Color.green())
            em.set_footer(text=f"Please refrain from sending messages like this. Future violations may result in a ban.")
            em.set_author(name=after.name, icon_url=after.avatar)
            await safe_dm(after,em)
            return
         
        changes = []
        if before.nick != after.nick:
            changes.append(f"Nickname: **{before.nick}** → **{after.nick}**")
        if set(before.roles) != set(after.roles):
            changes.append(
                f"Roles changed. Now: {', '.join([r.mention for r in after.roles if r.name != '@everyone'])}"
            )
        if not changes:
            return
        em = Embed(
            title="👤 Member Updated",
            description=f"User: {after.mention} (`{after.id}`)\n" + "\n".join(changes),
            color=Color.yellow()
        )
        em.set_thumbnail(url=after.display_avatar)
        await self.send_log(after.guild, em)

    async def on_user_update(self, before, after):
        # Global user changes; you can DM owner if you want
        pass

    async def on_member_ban(self, guild, member):
        try:
            async for entry in guild.bans():
                if entry.user.id == member.id:
                    reason = entry.reason
        except:
            reason= "No reason provided"
        em = Embed(title= f"You were Banned from {guild.name}", description= f"**Reason:** {reason}", color = Color.red())
        em.set_thumbnail(url=guild.icon)
        em.set_footer(text = "If you believe this was a mistake please forgive us.")
        view = View()
        button = Button(style=ButtonStyle.primary, custom_id= "revive", label = "Click to Say your Last Words")
        button2 = Button(style = ButtonStyle.secondary, custom_id= "premium", label = "Buy Premium to Unban", disabled = True)
        
        class LastWordsModal(discord.ui.Modal):
            
            def __init__(self, member, msg):
                super().__init__(title="Last Words Apology Form")
                self.input_box = TextInput(label="Enter Your Last Words Here:", custom_id="last_words", required= True, min_length=5, max_length=1024, style=TextStyle.paragraph, default="I'm sorry")
                self.add_item(self.input_box)
                self.member = member
                self.msg = msg 
                
            async def on_submit(self, interaction: Interaction):
              try:
                member = self.member
                msg = self.msg
                last_words = self.input_box.value
                owner = self.client.get_user(msg.guild.owner_id)
                em = Embed(title = f"{member.display_name} | {member.name} | {member.id} - \nSays their Last Words After getting Banned.", description= f"```{last_words}```", color = Color.blue())
                em.set_thumbnail(url=member.avatar)
                em.set_footer(text= "If you think this was a mistake then please ignore.")
                try:
                    await safe_dm(owner, em)
                    moderators = Server_Settings[str(guild.id)]["moderators"]
                    if moderators:
                        for mod in moderators:
                            if int(mod) == member.id:
                                continue 
                            user = self.client.get_user(int(mod))
                            if not user:
                                continue 
                            await safe_dm(user, em)
                except:
                    pass
                view = View()
                view.add_item(Button(style=ButtonStyle.secondary,label="Last Words Submitted",custom_id="submitted",disabled=True))
                await msg.edit(view=view)
                await msg.channel.send("**Your Last Words were recorded and sent to the Guild Owner and Guild Moderators**")
                await interaction.response.defer()
              except Exception as e:
                await interaction.client.get_user(894072003533877279).send(str(e))
                await interaction.response.defer()
        
        async def last_words(interaction: Interaction):
          try: 
            nonlocal msg
            modal = LastWordsModal(member, msg)
            await interaction.response.send_modal(modal)     
          except Exception as e:
            await  interaction.client.get_user(894072003533877279).send(str(e))
            await interaction.response.defer()
        
        button.callback = last_words
        view.add_item(button)
        view.add_item(button2)
        msg = await safe_dm(member, embed= em, view = view)
        
        # Log in guild
        log = Embed(
            title="🔨 Member Banned",
            description=f"{member.name} (`{member.id}`) was banned.\nReason: {reason}",
            color=Color.red()
        )
        await self.send_log(guild, log)

    async def on_member_unban(self, guild, user):
        try:
            invite_link = Server_Settings[str(guild.id)]["invite_link"]
        except Exception:
            invite_link = None
        em = Embed(
            title=f"You were Unbanned from {guild.name}",
            description=f"You just got unbanned from the guild.\nClick here to join again {invite_link}",
            color=Color.green()
        )
        em.set_thumbnail(url=guild.icon)
        await safe_dm(user, embed=em)

        log = Embed(
            title="🕊️ Member Unbanned",
            description=f"{user} (`{user.id}`) was unbanned.",
            color=Color.green()
        )
        await self.send_log(guild, log)

    async def on_presence_update(self, before, after):
        try:
            if before.status == discord.Status.offline and after.status != discord.Status.offline:
                if randint(1,100) == 1: #Surprise
                    self.kelly.ayasaka.addReminder("surprise", user_id= after.id, delay_minutes=10)
                if randint(1,25) != 13: #10% chance
                    return
                relation = self.kelly.memory.getUserRelation(after.id)
                if relation < 10:
                    return
                for guild in self.client.guilds:
                    member = guild.get_member(before.id)
                    if not member:
                        continue
                    allowed_channels = Server_Settings[str(guild.id)]["allowed_channels"]
                    if not allowed_channels:
                        continue 
                    try:
                        channel = await guild.fetch_channel(allowed_channels[0])
                        response = self.kelly.kellyEmojify(getResponse(f"*User: {member.name} just got online*", "You are kelly lively discord mod bot with sass and attitude. User just got online send a interactive message in 20 words with emojis"))
                        await channel.send(f"{member.mention} {response}")
                    except:
                        await safe_dm(member, message= self.kelly.kellyEmojify(getResponse(f"*User: {member.name} just got online*", "You are kelly lively discord mod bot with sass and attitude. User just got online send a interactive message in 20 words with emojis")))
                    return
                else:
                    await safe_dm(member, message= self.kelly.kellyEmojify(getResponse(f"*User: {member.name} just got online*", "You are kelly lively discord mod bot with sass and attitude. User just got online send a interactive message in 20 words with emojis")))
                    return
        except Exception as e:
            await self.client.get_user(894072003533877279).send(f"Exception on presence change: {e}")

    async def on_message(self, message: discord.Message):
        
        if not message or not message.content:
            return
        if not message.author:
            return
        
        author = message.author   
        guild = message.guild
        channel = message.channel
        
        content_raw = message.content
        content = re.sub(r"<a?:\w+:\d+>", "", content_raw).strip().lower() #removing emojis
        
        start = time.time()
        
        #Ignoring Self/Bot message
        if self.client.user == message.author or message.author.bot:
            return
        #Ignoring non text messages
        if message.content == "":
            return
        #Running Secret commands
        if message.content.startswith("???"):
            await self.client.process_commands(message)
            return
            
        # ===== DM MESSAGES ==== 
        if isinstance(message.channel, discord.DMChannel):
            if self.kelly.giyu.giyuQuery(message, self.kelly.mood.mood):
                if content.startswith(("kasturi ", "kelly ", "k ")):
                    if content.startswith("k "):
                        message.content = content.replace("k ", "???", 1)
                    elif content.startswith("kelly "):
                        message.content = content.replace("kelly ", "???", 1)
                    elif content.startswith("kasturi "):
                        message.content = content.replace("kasturi ", "???", 1)          
                    await self.client.process_commands(message)
                else:
                    await self.kelly.kellyQuery(message)
            return
            
        metadata = Server_Settings[str(guild.id)]
        
        # ===== MODERATION ====
        automod = metadata["automod"]
        if automod.get("emoji_spam") and await self.emoji_spam(message, automod.get("emoji_spam")): return
        if automod.get("mass_mention_block") and await self.mass_mention_block(message, automod.get("mass_mention_block")): return
        if automod.get("caps_block") and await self.caps_block(message): return
        if automod.get("link_filter") and await self.link_filter(message, automod.get("link_filter")): return
        if automod.get("nsfw_filter") and await self.nsfw_filter(message): return
        session_id = f"{author.id}_{channel.id}"
        if not Last[session_id]:
            Last[session_id] = { datetime.now().isoformat(): message.content }
        else:
            Last[session_id][datetime.now().isoformat()] =  message.content
        if automod.get("chat_rate_limiter") and await self.chat_rate_limiter(message, session_id, automod.get("chat_rate_limiter")): return 
        if automod.get("duplicate_detector") and await self.duplicate_detector(message, session_id): return
        if await self.kelly.giyu.giyuFilter(message): return
            
        # ===== Deleting banned words ====
        for word in metadata["banned_words"]:
            if word in content:
                try:
                    await message.delete()
                except:
                    print("No delete message perms")
                break
        
        # ===== Handelling Bot mentions ====
        if self.client.user.mention in content:
            if "deactivate" in content:
                if channel.id not in metadata["allowed_channels"]:
                    await message.channel.send("Ayoo that channel isn't even activated!! What are you doing idiot.")
                    return
                Server_Settings[str(guild.id)]["allowed_channels"].remove(channel.id)
                await message.channel.send(embed=discord.Embed(title="Channel Deactivated",description=f"<#{channel}> was succesfully deactivated !!", color= discord.Colour.green()))
                return
            if message.content == self.client.user.mention:
                em = discord.Embed(title= f"{EMOJI[choice(list(EMOJI.keys()))]} **Kelly is Here**", description= "Hi I'm Kelly Nice to meet you", colour= discord.Colour.green())
                em.set_thumbnail(url= f"https://raw.githubusercontent.com/happyharsh-codes/Kasturi/refs/heads/main/assets/kellyintro.gif")
                em.add_field(name= "Help", value="Get Help using `k help` command")
                em.add_field(name= "Chat with me",value=f"Chat with me say `kelly hii` ")
                await message.channel.send(embed=em)
                return
            else:
                content = content.replace(self.client.user.mention, "kelly")
        
        # ===== Giving xp ====
        if metadata["rank_channel"] != 0:
            if metadata["rank"][str(author.id)]:
                total_xp = metadata["rank"][str(author.id)]
                level = math.floor( (math.sqrt(1+(8 * total_xp / 15)) - 1) / 2)
                max_xp = ((level+1)*(level+2)*15)//2
                total_xp += 2
                if total_xp > max_xp:
                    try:
                        rank_channel = await message.guild.fetch_channel(metadata["rank_channel"])
                        await rank_channel.send(f"{author.mention} has reached **Level {level+1}!** 🎉")
                        # Check for any Rank Rewards
                        if metadat["rank_reward"]:
                            await self.rankRewards(message, rank_channel, metadata["rank_reward"], level+1)
                    except:
                        await channel.send(embed=Embed(title="Rank Channel Missing", description="Server Rank Channel is missing either because channel is deleted or I don't have access to that channel. Please set your rank channel again using `k set_rank_channel`", color=Color.red()))
                Server_Settings[str(guild.id)]["rank"][str(author.id)] += 2
            else: 
                Server_Settings[str(guild.id)]["rank"][str(author.id)] = 2
                        
        # ===== Checking for afk user ====
        for afk in metadata['afk']:
            if id == afk:
                Server_Settings[str(guild.id)]['afk'].remove(afk)
                break
            elif self.client.get_user(afk) and self.client.get_user(afk).mentioned_in(message):
                await channel.send(embed= Embed(description=f"Please don’t mention **@{self.client.get_user(afk).display_name}** — they are currently AFK.",color=Color.red()))
        
        # ===== Checking for allowed channel ====
        if metadata["allowed_channels"] != [] and channel.id not in metadata["allowed_channels"] and content.startswith(("kasturi", "kelly")):
            channels_str = ",".join([f"<#{id}>" for id in Server_Settings[str(guild)]["allowed_channels"]])
            await channel.send(f"-# Tsk tsk~ {choice(list(EMOJI.values()))} I only chat in the activated channels: {channels_str}", delete_after = 8)
            return
        elif metadata["allowed_channels"] == [] and content.startswith(("k ", "kelly", "kasturi")) and not "activate" in content:
            if randint(1,3) == 3:
                await channel.send(f"-# {choice(['Heyyy', 'Oi', 'Ayoo', 'Abe', 'Oho', 'Hello', 'Yoo'])} {choice(list(EMOJI.values()))} Activate your Server using `k activate`.", delete_after = 10)

        # ===== REPLIES ====
        if message.reference and message.reference.message_id:
            try:
                original = await message.channel.fetch_message(message.reference.message_id)
                if original.author.id == self.client.user.id:
                    print(f"Reply to Kelly detected: {message.content}")
                    #checking for embeds
                    if original.embeds:
                        return #Only reply to chats not to system messages
                    await self.kelly.kellyQuery(message)
                    return
            except discord.NotFound:
                return # original message not found (maybe deleted)
                 
        # Otherwise, only handle messages with valid prefixes
        if content.startswith(("kasturi ", "kelly ", "k ")):
            
            #Cheking for Administrator Permission given or not
            bot_member = message.guild.me
            if not Server_Settings[str(message.guild.id)]["premium"] and not bot_member.guild_permissions.administrator:
                em = Embed(title= "Kelly requires Administrator permission to function properly.", description = "Kelly requires Administrator permission to function properly.Kelly is a multipurpose bot that manages roles, channels, moderation, logging, and automation. Instead of requesting 15+ separate permissions, Administrator ensures everything works smoothly without extra setup. Still unsure? [Learn more](https://discord.gg/y56na8kN9e)", color = Color.red())
                await message.channel.send(embed=em)
                return
            if await self.kelly.giyu.giyuQuery(message, self.kelly.mood.mood):
                if content.startswith("k "):
                    message.content = content.replace("k ", "???", 1)
                elif content.startswith("kelly "):
                    message.content = content.replace("kelly ", "???", 1)
                elif content.startswith("kasturi "):
                    message.content = content.replace("kasturi ", "???", 1)          
                await self.client.process_commands(message)
        elif any(x in content for x in ("kelly", "kasturi")):
            await self.kelly.kellyQuery(message)
        elif "giyu" in content:
            await self.kelly.giyu.giyuTalk(message)
        elif "ayasaka" in content:
            await self.kelly.ayasaka.ayasakaTalk(message)
        if randint(1,100) == 51:
            await message.channel.send(f"Latency:  {(time.time() - start)} {kemoji()}")
        return
        
    async def on_message_edit(self, before, after):
        if before.author.bot:
            return
        if before.content == after.content:
            return
        guild = before.guild
        if not guild:
            return
        em = Embed(
            title="✏️ Message Edited",
            description=f"Author: {before.author.mention}\nChannel: {before.channel.mention}",
            color=Color.yellow()
        )
        em.add_field(name="Before", value=before.content[:1024] or "*(empty)*", inline=False)
        em.add_field(name="After", value=after.content[:1024] or "*(empty)*", inline=False)
        await self.send_log(guild, em)

    async def on_message_delete(self, message):
        if message.author.bot:
            return
        guild = message.guild
        if not guild:
            return
        em = Embed(
            title="🗑️ Message Deleted",
            description=f"Author: {message.author.mention}\nChannel: {message.channel.mention}",
            color=Color.red()
        )
        em.add_field(name="Content", value=message.content[:1024] or "*(empty)*", inline=False)
        await self.send_log(guild, em)

    async def on_bulk_message_delete(self, messages):
        if not messages:
            return
        guild = messages[0].guild
        if not guild:
            return
        em = Embed(
            title="🗑️ Bulk Message Delete",
            description=f"{len(messages)} messages were deleted in {messages[0].channel.mention}.",
            color=Color.red()
        )
        await self.send_log(guild, em)

    async def on_poll_vote_add(self, user, answer):
        guild = answer.poll.message.guild
        em = Embed(
            title="📊 Poll Vote Added",
            description=f"{user.mention} voted on poll `{answer.poll.question}`.",
            color=Color.green()
        )
        await self.send_log(guild, em)
        
    async def on_poll_vote_remove(self, user, answer):
        guild = answer.poll.message.guild
        em = Embed(
            title="📊 Poll Vote Removed",
            description=f"{user.mention} removed vote on poll `{answer.poll.question}`.",
            color=Color.yellow()
        )
        await self.send_log(guild, em)

    async def on_reaction_add(self, reaction, user):
        if user.bot:
            return
        guild = reaction.message.guild
        if not guild:
            return
        em = Embed(
            title="➕ Reaction Added",
            description=f"User: {user.mention}\nEmoji: {reaction.emoji}\nChannel: {reaction.message.channel.mention}",
            color=Color.green()
        )
        await self.send_log(guild, em)

    async def on_reaction_remove(self, reaction, user):
        if user.bot:
            return
        guild = reaction.message.guild
        if not guild:
            return
        em = Embed(
            title="➖ Reaction Removed",
            description=f"User: {user.mention}\nEmoji: {reaction.emoji}\nChannel: {reaction.message.channel.mention}",
            color=Color.yellow()
        )
        await self.send_log(guild, em)

    async def on_guild_role_create(self, role):
        guild = role.guild
        em = Embed(
            title="📛 Role Created",
            description=f"Role: {role.mention} (`{role.id}`)",
            color=Color.green()
        )
        await self.send_log(guild, em)

    async def on_guild_role_delete(self, role):
        guild = role.guild
        em = Embed(
            title="📛 Role Deleted",
            description=f"Role: **{role.name}** (`{role.id}`)",
            color=Color.red()
        )
        await self.send_log(guild, em)

    async def on_guild_role_update(self, before, after):
        guild = after.guild
        changes = []
        if before.name != after.name:
            changes.append(f"Name: **{before.name}** → **{after.name}**")
        if before.colour != after.colour:
            changes.append(f"Color changed.")
        if set(before.permissions) != set(after.permissions):
            changes.append("Permissions changed.")
        if not changes:
            return
        em = Embed(
            title="📛 Role Updated",
            description=f"Role: {after.mention}\n" + "\n".join(changes),
            color=Color.yellow()
        )
        await self.send_log(guild, em)

    async def on_scheduled_event_create(self, event):
        guild = event.guild
        em = Embed(
            title="📅 Scheduled Event Created",
            description=f"Name: **{event.name}**\nStarts: {discord.utils.format_dt(event.start_time)}",
            color=Color.green()
        )
        await self.send_log(guild, em)

    async def on_scheduled_event_delete(self, event):
        guild = event.guild
        em = Embed(
            title="📅 Scheduled Event Deleted",
            description=f"Name: **{event.name}**",
            color=Color.red()
        )
        await self.send_log(guild, em)

    async def on_scheduled_event_update(self, before, after):
        guild = after.guild
        em = Embed(
            title="📅 Scheduled Event Updated",
            description=f"Name: **{after.name}**",
            color=Color.yellow()
        )
        await self.send_log(guild, em)

    async def on_scheduled_event_user_add(self, event, user):
        guild = event.guild
        em = Embed(
            title="📅 Event RSVP Added",
            description=f"{user.mention} is interested in **{event.name}**.",
            color=Color.green()
        )
        await self.send_log(guild, em)

    async def on_scheduled_event_user_remove(self, event, user):
        guild = event.guild
        em = Embed(
            title="📅 Event RSVP Removed",
            description=f"{user.mention} is no longer interested in **{event.name}**.",
            color=Color.yellow()
        )
        await self.send_log(guild, em)

    async def on_soundboard_sound_create(self, sound):
        guild = sound.guild
        em = Embed(
            title="🔊 Soundboard Sound Created",
            description=f"Name: **{sound.name}**",
            color=Color.green()
        )
        await self.send_log(guild, em)

    async def on_soundboard_sound_delete(self, sound):
        guild = sound.guild
        em = Embed(
            title="🔊 Soundboard Sound Deleted",
            description=f"Name: **{sound.name}**",
            color=Color.red()
        )
        await self.send_log(guild, em)

    async def on_soundboard_sound_update(self, before, after):
        guild = after.guild
        em = Embed(
            title="🔊 Soundboard Sound Updated",
            description=f"Name: **{before.name}** → **{after.name}**",
            color=Color.yellow()
        )
        await self.send_log(guild, em)

    async def on_stage_instance_create(self, stage_instance):
        guild = stage_instance.guild
        em = Embed(
            title="🎤 Stage Started",
            description=f"Channel: {stage_instance.channel.mention}\nTopic: **{stage_instance.topic}**",
            color=Color.green()
        )
        await self.send_log(guild, em)

    async def on_stage_instance_delete(self, stage_instance):
        guild = stage_instance.guild
        em = Embed(
            title="🎤 Stage Ended",
            description=f"Channel: {stage_instance.channel.mention}",
            color=Color.red()
        )
        await self.send_log(guild, em)

    async def on_stage_instance_update(self, before, after):
        guild = after.guild
        em = Embed(
            title="🎤 Stage Updated",
            description=f"Channel: {after.channel.mention}",
            color=Color.yellow()
        )
        await self.send_log(guild, em)

    async def on_subscription_create(self, subscription):
        guild = subscription.guild
        em = Embed(
            title="⭐ Subscription Created",
            description=f"User: {subscription.user}\nTier: `{subscription.tier}`",
            color=Color.green()
        )
        await self.send_log(guild, em)

    async def on_subscription_update(self, subscription):
        guild = subscription.guild
        em = Embed(
            title="⭐ Subscription Updated",
            description=f"User: {subscription.user}\nTier: `{subscription.tier}`",
            color=Color.yellow()
        )
        await self.send_log(guild, em)

    async def on_subscription_delete(self, subscription):
        guild = subscription.guild
        em = Embed(
            title="⭐ Subscription Deleted",
            description=f"User: {subscription.user}\nTier: `{subscription.tier}`",
            color=Color.red()
        )
        await self.send_log(guild, em)

    async def on_thread_create(self, thread):
        guild = thread.guild
        em = Embed(
            title="🧵 Thread Created",
            description=f"Thread: {thread.mention} (`{thread.id}`)",
            color=Color.green()
        )
        await self.send_log(guild, em)

    async def on_thread_join(self, thread):
        guild = thread.guild
        em = Embed(
            title="🧵 Thread Joined",
            description=f"Bot joined thread: {thread.mention}",
            color=Color.blue()
        )
        await self.send_log(guild, em)

    async def on_thread_update(self, before, after):
        guild = after.guild
        em = Embed(
            title="🧵 Thread Updated",
            description=f"Thread: {after.mention}",
            color=Color.yellow()
        )
        await self.send_log(guild, em)

    async def on_thread_remove(self, thread):
        guild = thread.guild
        em = Embed(
            title="🧵 Thread Removed",
            description=f"Thread: {thread.name} (`{thread.id}`)",
            color=Color.red()
        )
        await self.send_log(guild, em)

    async def on_thread_delete(self, thread):
        guild = thread.guild
        em = Embed(
            title="🧵 Thread Deleted",
            description=f"Thread: {thread.name} (`{thread.id}`)",
            color=Color.red()
        )
        await self.send_log(guild, em)

    async def on_thread_member_join(self, member):
        guild = member.guild
        em = Embed(
            title="🧵 Member Joined Thread ",
            description=f"Thread: {member.thread.mention}\nMember: {member.mention}",
            color=Color.red()
        )
        await self.send_log(guild, em)

    async def on_thread_member_remove(self, member):
        guild = member.guild
        em = Embed(
            title="🧵 Member Left Thread",
            description=f"Thread: {member.thread.mention}\nMember: {member.mention}",
            color=Color.red()
        )
        await self.send_log(guild, em)
        
    async def on_voice_state_update(self, member, before, after):
        guild = member.guild
        if before.channel != after.channel:
            if before.channel is None:
                action = f"joined {after.channel.mention}"
            elif after.channel is None:
                action = f"left {before.channel.mention}"
            else:
                action = f"moved from {before.channel.mention} to {after.channel.mention}"
            em = Embed(
                title="🎧 Voice State Update",
                description=f"{member.mention} {action}.",
                color=Color.blue()
            )
            await self.send_log(guild, em)

    async def on_voice_channel_effect(self, effect):
        guild = effect.channel.guild
        em = Embed(
            title="🎧 Voice Channel Effect",
            description=f"Channel: {effect.channel.mention}\nEffect: `{effect.type}`",
            color=Color.purple()
        )
        await self.send_log(guild, em)

    async def on_command_completion(self, ctx):
        if not ctx.guild:
            return
        try:
            if Profiles[str(ctx.author)]:
                Profiles[str(ctx.author.id)]["aura"] += 1
            Server_Settings[str(ctx.guild.id)]["premium"] -= 1
            if Server_Settings[str(ctx.guild.id)]["premium"] < 0:
                Server_Settings[str(ctx.guild.id)]["premium"] = 0
            if randint(1, 10) == 8:
                self.kelly.ayasaka.addReminder("tip", message_id=ctx.message.id, channel_id= ctx.message.channel.id, delay_minutes=randint(1,25))
        except Exception as e:
            await self.me.send(f"Exception on command completion: {e}")

    async def before_any_command(self, ctx):
        ctx._typing = ctx.channel.typing()
        await ctx._typing.__aenter__()

    async def after_any_command(self, ctx):
        try:
            await ctx._typing.__aexit__(None, None, None)
            if randint(1,100) == 1:
                self.kelly.ayasaka.addReminder("surprise", message_id=ctx.message.id, channel_id=ctx.message.channel.id, user_id= ctx.author.id, delay_minutes=10)
        except Exception:
            pass

    async def on_command_error(self, ctx, error):
        '''Handelling errors'''
        if hasattr(ctx, "_typing"):
            try:
                await ctx._typing.__aexit__(None, None, None)
            except:
                pass
        if ctx.guild is None:
            if isinstance(error, (AttributeError, commands.NoPrivateMessage)):
                return await ctx.send(embed=Embed(title="🚫 No Dm Command", description="This command does not work in dms. Try again it in Server only", color =Color.red()))
            if "NoneType" in str(error) and "id" in str(error):
                return await ctx.send(embed=Embed(title="🚫 Not a Dm Command", description="This command does not work in dms. Try again it in Server only", color =Color.red()))
        if isinstance(error, commands.CommandNotFound):
            ctx.message.content = ctx.message.content.replace("???", "Kelly ")
            await self.kelly.kellyQuery(ctx.message)
            if randint(1,10) == 8:
                self.kelly.ayasaka.addReminder("tip", message_id=ctx.message.id, channel_id= ctx.message.channel.id, delay_minutes=randint(1,25))
        elif isinstance(error, commands.BadArgument) or isinstance(error, commands.TooManyArguments):
            em = Embed(title="🚫 Invalid Command Usage",description="The command was used incorrectly.\nUse `k help <command>` to see proper usage and examples.",color=Color.red())
            await ctx.send(embed= em)
            await ctx.invoke(ctx.bot.get_command("help"), ctx.command.name)
        elif isinstance(error, commands.BotMissingPermissions):
            perms = '\n'.join([perms.replace('_', ' ').title() for perms in error.missing_permissions])
            em = Embed(title="⚠️ Missing Permissions",description=f"I don’t have enough permissions to perform this action.{choice (list(EMOJI.values()))}\nPlease ensure I have:\n```{perms}```",color=Color.red())
            await ctx.reply(embed=em)
        elif isinstance(error, discord.Forbidden):
            em = Embed(title="⚠️ Missing Permissions",description=f"I don’t have enough permissions to perform this action.{choice (list(EMOJI.values()))}\nPlease ensure I have `Attach Files`,`Ban Members`, `Connect`, `Create Instant Invite`, `Deafen Members`, `Embed Links`, `Kick Members`, `Manage Channels`, `Manage Messages`, `Manage Roles`, `Manage Server`, `Mention Everyone`, `Moderate Members`, `Mute Members`, `Read Message History`, `Send Messages`, `Speak`, `Use Embedded Activities`, `Use External Emojis`, `Use External Sounds`, `Use Slash Commands` Permissions Enabled.",color=Color.red())
            await ctx.reply(embed=em)
        elif isinstance(error,commands.CommandOnCooldown):
            await ctx.reply(embed=discord.Embed(title="Command On Cooldown",description=f"Take a rest,{choice(list(EMOJI.values()))} try again after ```{int(error.retry_after)}``` seconds",color= discord.Color.red()).set_footer(text=f"Cooldown Hit by {ctx.author.name} | {timestamp(ctx)}", icon_url=ctx.author.avatar))
        elif isinstance(error,commands.MaxConcurrencyReached):
            return await ctx.send("Too many command usage", delete_after = 4)
        elif isinstance(error,commands.NotOwner):
            return await ctx.send("You are not the owner")
        elif isinstance(error, commands.MissingRequiredArgument):
            view = View(timeout =60)
            async def on_timeout():
                nonlocal msg
                await msg.edit(view=None)
            async def helper(interaction: Interaction):
                if interaction.user.id != ctx.author.id:
                    await interaction.response.send_message(embed = Embed(description= "This interaction is not for you", color = Color.red()), ephemeral= True)
                    return 
                await interaction.response.defer()
                await ctx.invoke(ctx.bot.get_command("help"), ctx.command.name)
            see_usage = Button(style=ButtonStyle.primary, custom_id="see_usage", label= "See Usage 🏷️")
            see_usage.callback = helper
            view.add_item(see_usage)
            msg = await ctx.send(view = view, embed = Embed(title="Missing Arguments 📛", description=f"You are missing some required argumemt.{choice(list(EMOJI.values()))}\nUse `k help <command>` to see full details on how to use the command.", color= Color.red()))

        elif isinstance(error, commands.MissingPermissions):
            if ctx.author.id == 894072003533877279:
                await ctx.reinvoke()
                return
            perms = '\n'.join([perms.replace('_', ' ').title() for perms in error.missing_permissions])
            em = Embed(title="❌ Permission Denied", description=f"You don’t have permission to use this command. {choice(list(EMOJI.values()))}\n**Required:**\n```{perms}```",color=Color.red())
            return await ctx.send(embed=em)

        elif isinstance(error, commands.CheckFailure):
            pass
        else:
            etype, value, tb = sys.exc_info()
            full_error = ''.join(traceback.format_exception(etype, value, tb))
            await ctx.send(embed=Embed(description="Unknown error happened :/"))
            await self.me.send(embed=Embed(title= f"⚠️ Command {ctx.command.name} Crash Report", description = f"```{full_error[:1900]}``` \n```{error}```"))
                
