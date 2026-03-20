from __init__ import*
from src.kellycore.kellymood import KellyMood
from src.kellycore.kellymemory import KellyMemory
from src.kellycore.giyu import Giyu
from src.kellycore.ayasaka import Ayasaka 

NUMBER_REGEX = re.compile(r"\b(\d+)\b")
REASON_REGEX = re.compile(r"(?:for|because|due to|reason[:\-]?)\s*(.+)",re.IGNORECASE)

class Kelly:
    """Main Kelly Core(Brain) - kellycore.py  
    Governs all activities:
        - Receives messages: -> if command run command else talk
        -   * Mood system - kellymood.py
            * Memory - kellymemory.py
            * Giyu - giyu.py
            * Ayasaka - ayasaka.py
        - Handles callbacks from KellyMemory(friend / ban)
        - Giyu guard, chat filters and protects Kelly when she sleeps
        - Ayasaka, assistant Manages busy-tasks via KellyBusy
        - Stores server & user data in memory systems
    """
    def __init__(self, name, bot):
        self.name = name
        self.client = bot #discord bot
        self.status = "happy"
        self.mood = KellyMood(bot, self)
        self.memory = KellyMemory()
        self.giyu = Giyu(bot, self)
        self.ayasaka = Ayasaka(self)
        self.mood.generateRandomMood()
        self.commands = {}

    def setStatus(self, status):
        self.status = status
        
    async def reportError(self, error):
        try:
            me = self.client.get_user(894072003533877279)
            etype, value, tb = sys.exc_info()
            full_error = ''.join(traceback.format_exception(etype, value, tb))
            em = Embed(title="🚫 Error on KellyCore", description=f"```{full_error[:1900]}```", color = Color.red())
            await me.send(embed=em)
        except:
            pass
        print("".join(traceback.format_exception(etype, value, tb)))

    def get_command_params(self, command, message, author=None):
        if not author:
            author = message.author
        params = {}
        content = message.content
        if "member" in command.clean_params:
            params["member"] = message.mentions[0] if message.mentions else author
        if "user" in command.clean_params:
            params["user"] = message.mentions[0] if message.mentions else author
        if "channel" in command.clean_params:
            params["channel"] = message.channel_mentions[0] if message.channel_mentions else message.channel
        if "role" in command.clean_params:
            params["role"] = message.role_mentions[0] if message.role_mentions else None
        for time_param in ("minutes", "seconds", "hours", "days"):
            if time_param not in command.clean_params:
                continue
            content = re.sub(r"<@!?\d+>", "", message.content)
            def extract(pattern, content):
                match = re.search(pattern, content, re.I)
                return int(match.group(1)) if match else 0
            days = extract(r"(\d+)\s*(d|day|days)", content)
            hours = extract(r"(\d+)\s*(h|hr|hrs|hour|hours)", content)
            minutes = extract(r"(\d+)\s*(m|min|mins|minute|minutes)", content)
            seconds = extract(r"(\d+)\s*(s|sec|secs|second|seconds)", content)
            total_seconds = seconds + (minutes*60) + (hours*3600) + (days*86400)
            if total_seconds == 0:
                num = re.search(r"\b(\d+)\b", content)
                total_seconds = int(num.group(1)) * 60 if num else 300
            total_minutes = total_seconds//60
            total_hours = total_seconds//3600
            total_days = total_seconds//86400
            if time_param == "days":
                params[time_param] = total_days
            elif time_param == "hours":
                params[time_param] = total_hours
            elif time_param == "minutes":
                params[time_param] = total_minutes
            elif time_param == "seconds":
                params[time_param] = total_seconds
            else:
                params[time_param] = 5
        
        if "reason" in command.clean_params:
            match = REASON_REGEX.search(content)
            if match:
                reason = match.group(1).strip()
            else:
                # fallback: strip mentions, numbers, command words
                reason = re.sub(r"<@!?\d+>", "", content)
                reason = re.sub(r"\b\d+\b", "", reason)
                reason = re.sub(r"\b(kelly|k|mute|ban|warn|kick|timeout)\b", "", reason, flags=re.I)
                reason = reason.strip()
            params["reason"] = reason if reason else "No reason provided"

        return params
                
    async def search_commands(self, message):
        start = time.time()
        if not self.commands:
            self.commands = {command.name: list(command.clean_params.keys()) for command in self.client.commands}
        prompt_command = f"""You are a Discord command classifier. Return ONLY JSON: {{ "command": "<name or null>" }}\nPick COMMAND from: {list(self.commands.keys())}\nReturn null unless the bot clearly agrees to perform or schedule an action. No params. No text. No guessing."""
        raw_result = getResponse(message, prompt_command)
        try:
            raw_result = raw_result.strip().lower()
            if raw_result.startswith("{"):
                result = loads(raw_result)
            if raw_result.startswith("```"):
                block = raw_result.split("```")[1]
                result = loads(block.replace("json",""))
            else:
                result = loads(raw_result)
        except Exception as parse_error:
             return
        command_name = result["command"]
        if not command_name:
            return
        if not self.commands[command_name]:
            return command_name, {}
        prompt = f"""You are extracting parameters for a Discord command.\nCommand name: {command_name}\nRequired parameters and types: {self.commands[command_name]}\nRules:\n- Output ONLY valid JSON\n- Use ONLY the listed parameters\n- Do NOT invent parameters\n- If a value is missing or unknown, set it to null\n- Do NOT guess Discord IDs\n- Do NOT add explanations\nOutput format:\n{{ "<param1>": <value1 or null> }}"""
        raw_result = getResponse(message, prompt)
        try:
            raw_result = raw_result.strip().lower()
            if raw_result.startswith("{"):
                params = loads(raw_result)
            if raw_result.startswith("```"):
                block = raw_result.split("```")[1]
                params = loads(block.replace("json",""))
            else:
                params = loads(raw_result)
        except Exception as parse_error:
             return
        print(f"search_commands Latency: {time.time() - start}")
        return (command_name, params)
    
    async def runCommand(self, message: discord.Message, cmd_name, params):
        try:
            cmd = self.client.get_command(cmd_name)
            ctx = await self.client.get_context(message)
            print(f"### Running command {cmd_name} with {params}")
            await ctx.invoke(cmd, **params)

        except Exception as e:
            await self.reportError(str(e))
            
    async def performTasks(self):
        if self.status in ("lazy", "sleepy", "mischievous", "sad"):
            return
        schedules = self.ayasaka.busy.getSchedules()
        for due_str, task in schedules.items():
            if datetime.fromisoformat(due_str) < datetime.now():
                channel = self.client.get_channel(task["channel"])
                if not channel:
                    try:
                        channel = await self.client.fetch_channel(task["channel"])
                    except:
                        del schedules[due_str]
                        self.status = "busy" if self.ayasaka.busy.isBusy() else "active"
                        return
                try:
                    message = await channel.fetch_message(task["message"])
                except:
                    del schedules[due_str]
                    self.status = "busy" if self.ayasaka.busy.isBusy() else "active"
                    return
                self.runCommand(message, task["command"], task["params"])
                del schedules[due_str]
                self.status = "busy" if self.ayasaka.busy.isBusy() else "active"
                return

    async def performReminders(self):
        if self.status in ("sleepy", "lazy", "mischievous"):
            return
        reminders = self.memory._memory["reminders"]
        for due_str, task in reminders.items():
            if datetime.fromisoformat(due_str) < datetime.now():
                if task["reminder"] == "surprise":
                    prompt = f"""Roleplay Kelly — sassy, human-like Discord mod with moods and personality.\nMood: {self.mood.mood}. Surprise user with something interesting. Generate responses in 10-30 words and 1-4 emojis."""
                    response = getResponse("", prompt, assistant= self.memory.getUserChats(task["user"], limit=4))
                elif task["reminder"] == "tip":
                    response = choice(TIP)
                if not task["channel"]:
                    user = self.client.get_user(task["user"])
                    await safe_dm(user, message=response)
                    del reminders[due_str]
                    return
                channel = self.client.get_channel(task["channel"])
                if not channel:
                    try:
                        channel = await self.client.fetch_channel(task["channel"])
                    except:
                        del reminders[due_str]
                        return
                try:
                    message = await channel.fetch_message(task["message"])
                except:
                    if task["user"]:
                        await channel.send(f"<@{task['user']}> {response}")
                    else:
                        await channel.send(response)
                    del reminders[due_str]
                    return
                await message.reply(response)
                del reminders[due_str]
                return
    async def kellyQuery(self, message: discord.Message):
        """
        Main handler for incoming user messages.
        Steps:
            1. Giyu Check - filter message, blocked, muted, agressive, kelly sleeping
            2. Ayasaka Check - kelly busy, kelly lazy, schedules overflow
            3. Kelly Reply
            4. Generate Message Result
                - Update relation (respect) based on message style.
                    - relation hits > 80: Kelly thinks of making friend
                    - relation hits < -20: Kelly thiks of warn, mute, ban
                - Adjust mood / persona based on outcome.
                - Stores user chat / behaviours / likes / dislikes
                - Process the user request - Runs valid command if required and if mood supports
            5. Run Command -> if kelly in right mood performs commands right now else adds them in Kelly's schedules for later
        """
        try: 
            #------Initializing------#
            start = time.time()
            mood = self.mood.getMood()
            persona = self.memory.getPersona()
            relation = self.memory.getUserRelation(message.author.id)
            behave = self.memory.getUserBehaviour(message.author.id)
            type = ""
            author = message.author
            if author.id == 894072003533877279:
                type += "Creator "
            if isinstance(message.channel, discord.DMChannel):
                type = "Dm channel "
            elif message.author.id == message.guild.owner_id:
                type += "Server owner "
            elif message.author.id in Server_Settings[str(message.guild.id)]["moderators"]:
                type = "Moderator "
            if not type:
                type = "Member"

            #------- 1. Giyu the bodyguard handles the message before getting to kelly -------#
            if not await self.giyu.giyuQuery(message, self.mood.mood, type):#if giyu already sent msg so here will not send so here we'll simply return
                return
            #------- 2. Ayasaka the assistant handles the message before getting to kelly -------#
            if not await self.ayasaka.ayasakaQuery(message, self.mood.mood, type):
                return

            # Setting up Prompt
            prompt = f"""Roleplay Kelly — cute, sassy, human-like Discord mod with moods and personality.\nMood: {mood},Persona: {persona},Relation: {relation}\nReply in 10–30 words, 0–3 emojis based on Moods, Persona and Relation. You can perform user command, save for later or deny. Giyu (guard) and Ayasaka (Assistant) call only when need."""
            usermessage = f"{message.author.display_name} ({type}): {message.content}"
            
            #------ 3. Kelly Reply------#
            async with message.channel.typing():
                msg = await message.channel.send(f"-# {choice(['thinking','busy','playing games','sleeping','yawning','drooling','watching','understanding','remembring','wondering','imagining','dreaming','creating','chatting','looking','helping'])}... {EMOJI[choice(list(EMOJI.keys()))]}")
                assist = self.memory.getUserChats(message.author.id) #getting previous chats
                kelly_reply = getResponse(usermessage, prompt, assistant= assist)
                self.memory.addUserChat(message.content, kelly_reply, message.author.id) #Saving chat
                await msg.delete()
                await message.reply(self.kellyEmojify(kelly_reply))  #Replying in channel

            #------ 4. Getting Convo summary------#
            prompt2 = f"""You are Kelly's internal decision engine. Do NOT roleplay or chat. ONLY analyze.\nStatus:mood={mood},persona={persona}\nReturn ONLY valid JSON with fields:\nrespect_delta: int (-5 to +5)\nmood_shift: one from (happy,sad,depressed,angry,annoyed,lazy,sleepy,mischievous,none)\ninfo: one line about user behaviour\ncommand: command_name or null (from chat only)\nexecution: now|later|deny (extract from chat)"""
            raw_result = getResponse(f"Id={message.author.id} {usermessage}\nKelly: {kelly_reply}", prompt2)
            try:
                raw_result = raw_result.strip().lower()
                if raw_result.startswith("{"):
                    result = loads(raw_result)
                elif raw_result.startswith("```"):
                    block = raw_result.split("```")[1]
                    result = loads(block.replace("json",""))
                else:
                    result = loads(raw_result)
            except Exception as parse_error:
                print("Could not parse Kelly AI response:", parse_error) 
                result = {"respect_delta": 0, "mood_shift": "happy", "info": "", "command": None}

            #------5. Performing Task/Command Now------#
            if result["command"] and result["command"] not in ("none", "null"):
                command = result["command"]
                assist = self.memory.getUserChats(message.author.id, limit = 2)
                cmd = self.client.get_command(command)
                if cmd:
                    params = self.get_command_params(cmd, message, author)
                    if "execution" in result and result["execution"] == "now":
                        await self.runCommand(message, command, params)
            
                    elif "execution" in result and result["execution"] == "later":
                        await self.ayasaka.ayasakaQueueTask(message, command, params)
                
            #-----Updating Kelly Now-----#
            await self.mood.modifyMood({"sleepy": randint(1,8)})
            if "mood_shift" in result and result["mood_shift"] in ("sleepy", "happy", "sad", "depressed", "mischievous", "lazy", "annoyed", "angry"):
                if result["mood_shift"] != "sleepy":
                    await self.mood.modifyMood({result["mood_shift"]: randint(1,15)})
                if result["mood_shift"] == "happy":
                    self.memory.modifyUserRelation(message.author.id, 2)
            if "respect_delta" in result:
                rel = self.memory.modifyUserRelation(message.author.id, result["respect_delta"])
                if rel == "friend":
                    await self.thinkFriendAction(message)
                elif rel == "ban":
                    await self.thinkBanAction(message)

            #making busy
            schedules = self.ayasaka.busy.getSchedules()
            for due, schedule in schedules.items():
                if schedule["chatting"] == message.guild.name:
                    del schedules[due]
                    schedules[datetime.now().isoformat()] = schedule
                    break
            else:
                self.ayasaka.busy.addSchedule(message.author.id, message.id, message.channel.id, chatting_in=message.guild.name)
            
        except Exception as error:
            await self.reportError(error)
        print(f">==MOOD<\n{self.mood.mood}\n>==<")
        print(f"KellyQuery Latency: {time.time() - start}s")
        if randint(1,100) == 100:
            await message.channel.send(f"-# Latency: {time.time() - start}s {kemoji()}", delete_after=8)

    def kellyEmojify(self, message):
        message = str(message)
        emoji_exchanger = {
            # kellytired / kellyyawn / kellysleeping
            "😫": "kellytired", 
            "😩": "kellytired", 
            "😪": "kellytired", 
            "😴": "kellysleeping", 
            "🥱": "kellyyawn",
            "🛌": "kellysleeping", 
            "💤": "kellysleeping",

            # kellyacting
            "🎭": "kellyacting", 
            "🎬": "kellyacting", 
            "🎥": "kellyacting", 
            "📽": "kellyacting",

            # kellyannoyed / kellyidontcare
            "😣": "kellyannoyed", 
            "😒": "kellyannoyed", 
            "🙄": "kellyidontcare", 
            "😤": "kellyannoyed",

            # kellyblush
            "😳": "kellyblush", 
            "☺️": "kellyblush", 
            "😊": "kellyblush",

            # kellybored / kellywaiting
            "😐": "kellybored", 
            "😑": "kellybored", 
            "😶": "kellybored", 
            "⏳": "kellywaiting",

            # kellybweh
            "😛": "kellybweh", 
            "😜": "kellybweh", 
            "😝": "kellybweh", 
            "🤪": "kellybweh",

            # kellycheekspull
            "😵": "kellycheekspull", 
            "😵‍💫": "kellycheekspull",

            # kellychips / kellypopcorn
            "🍟": "kellychips", 
            "🍿": "kellypopcorn",

            # kellycry / kellysob
            "😢": "kellycry",
            "🥺": "kellycry",
            "😰": "kellycry",
            "😭": "kellysob",

            # kellyded
            "💀": "kellyded", 
            "☠️": "kellyded",
            "⚰️": "kellyded",

            # kellydaydreaming
            "🤤": "kellydaydreaming", 
            "💭": "kellydaydreaming",

            # kellydrooling
            "🤤": "kellydrooling", 
            "👅": "kellydrooling",

            # kellydumbfounded
            "🤡": "kellydumbfounded", 
            "🤹": "kellydumbfounded",

            # kellyembaress (embarrassed)
            "🤭": "kellyembaress", 
            "😳": "kellyembaress",

            # kellyenjoying
            "🥳": "kellyenjoying",
            "😄": "kellyenjoying", 
            "😃": "kellyenjoying",
 
            # kellyfight
            "👊": "kellyfight", 
            "💪": "kellyfight", 
            "🦾": "kellyfight",

            # kellygigle
            "😁": "kellygigle", 
            "😆": "kellygigle", 
            "😄": "kellygigle",

            # kellyhandraise
            "🙌": "kellyhandraise", 
            "🙋": "kellyhandraise",

            # kellyheart
            "♥": "kellyheart", 
            "❤️": "kellyheart", 
            "💖": "kellyheart", 
            "💗": "kellyheart",

            # kellyhiding
            "😬": "kellyhiding", 
            "😶‍🌫️": "kellyhiding",

            # kellyidontcare (also above)
            "🙂‍↔️": "kellyidontcare",
            "😏": "kellyidontcare",

            # kellyinteresting
            "🧩": "kellyinteresting", 
            "🧐": "kellyinteresting",

            # kellyjuice
            "🥤": "kellyjuice", 
            "🧃": "kellyjuice",

            # kellylaugh
            "😂": "kellylaugh", 
            "🤣": "kellylaugh", 
            "😹": "kellylaugh",

            # kellyok
            "👌": "kellyok", 
            "🆗": "kellyok",

            # kellyowolove
            "😍": "kellyowolove", 
            "😘": "kellyowolove", 
            "🥰": "kellyowolove", 
            "😻": "kellyowolove",

            # kellypat
            "🤗": "kellypat", 
            "🤝": "kellypat",

            # kellysalute
            "🫡": "kellysalute", 
            "🙇": "kellysalute", 
            "🙇‍♀️": "kellysalute", 
            "🙇‍♂️": "kellysalute",

            # kellysimping
            "😙": "kellysimping", 
            "😉": "kellysimping",

            # kellyvibing
            "😎": "kellyvibing", 
            "🕺": "kellyvibing",
            "💃": "kellyvibing",
            "👯": "kellyvibing",
            "👯‍♀️": "kellyvibing",
            "👯‍♂️": "kellyvibing",

            # kellythinking
            "🤔": "kellythinking",

            # kellywatching
            "😠": "kellywatching", 
            "😡": "kellywatching", 
            "👀": "kellywatching",

            # fallback / synonyms (map to existing names)
            "🙂": "kellygigle",
            "😇": "kellyheart",
            "😮": "kellyinteresting",
            "😯": "kellyinteresting"
        }
        for emoji, kellyemoji in emoji_exchanger.items():
            if emoji in message:
                message = message.replace(emoji, EMOJI[kellyemoji])
        return message

    async def thinkFriendAction(self, message):
        """Bot thinks of making user a friend when respect is high."""
        # Think message
        if message.author.id in self.memory._memory["friends"]:
            if randint(1,10) == 5:
                #------ Sending message------#
                prompt = f"Roleplay Kelly — cute, sassy, human-like Discord mod with moods and personality.\nMood: {self.status}\nReply in 10–30 words, 0–3 emojis based on your mood\nYou already replied to user, send one more message continuing the chat.\n• If annoyed/angry → short & firm\n• If sleepy/lazy → delay or deflect\n• If mischievous → tease\n• If duty high → strict"""
                async with message.channel.typing():
                    assist = self.memory.getUserChatData(message.author.id) #getting previous chats
                    kelly_reply = getResponse(message.content, prompt, assistant= assist)
                    self.memory.addUserChat(message.content, kelly_reply, message.author.id) #Saving chat
                    return await message.reply(self.kellyEmojify(kelly_reply))  #Replying in channel
                    
        # Action chance
        roll = randint(1, 100)
        # 60% think only
        if roll <= 60:
            prompt = f"Roleplay Kelly — cute, sassy, human-like Discord mod with moods and personality.\nMood: {self.status}\n You already replied to user. You think of making user friend but havent made him friend yet. Reply in 10-30 words with 0-4 emojis."
            async with message.channel.typing():
                assist = self.memory.getUserChats(message.author.id)
                kelly_reply = getResponse(message.content, prompt, assistant= assist)
                self.memory.addUserChat(message.content, kelly_reply, message.author.id) #Saving chat
                await message.reply(self.kellyEmojify(kelly_reply))  #Replying in channel     
            
        # 25% make friend
        elif roll <= 85:
            prompt = f"Roleplay Kelly — cute, sassy, human-like Discord mod with moods and personality.\nMood: {self.status}.\nReply in 10–30 words, 0–3 emojis based on your mood. You are Kelly sassy lively Discord Mod Bot, You already replied to user. You have finally made user as your friend. Also inform user that dms are open now."
            async with message.channel.typing():
                assist = self.memory.getUserChats(message.author.id)
                kelly_reply = getResponse(message.content, prompt, assistant=assist)
                self.memory.addUserChat(message.content, kelly_reply, message.author.id) #Saving chat
                return await message.reply(self.kellyEmojify(kelly_reply))  #Replying in channel     
            self.memory.addFriend(message.author.id)
        # 15% small reward
        else:
            await message.channel.send("✨ You're special! Here's a small gift for being nice. Join official Server to recieve your reward")
            # Give reward logic here

    async def thinkBanAction(self, message):
        """Bot thinks of punishing the user when respect is low."""
        roll = randint(1, 100)
        if message.author.id in self.memory._memory["friends"]:
            self.memory.removeFriend(message.author.id)
            
        # 60% think only
        if roll <= 60:
            promt = f"Roleplay Kelly — cute, sassy, human-like Discord mod with moods and personality.\nMood: {self.status}\n You already replied to user, but yoou think user is very rude but you tolerate this for now.\nReply in 10–30 words, 0–3 emojis based on your mood."
            async with message.channel.typing():
                assist = self.memory.getUserChats(message.author.id) #getting previous chats
                kelly_reply = getResponse(message.content, prompt, assistant= assist)
                self.memory.addUserChat(message.content, kelly_reply, message.author.id) #Saving chat
                return await message.reply(self.kellyEmojify(kelly_reply))  #Replying in channel
            
        # 25% mute instead of ban
        elif roll <= 85:
            prompt = f"Roleplay Kelly — cute, sassy, human-like Discord mod with moods and personality.\nMood: {self.status}\nYou already replied to user. You think user is very rude and you are angry and mute him. Reply in 10-30 words with 0-3 emojis."
            async with message.channel.typing():
                assist = self.memory.getUserChats(message.author.id) #getting previous chats
                kelly_reply = getResponse(message.content, prompt, assistant= assist)
                self.memory.addUserChat(message.content, kelly_reply, message.author.id) #Saving chat
                await message.reply(self.kellyEmojify(kelly_reply))  #Replying in channel     
                await self.runCommand(message, "mute_from_kelly", {"member": message.author, "minutes":ranint(1,15), "reason": "Very Bad Relations with Kelly"})
        # 15% actual ban
        else:
            prompt = f"Roleplay Kelly — cute, sassy, human-like Discord mod with moods and personality.\nMood: {self.status}.You are Kelly sassy lively Discord Mod Bot, You already replied to user. You think user is very rude and you are angry and you ban him finally no mercy. Reply in 10-30 words with 0-3 emojis."
            async with message.channel.typing():
                assist = self.memory.getUserChats(message.author.id) #getting previous chats
                kelly_reply = getResponse(message.content, prompt, assistant= assist)
                self.memory.addUserChat(message.content, kelly_reply, message.author.id) #Saving chat
                await message.reply(self.kellyEmojify(kelly_reply))      
                await self.runCommand(message, "ban_from_kelly", {"member": message.author, "reason": "Bad Relationship"})
        
    async def remind(self, task):
        prompt = f"Roleplay Kelly, a Discord Mod (human like with mood and sass). You have to {task['task']} user. Keep chat alive fun and interesting.\nGenerate response in 20 words with 0-4 emojiy."
        if "user" in task:
            try:
                user = await self.client.fetch_user(task["user"])
            except:
                return
            msg = self.kellyEmojify(getResponse(f"Hey I'm {user.display_name}, {task['task']} me!", prompt))
            if task["channel"]:
                try:
                    channel = await self.client.fetch_channel(task["channel"])
                    await channel.send(f"{user.mention} {msg}")
                except:
                    await safe_dm(user, message = msg)
            else:
                await safe_dm(user, message = msg)
        try:
            channel = await self.client.fetch_channel(task["channel"])
            message = await channel.fetch_message(task["message"])
        except:
            return
        await message.reply(self.kellyEmojify(getResponse(f"{task['task']} user", prompt)))
        
