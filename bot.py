from __init__ import *

class Bot:

    def __init__(self, client, kelly):
        self.client = client
        self.kelly = kelly
        self.last_request = datetime.now()

    # ------------- INTERNAL HELPERS -------------

    async def get_log_channel(self, guild: Guild):
        """Return the logging channel for this guild or None if disabled/not set."""
        data = Server_Settings.get(str(guild.id))
        if not data:
            return None
        logging = data.get("logging")
        if not logging:
            return
        try:
            channel = await guild.fetch_channel(logging)
            if isinstance(channel, discord.TextChannel):
                return channel
        except Exception:
            return None
        return None

    async def send_log(self, guild: Guild, embed: discord.Embed):
        """Send an embed to the guild's log channel if logging is enabled."""
        channel = await self.get_log_channel(guild)
        if not channel:
            return
        try:
            await channel.send(embed=embed)
        except Exception:
            pass

    # ------------- TASK LOOPS -------------

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
                            title="✅ You’ve Been Unmuted",
                            description="**Reason:** Mute expired.\nYou may chat again. Please follow the server rules and behave.",
                            color=Color.green()
                        )
                        em.set_footer(text="Please refrain from sending messages like this. Future violations may result in a ban.")
                        em.set_author(name=user.name, icon_url=user.avatar)
                        await safe_dm(user,em)
                    except Exception as dm_error:
                        print(f"Could not DM {muted_id}: {dm_error}")

    @tasks.loop(minutes=2)
    async def mood_swings(self):
        try:
            mood = self.kelly.mood.moodSwing()
            action_text = None
            message = None

            if mood:
                prev_mood = mood[1]
                new_mood = mood[0]
                special_lines = {
                    "angry": "Kelly is fuming right now 🔥 with anger (mood change = angry)",
                    "sad": "Kelly feels a bit emotional 💔 so sad (mood change = sad)",
                    "mischievous": "Kelly is up to something suspicious 😼 (mood change = mischievous)",
                    "busy": "Kelly is too busy for your nonsense ⏳ (mood change = busy)",
                    "lazy": "Kelly is too lazy to even get her ass up right now (mood change = lazy)",
                    "depressed": "Kelly is so depressed needs someone to comfort her (mood change = depressed)"
                }
                action = {
                    "sleepy": "-# Kelly is sleeping 😴",
                    "depressed": "-# Kelly is depressed 😔",
                    "angry": "-# Kelly is angry 😡",
                    "busy": "-# Kelly has gone busy",
                    "lazy": "-# Kelly is too lazy to respond now 😪",
                    "sad": "-# Kelly is so sad right now 😭",
                    "mischievous": "-# Kelly is feeling a little mischievous 😉",
                    "annoyed": "-# Kelly is so annoyed now 😒"
                }
                text = special_lines.get(new_mood, f"Kelly just got a mood change to **{new_mood}**")
                action_text = self.kelly.getEmoji(action.get(new_mood, f"-# Kelly just got {new_mood}"))
                if new_mood == "happy" and prev_mood == "sleepy":
                    text = "Kelly just woke up from her deep slumber (mood change = woke up)"
                prompt = (
                    "Roleplay Kelly, a cute Discord Mod (human like with mood and sass)."
                    "Generate response telling all audience kelly went this mood change in 20 words with 1-5 emojis"
                )
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(None, getResponse, text, prompt, "", 0)
                message = self.kelly.getEmoji(response)

            for gid, settings in Server_Settings.items():
                try:
                    guild = await self.client.fetch_guild(int(gid))
                except Exception:
                    continue

                if settings["allowed_channels"]:
                    for channel_id in settings["allowed_channels"]:
                        try:
                            channel = await guild.fetch_channel(int(channel_id))
                            if mood:
                                await channel.send(action_text)
                                await channel.send(message, delete_after=120)
                            elif randint(1, 10) == 7 and settings["timer_messages"]:
                                text = "Kelly got to revive the ded chat"
                                prompt = (
                                    "Roleplay Kelly, a cute Discord Mod (human like with mood and sass)."
                                    "Generate response activating ded chat in 20 words with 1-4 emojis"
                                )
                                loop = asyncio.get_event_loop()
                                response = await loop.run_in_executor(None, getResponse, text, prompt, "", 0)
                                await channel.send(self.kelly.getEmoji(response))
                        except Exception as e:
                            await self.client.get_user(894072003533877279).send(f"Exception on Mood change: {e}")
                else:
                    for channel in guild.text_channels:
                        if channel.last_message and mood:
                            await channel.send(action_text)
                            await channel.send(message, delete_after=120)
        except Exception as e:
            await self.client.get_user(894072003533877279).send(f"Exception on Mood change: {e}")

    # ------------- EVENTS -------------

    async def on_automode_rule_create(self, rule):
        guild = rule.guild
        em = Embed(
            title="🛡️ AutoMod Rule Created",
            description=f"Rule: **{rule.name}**\nID: `{rule.id}`",
            color=Color.green()
        )
        await self.send_log(guild, em)

    async def on_automode_rule_update(self, rule):
        guild = rule.guild
        em = Embed(
            title="🛡️ AutoMod Rule Updated",
            description=f"Rule: **{rule.name}**\nID: `{rule.id}`",
            color=Color.yellow()
        )
        await self.send_log(guild, em)

    async def on_automode_rule_delete(self, rule):
        guild = rule.guild
        em = Embed(
            title="🛡️ AutoMod Rule Deleted",
            description=f"Rule: **{rule.name}**\nID: `{rule.id}`",
            color=Color.red()
        )
        await self.send_log(guild, em)

    async def on_automode_action(self, execution):
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

    async def on_error(self, event_method):
        print(f"Error in event: {event_method}")
        try:
            await self.client.get_user(894072003533877279).send(
                embed=Embed(
                    title="Error in event",
                    description=f"```{event_method}```",
                    color=Color.red()
                )
            )
        except Exception:
            pass

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
        self.save_files.start()
        self.unmute.start()

        # saving guilds
        for guild in self.client.guilds:
            invite_link = None
            embed = Embed(
                title="✅ Kelly Updated",
                description="Kelly has been updated successfully and is running on the latest version 💫",
                color=Color.green()
            )
            embed.set_footer(text="Kelly System", icon_url=self.client.user.avatar)
            embed.timestamp = datetime.utcnow()
            for channel in guild.text_channels:
                try:
                    invite = await channel.create_invite(max_age=0, max_uses=0)  # infinite invite
                    invite_link = str(invite)
                    await channel.send(embed=embed)
                    break
                except Exception:
                    continue

            if str(guild.id) not in Server_Settings:
                moderators = []
                for member in guild.members:
                    if any(
                        r.permissions.administrator
                        or r.permissions.kick_members
                        or r.permissions.ban_members
                        or r.permissions.manage_roles
                        or r.permissions.mute_members
                        or r.permissions.deafen_members
                        or r.permissions.manage_permissions
                        or r.permissions.manage_channels
                        for r in member.roles
                    ):
                        moderators.append(member.id)
                Server_Settings[str(guild.id)] = {
                    "name": guild.name,
                    "allowed_channels": [],
                    "premium": False,
                    "invite_link": invite_link,
                    "owner": guild.owner_id,
                    "moderators": moderators,
                    "banned_words": [],
                    "block_list": [],
                    "muted": {},
                    "invites": {},
                    "rank": {},
                    "rank_channel": 0,
                    "rank_reward": {},
                    "join/leave_channel": 0,
                    "welcome_message": "",
                    "welcome_image": 1,
                    "social": {
                        "yt": None,
                        "insta": None,
                        "twitter": None,
                        "social_channel": 0
                    },
                    "timer_messages": False,
                    "afk": [],
                    "warn": {},
                    "warn_action": {},
                    "friends": [],
                    "logging": 0
                }

        # help / brief
        for cmd in self.client.commands:
            if not cmd.help and cmd.callback.__doc__:
                cmd.help = cmd.callback.__doc__.strip()

        for cmd_name, brief_text in DATA["brief"].items():
            cmd = self.client.get_command(cmd_name)
            if cmd:
                cmd.brief = brief_text

        # tracking invites
        for guild in self.client.guilds:
            self.invite_cache[guild.id] = {
                invite.code: invite.uses for invite in await guild.invites()
            }

        self.client.add_view(BugReportView())

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
        channels = guild.channels 
        invite = None
        kelly = Button(style = ButtonStyle.link, url = "https://discord.gg/y56na8kN9e", label = "Kelly's Homeland")
        developer = Button(style= ButtonStyle.link, url = "https://github.com/happyharsh-codes", label = "Developer")
        view = View()
        view.add_item(kelly)
        view.add_item(developer)
        em = discord.Embed(title = f"{EMOJI[choice(list(EMOJI.keys()))]} **Kelly has Arrived!**", description=f"Thanks for adding me!\n• Say `kelly hi` to talk\n• Use `k activate` to enable chat\n• Use `k help` to view commands\n• Found a bug? Use `k bug`",color = discord.Colour.green())
        em.set_image(url="https://raw.githubusercontent.com/happyharsh-codes/Kasturi/refs/heads/main/assets/welcome_setup.png")
        em.set_thumbnail(url= f"https://raw.githubusercontent.com/happyharsh-codes/Kasturi/refs/heads/main/assets/kellyintro.gif")
        em.set_footer(text=f"⟡ {len(self.client.guilds)} Guilds Strong 💪🏻 | At {datetime.now(UTC).strftime('%m-%d %H:%M')}")
                        
        for channel in channels:
            if isinstance(channel, discord.TextChannel):
                if "general" in channel.name.lower() or "chat" in channel.name.lower():
                    try:         
                        invite = await channel.create_invite(max_age=0, max_uses=0)
                        await channel.send("@everyone", embed= em, view=view)
                        break
                    except:
                        continue
        else:
            for channel in channels:
                if isinstance(channel, discord.TextChannel):
                    try:
                        invite = await channel.create_invite(max_age=0,max_uses=0)
                        await channel.send("@everyone", embed= em, view=view)
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
        Server_Settings[str(guild.id)] = {"name": guild.name,"allowed_channels": [],"premium": False,"invite_link": invite,"owner": guild.owner_id,"moderators": moderators,"banned_words": [],"block_list": [],"muted": {},"invites": {},"rank": {},"rank_channel": 0,"rank_reward": {},"join/leave_channel": 0,"welcome_message": "","welcome_image": 1,"social": {"yt": None,"insta": None,"twitter": None,"social_channel": 0},"timer_messages": False, "afk": [],"warn": {},"warn_action": {},"friends": [],"logging": 0}

    async def on_guild_remove(self, guild: discord.Guild):
        try:
            entry = await guild.audit_logs(limit=1,action=discord.AuditLogAction.bot_ban).flatten()
            if entry:
                moderator = entry[0].user
                em = Embed(title="I got banned",description=f"I got banned from {guild.name}\nAction taken by: {moderator.name} {moderator.id} {moderator.display_name}", color = Color.red())
                em.url = Server_Settings[str(ctx.guild.id)]["invite_link"]
                em.set_thumbnail(url = moderator.avatar)
                em.set_footer(text = "Banned by {moderator.name}", icon_url = moderator.avatar)
                await me.send(embed = em)
                for channel in guild.text_channels:
                    try:
                         await channel.send(f"👋 It seems I've been **banned** from this server.\nAction taken by: **{moderator}**\nFarewell everyone! 💖")
                    except:
                         continue
        except:
          try:
           async for ban in guild.bans():
               if ban.user.id == client.user.id:
                   em = Embed(title="I got banned",description=f"I got banned from {guild.name}\nAction taken by: {moderator.name} {moderator.id} {moderator.display_name}", color = Color.red())
                   em.url = Server_Settings[str(ctx.guild.id)]["invite_link"]
                   em.set_thumbnail(url = moderator.avatar)
                   em.set_image(url=guild.icon)
                   em.set_footer(text = "Banned by {moderator.name}", icon_url = moderator.avatar)
                   me = self.client.get_user(894072003533877279)
                   await me.send(embed = em)
          except:
            pass
            
        me = self.client.get_user(894072003533877279)
        await me.send(f"Left a server: {Server_Settings[str(guild.id)]['name']}\n{Server_Settings[str(guild.id)]['invite_link']}")
        Server_Settings.pop(str(guild.id), None)
        
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
        #setting invites
        invites_before = self.invite_cache[member.guild.id]
        used_invite = None
        for inv in await member.guild.invites():
            before = invites_before.get(inv.code, 0)
            after = inv.uses
            if after > before:
                used_invite = inv
                break
        self.invite_cache[member.guild.id] = {invite.code: invite.uses for invite in await member.guild.invites()}
        if used_invite:
            inviter = used_invite.inviter
            if str(used_invite.code) in Server_Settings[str(member.guild.id)]["invites"]:
                Server_Settings[str(member.guild.id)]["invites"][str(used_invite.code)].append(member.id)
            else:
                Server_Settings[str(member.guild.id)]["invites"][str(used_invite.code)] = [member.id]
            
        if Server_Settings[str(member.guild.id)]["join/leave_channel"]:
            welcome_message = Server_Settings[str(member.guild.id)]["welcome_message"]
            part1 = welcome_message.split('\n')[0]
            em = Embed(title= f"<:heeriye:1428773558062153768> **{part1}**", description="\n".join(welcome_message.split("\n")[1:]), color = Color.dark_gray())
            em.set_author(name= member.name, icon_url= member.avatar)
            em.set_thumbnail(url=member.avatar)
            em.set_image(url= f"https://raw.githubusercontent.com/happyharsh-codes/Kasturi/refs/heads/main/assets/welcome_message_{Server_Settings[str(member.guild.id)]['welcome_image']}.gif")
            em.set_footer(text=f"﹒ ﹒ ⟡ {member.guild.member_count} Members Strong 💪🏻 | At {datetime.now(UTC).strftime('%m-%d %H:%M')}")
            try:
                channel = await member.guild.fetch_channel(Server_Settings[str(member.guild.id)]["join/leave_channel"])
                await channel.send(f"Welcome {member.mention} <:heart_draw:1428773561904140469>",embed=em)
            except:
                print("No perms allowed")

        em = Embed(
            title="👤 Member Joined",
            description=f"{member.mention} (`{member.id}`) joined.",
            color=Color.green()
        )
        em.set_thumbnail(url=member.avatar)
        if used_invite:
            description += f"\nInvite: {used_invite.code}\nInvitor : {used_invite.inviter.mention}"
        await self.send_log(member.guild, em)

    async def on_member_remove(self, member: discord.Member):
        if Server_Settings[str(member.guild.id)]["join/leave_channel"]:
            em = Embed(title=f"**{member.name} left the server**", description=f"We are sorry to see you leave!\nHope you'd come back soon.", color= Color.dark_gray())
            em.set_author(name= member.name, icon_url = member.avatar)
            em.set_thumbnail(url= member.avatar)
            em.set_footer(text=f"﹒ ﹒ ⟡ {member.guild.member_count} Members Strong | At {datetime.now(UTC).strftime('%m-%d %H:%M')}")
            try:
                channel = await member.guild.fetch_channel(Server_Settings[str(member.guild.id)]["join/leave_channel"])
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
            if after.id not in Server_Settings[str(after.guild.id)]["moderators"]:
                Server_Settings[str(after.guild.id)]["moderators"].append(after.id)
        else:
            if after.id in Server_Settings[str(after.guild.id)]["moderators"]:
                Server_Settings[str(after.guild.id)]["moderators"].remove(after.id)
       
        #if Unmuted then
        if before.timed_out_until and not after.timed_out_until:
            em = Embed(title="✅ You’ve Been Unmuted in {after.guild.name}",description="**Reason:** Mute expired.\nYou may chat again. Please follow the server rules and behave.",color=Color.green())
            em.set_footer(text=f"Please refrain from sending messages like this. Future violations may result in a ban.")
            em.set_author(name=user.name, icon_url=user.avatar)
            await safe_dm(after,em)
         
        changes = []
        if before.nick != after.nick:
            changes.append(f"Nickname: **{before.nick}** → **{after.nick}**")
        if set(before.roles) != set(after.roles):
            changes.append(
                f"Roles changed. Now: {', '.join(r.mention for r in after.roles if r.name != '@everyone')}"
            )
        if not changes:
            return
        em = Embed(
            title="👤 Member Updated",
            description=f"User: {after.mention} (`{after.id}`)\n + \n".join(changes),
            color=Color.yellow()
        )
        em.set_thumbnail(url=after.guild_avatar)
        await self.send_log(after.guild, em)

    async def on_user_update(self, before, after):
        # Global user changes; you can DM owner if you want
        pass

    async def on_member_ban(self, guild, member):
        reason = "No reason provided."
        em = Embed(
            title=f"You were Banned from {guild.name}",
            description=f"**Reason:** {reason}",
            color=Color.red()
        )
        em.set_footer(text="If you believe this was a mistake please forgive us.")
        
        em = Embed(title= f"You were Banned from {guild.name}", description= f"**Reason:** {reason}", color = Color.red())
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
                owner = self.client.get_user(ctx.guild.owner_id)
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
                await self.clientget_user(894072003533877279).send(str(e))
                await interaction.response.defer()
        
        async def last_words(interaction: Interaction):
          try: 
            nonlocal msg
            modal = LastWordsModal(member, msg)
            await interaction.response.send_modal(modal)     
          except Exception as e:
            await self.clientget_user(894072003533877279).send(str(e))
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
            await self.client.get_user(894072003533877279).send(f"Exception on presence change: {e}")

    async def on_message(self, message: discord.Message):
        start = time.time()
        id = message.author.id
        guild = message.guild.id
        channel = message.channel.id
        metadata = Server_Settings[str(guild)]
        try:
            #Ignoring Self message
            if self.client.user == message.author or message.author.bot:
                return
            #ignoring non text messages
            if message.content == "":
                return
            #Deleting banned words
            for word in metadata["banned_words"]:
                if word in message.content:
                    try:
                        await message.delete()
                    except:
                        print("No delete message perms")
                    break
            #Handelling Bot mentions
            if self.client.user.mention in message.content:
                if "deactivate" in message.content.lower():
                    if channel not in metadata["allowed_channels"]:
                        await message.channel.send("Ayoo that channel isn't even activated!! What are you doing idiot.")
                        return
                    Server_Settings[str(guild)]["allowed_channels"].remove(channel)
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
                    message.content = message.content.replace(self.client.user.mention, "kelly")
            
            #Giving xp
            if metadata["rank_channel"] != 0:
                if str(id) in metadata["rank"]:
                    total_xp = metadata["rank"][str(id)]
                    level = (math.sqrt(1+8*(total_xp//15)) -1)//2
                    max_xp = ((level+1)*(level+2)*15)//2
                    total_xp += 2
                    if total_xp > max_xp:
                        channel = await message.guild.fetch_channel(metadata["rank_channel"])
                        await channel.send(f"{message.author.mention} has reached **Level {level+1}!** 🎉") 
                    Server_Settings[str(guild)]["rank"][str(id)] += 2
                else: 
                    Server_Settings[str(guild)]["rank"][str(id)] = 2

            #checking for afk user
            for afk in metadata['afk']:
                if id == afk:
                    Server_Settings[str(guild)]['afk'].remove(afk)
                elif self.client.get_user(afk).mentioned_in(message):
                    await message.channel.send(embed= Embed(description=f"Please don’t mention **@{self.client.get_user(afk).name}** — they are currently AFK.",color=Color.red()))
        
            #checking for allowed channel
            if metadata["allowed_channels"] != [] and channel not in metadata["allowed_channels"] and message.content.lower().startswith(("kasturi", "kelly")):
                channels_str = ",".join([f"<#{id}>" for id in Server_Settings[str(guild)]["allowed_channels"]])
                await message.channel.send(f"-# Tsk tsk~ {choice(list(EMOJI.values()))} I only chat in the activated channels: {channels_str}", delete_after = 8)
                return
            elif metadata["allowed_channels"] == [] and message.content.lower().startswith(("k ", "kelly", "kasturi")) and not "activate" in message.content:
                if randint(1,3) == 3:
                    await message.channel.send(f"-# {choice(['Heyyy', 'Oi', 'Ayoo', 'Abe', 'Oho'])} {choice(list(EMOJI.values()))} Activate your Server using `k activate` now")
            #replying to replies i.e messages without prefixes
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
            message.content = re.sub(r"<a?:\w+:\d+>", "", message.content).strip().lower() # removing emojis
            if not message.content.startswith(("kasturi", "kelly", "k")):
                if "kasturi" in message.content.lower() or "kelly" in message.content.lower():
                    #cheking for Administrator Permission given or not
                    '''bot_member = message.guild.me
                    if not bot_member.guild_permissions.administrator:
                        em = Embed(title= "Kelly requires Administrator permission to function properly.", description = "Kelly requires Administrator permission to function properly.Kelly is a multipurpose bot that manages roles, channels, moderation, logging, and automation. Instead of requesting 15+ separate permissions, Administrator ensures everything works smoothly without extra setup. Still unsure? [Learn more](https://discord.gg/y56na8kN9e)", color = Color.red())
                        await message.channel.send(embed=em)
                        return'''
                    await self.kelly.kellyQuery(message)
                return
            message.content = message.content.replace("kelly","").replace("kasturi","").strip()
            #cheking for Administrator Permission given or not
            '''bot_member = message.guild.me
            if not bot_member.guild_permissions.administrator:
                em = Embed(title= "Administrator Permission is Compulsory", description = "I need administrator permission to operate properly. This is beacause our bot is multipurpose and requries almost all kinds of permissions. Please grant me administrator permission. This is safe we do not intend to do anything malicious. If you are still not satisfied why we need this [Click Here](https://discord.gg/y56na8kN9e)", color = Color.red())
                await message.channel.send(embed=em)
                return'''
                
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
            import traceback
            traceback.print_exc()

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
        try:
            Profiles[ctx.author.id]["aura"] += 1
            if randint(1, 10) == 8:
                await ctx.send(choice(list(TIP.values())))
        except Exception:
            pass

    async def before_any_command(self, ctx):
        ctx._typing = ctx.channel.typing()
        await ctx._typing.__aenter__()

    async def after_any_command(self, ctx):
        try:
            await ctx._typing.__aexit__(None, None, None)
        except Exception:
            pass

    async def on_command_error(self, ctx, error):
        '''Handelling errors'''
        if hasattr(ctx, "_typing"):
            try:
                await ctx._typing.__aexit__(None, None, None)
            except:
                pass
        if isinstance(error, commands.CommandNotFound):
            ctx.message.content = ctx.message.content[3:]
            await self.kelly.kellyQuery(ctx.message)
            if ranint(1,10) == 8:
                await ctx.send(choice(list(TIP.values())))
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
            await ctx.send(embed=em)

        elif isinstance(error, commands.CheckFailure):
            pass
        else:
            await ctx.send(embed=Embed(description="Unknown error happened :/"))
            user = self.client.get_user(894072003533877279)
            if user != None:
                await user.send(embed=Embed(title= f"Crash report on command error", description = f"```{error}```"))
                
