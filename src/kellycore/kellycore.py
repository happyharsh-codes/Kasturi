from __init__ import*
from src.kellycore.kellymood import KellyMood
from src.kellycore.kellyrelation import KellyRealtion
from src.kellycore.kellypersonality import KellyPersona
from src.kellycore.kellybusy import KellyBusy
from src.kellycore.kellymemory import KellyMemory
from src.kellycore.giyu import Giyu
from src.kellycore.ayaka import Ayaka 

class Kelly:
    """Main Kelly Core(Brain) - kellycore.py  
    Governs all activities:
        - Receives messages: -> if command run command else talk
        -   * Relation system - kellyrelation.py
            * Mood system - kellymood.py
            * Personality - kellypersonality.py
            * Memory - kellymemory.py
            * Busy - kellybusy.py
            * Giyu - giyu.py
            * Ayaka - ayaka.py
        - Handles callbacks from KellyRelation (friend / ban)
        - Manages busy-tasks via KellyBusy
        - Stores server & user data in memory systems
    """
    def __init__(self, name, bot):
        self.name = name
        self.client = bot #discord bot
        self.mood = KellyMood(bot)
        self.personality = KellyPersona(Persona)
        self.relations = KellyRealtion()
        self.memory = KellyMemory()
        self.giyu = Giyu(bot)
        self.ayaka = Ayaka(self)
        self.mood.generateRandomMood()
        self.commands = {cmd.name : list(cmd.clean_perms.keys()) for cmd in bot.commands}
                
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
    
    async def runCommand(self, message: discord.Message, ai_result: dict):
        try:
            cmd_name = list(ai_result.get("command").keys())[0]
            params = list(ai_result.get("command").values())[0]

            if not cmd_name:
                await message.channel.send("I’m not seeing any command here. 🙄")
                return

            # Find the command object
            cmd = self.client.get_command(cmd_name)
            if not cmd:
                await message.channel.send(f"Ughhh, I don’t even *have* a `{cmd_name}` command. 🙃")
                return

            # Get ctx
            ctx = await self.client.get_context(message)
            final_params = {}

            for item, val in params.items():
                if val == "" or val == [] or val == {}:
                    await message.channel.send(f"You are missing this : {item}")
                    return
                if isinstance(val,str) and val.startswith("<"):
                    try:
                        if "@&" in val:
                            final_params[item] = await message.guild.fetch_role(int(val[3:-1]))
                        elif "@" in val:
                            user_id = int(val[2:-1].lstrip("!"))  # handle <@!id>
                            final_params[item] = await message.guild.fetch_member(int(val[2:-1]))
                        elif "#" in val:
                            final_params[item] = await message.guild.fetch_channel(int(val[2:-1]))
                    except Exception as e:
                        await message.channel.send(f"Invalid Channel/Role/User provided for {item}:{val}\nError:{e}")
                        return
                elif isinstance(val,str) and val.isdigit():
                    try:
                        final_params[item] = await message.guild.fetch_member(int(val))
                    except:
                        try:
                            final_params[item] = await message.guild.fetch_channel(int(val))
                        except:
                            try:
                                final_params[item] = await message.guild.fetch_role(int(val))
                            except Exception as e:
                                await message.channel.send(f"Invalid Role/Channel/User Provided for {item}:{val}\nError:{e}")
                                return          
                else: final_params[item] = val
            print(f"### Running command {cmd_name} with {final_params}")
            await ctx.invoke(cmd, **final_params)

        except Exception as e:
            await self.reportError(e)
    
    async def kellyQuery(self, message: discord.Message):
        """
        Main handler for incoming user messages.
        Steps:
            1. Giyu Check
                - Check if user is Blocked
                - Check is user is Muted
                - Check is user is new
                - Check if Kelly is busy:
                    - If busy, talk but queue the request.
                - Check if Kelly is sleeping 
            2. Kelly Reply
            3. Generate Message Result
                - Update relation (respect) based on message style.
                    - relation hits > 80: Kelly thinks of making friend
                    - relation hits < -20: Kelly thiks of warn, mute, ban
                - Adjust mood / persona based on outcome.
                - Stores user chat
                - Store memory / info about user
                - Process the user request - Runs valid command if required and if mood supports
        """
        try: 
            #------Initializing------#
            mood = self.mood.getCurrentMood()
            persona = self.personality.getRequiredPersona()
            relation = self.relations.getUserRelation(message.author.id)
            behave = self.memory.getUserInfo(message.author.id)["behaviours"]
            type = ""
            if message.author.id == 894072003533877279:
                type += "God aka your creator "
            if isinstance(message.channel, discord.DMChannel):
                type = "Dm channel "
            elif message.author.id == message.guild.owner_id:
                type += "Server owner "
            elif message.author.id in Server_Settings[str(message.guild.id)]["moderators"]:
                type = "Moderator "
            if not type:
                type = "Member"
            prompt = f"""Roleplay Kelly, a Discord Mod (human like with mood and sass). Current mood: {mood}, perosna: {persona}, relation: {self.relations.getUserRelation(message.author.id)}, User: {{Name: {message.author.display_name}, type:{type}, id:{message.author.id}}}\nGenerate response in 20 words with 0-4 emojiy. Keep chat interesting and fun by interacting with user and asking enagaging questions."""

            #------- 1. Giyu the bodyguard handles the message before getting to kelly -------#
            if not await self.giyu.giyuQuery(message, self.mood.mood, type):#if giyu already sent msg so here will not send so here we'll simply return
                return
            if not await self.ayaka.ayakaQuery(message, self.mood.mood, type):
                return

            # Setting Kelly Mood - only alters the response
            if self.mood.mood["mischievous"] > 80:
                prompt += " Kelly is feeling extra mischevious today"
            elif self.mood.mood["sad"] > 80 or self.mood.mood["depressed"] > 80:
                prompt += " Kelly is extremely sad and depressed"

            #------ 2. Sending message------#
            async with message.channel.typing():
                msg = await message.channel.send(f"-# {choice(['thinking','busy','playing games','sleeping','yawning','drooling','watching','understanding','remembring','wondering','imagining','dreaming','creating','chatting','looking','helping'])}... {EMOJI[choice(list(EMOJI.keys()))]}")
                assist = self.memory.getUserChatData(message.author.id) #getting previous chats
                kelly_reply = getResponse(message.content, prompt, assistant= assist, client=0)
                self.memory.storeChatData(message.content, kelly_reply, message.author.id) #Saving chat
                await msg.delete()
                await message.reply(self.kellyEmojify(kelly_reply))  #Replying in channel

            #------ 3. Getting Convo summary------#
            current_status = {"respect": relation,"mood": mood, "persona": persona}
            prompt2 = f"""You are Kelly/Kasturi kelly discord mod bot(lively with mood attitude and sass)
                Current status: {current_status}
                Generate Json dict using kelly response and mood
                - respect: (-10 : +10) (int)
                - mood: (happy(default)/sad/depressed/angry/annoyed/lazy/sleepy/mischevious) (from these only)
                - personality_change: {{(personality_name): +/- 10 (int)}}
                - info: (str) (small info about user behaviour and type)
                - command: (default none for talking) {self.commands} (eg: {{"command_name":{{"param1": "value"}}}})"""
            raw_result = getResponse(f"User(id = {message.author.id}): {message.content}\nKelly: {kelly_reply}", prompt2, assistant=assist, client=0).lower()
            try:
                if not raw_result.startswith("```"):
                    raw_result = "```json " + raw_result + " ```"
                result = loads(raw_result.replace("+","").split("```json")[1].split('```')[0])

            except Exception as parse_error:
                print("Could not parse Kelly AI response:", parse_error) 
                result = {"respect": 0, "mood": "happy", "personality_change": {}, "info": [], "command": None}

            #-----Updating Kelly Now-----#
            self.mood.modifyMood({"sleepy": 10})
            if "mood" in result:
                self.mood.modifyMood({result["mood"]: randint(1,15)})
                if result["mood"] == "happy":
                    self.relations.modifyUserRespect(2, message.author.id)
            if "personality_change" in result and isinstance(result["personality_change"], int):
                self.personality.modifyPersonality(result['personality_change'])
            if "relation" in result:
                rel = self.relations.modifyUserRespect(result["respect"], message.author.id)
                if rel == "friend":
                    await self.thinkFriendAction(message, prompt)
                elif rel == "ban":
                    await self.thinkBanAction(message, prompt)
            
            #------Performing Task/Command Now------#
            if "command" in result and result["command"] and result["command"] != "none":
                if isinstance(list(result["command"].values())[0], list):
                    params = {}
                    cmd = list(result["command"].keys())[0]
                    for index, param in enumerate(self.commands[cmd]):
                        params[param] = list(result["command"].values())[0][index]
                    result["command"] = {cmd: params}
                await self.runCommand(message, result)

        except Exception as error:
            await self.reportError(error)
        print(f">==MOOD<\n{self.mood.mood}\n>==<")
        print(f">==PERSONALITY<\n{self.personality.persona}\n>==<")

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
        mood_map = {
            "happy": {"kellypat", "kellylaugh", "kellygigle", "kellyowolove", "kellyenjoying", "kellyvibing"},
            "sad": {"kellycry", "kellysob"},
            "angry": {"kellywatching", "kellyfight", "kellyannoyed"},
            "annoyed": {"kellyannoyed", "kellyidontcare", "kellybored", "kellywatching", "kellycheekspull"},
            "depressed": {"kellydead", "kellycry"},
            "mischievous": {"kellydaydreaming", "kellybweh", "kellyacting", "kellydumbfounded", "kellysimping",},
            "sleepy": {"kellytired", "kellyyawn", "kellysleeping", "kellydrooling" },
            "lazy": {"kellytired", "kellysleeping", "kellyyawn", "kellychips"}
        }
        for emoji, kellyemoji in emoji_exchanger.items():
            if emoji in message:
                message = message.replace(emoji, EMOJI[kellyemoji])

            for mood, triggers in mood_map.items():
                if kellyemoji in triggers:
                    self.mood.modifyMood({mood: randint(1, 8)})
            
        return message

    async def thinkFriendAction(self, message):
        """Bot thinks of making user a friend when respect is high."""
        # Think message
        if message.author.id in Database["friends"]:
            if ranint(1,6) == 5:
                #------ Sending message------#
                prompt = "You are Kelly sassy lively Discord Mod Bot, You already replied to user. Send one more message continuing the chat because you are good friends now."
                async with message.channel.typing():
                    assist = self.memory.getUserChatData(message.author.id) #getting previous chats
                    kelly_reply = getResponse(message.content, prompt, assistant= assist)
                    await message.reply(self.kellyEmojify(kelly_reply))  #Replying in channel
                    last_msg = Behaviours[str(message.author.id)][-1]
                    last_msg += kelly_reply
                    Behaviours[str(message.author.id)][-1] = last_msg
            return
        # Action chance
        roll = random.randint(1, 100)
        # 60% think only
        if roll <= 60:
            prompt = "You are Kelly sassy lively Discord Mod Bot, You already replied to user. You think of making user friend but havent made him friend yet. Generate reply in 20 words with emojis."
            async with message.channel.typing():
                assist = self.memory.getUserChatData(message.author.id)
                kelly_reply = getResponse(message.content, prompt, assistant= assist)
                await message.reply(self.kellyEmojify(kelly_reply))  #Replying in channel     
            
        # 25% make friend
        elif roll <= 85:
            prompt = "You are Kelly sassy lively Discord Mod Bot, You already replied to user. You have finally made user as your friend. Also inform user that dms are open now. Generate reply in 20 words with emojis."
            async with message.channel.typing():
                assist = self.memory.getUserChatData(message.author.id)
                kelly_reply = getResponse(message.content, prompt, assistant= assist)
                await message.reply(self.kellyEmojify(kelly_reply))  #Replying in channel     
            self.memory.addFriend(message.author.id)
        # 15% small reward
        else:
            await message.channel.send("✨ You're special! Here's a small gift for being nice. Join official Server to recieve your reward")
            # Give reward logic here

    async def thinkBanAction(self, message):
        """Bot thinks of punishing the user when respect is low."""
        roll = random.randint(1, 100)
        if message.author.id in Database["friends"]:
            self.memory.removeFriend(message.author.id)
            
        # 60% think only
        if roll <= 60:
            prompt = "You are Kelly sassy lively Discord Mod Bot, You already replied to user. You think user is very rude but tolerate this for once for now. Generate reply in 20 words with emojis."
            async with message.channel.typing():
                assist = self.memory.getUserChatData(message.author.id)
                kelly_reply = getResponse(message.content, prompt, assistant= assist)
                await message.reply(self.kellyEmojify(kelly_reply))  #Replying in channel
            
        # 25% mute instead of ban
        elif roll <= 85:
            prompt = "You are Kelly sassy lively Discord Mod Bot, You already replied to user. You think user is very rude and you are angry and mute him. Generate reply in 20 words with emojis."
            async with message.channel.typing():
                assist = self.memory.getUserChatData(message.author.id)
                kelly_reply = getResponse(message.content, prompt, assistant= assist)
                await message.reply(self.kellyEmojify(kelly_reply))  #Replying in channel     
                await self.runCommand(message, {"mute_from_kelly": {"member": message.author, "minutes":ranint(1,15), "reason": self.getEmoji(kelly_reply)}})
        # 15% actual ban
        else:
            prompt = "You are Kelly sassy lively Discord Mod Bot, You already replied to user. You think user is very rude and you are angry and you ban him finally no mercy. Generate reply in 20 words with emojis."
            async with message.channel.typing():
                assist = self.memory.getUserChatData(message.author.id)
                kelly_reply = getResponse(message.content, prompt, assistant= assist)
                await message.reply(self.kellyEmojify(kelly_reply))      
                await self.runCommand(message, {"ban_from_kelly": {"member": message.author, "reason": self.getEmoji(kelly_reply)}})
        
    async def remind(self, task):
        prompt = f"Roleplay Kelly, a Discord Mod (human like with mood and sass). You have to {task['task']} user. Keep chat alive fun and interesting.\nGenerate response in 20 words with 0-4 emojiy."
        if "uid" in task:
            try:
                user = await self.client.fetch_user(task["uid"])
            except:
                return
            em = Embed(color=Color.green())
            em.description = self.kellyEmojify(getResponse(f"Hey I'm {user.display_name}, {task['task']} me!", prompt))
            await safe_dm(user, em)
        try:
            channel = await self.client.fetch_channel(task["channel"])
            message = await channel.fetch_message(task["message"])
        except:
            return
        await message.reply(self.kellyEmojify(getResponse(f"{task['task']} user", prompt)))
        
