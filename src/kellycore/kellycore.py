from __init__ import*
from src.kellycore.kellymood import KellyMood
from src.kellycore.kellyrelation import KellyRealtion
from src.kellycore.kellypersonality import KellyPersona
from src.kellycore.giyu import Giyu

class Kelly:

    def __init__(self, name, bot):
        self.name = name
        self.client = bot #discord bot
        self.mood = KellyMood(bot)
        self.personality = KellyPersona(Persona)
        self.relations = KellyRealtion()
        self.chats = Chats
        self.mood.generateRandomMood()
        self.giyu = Giyu(bot)
        self.commands = None
                
    async def reportError(self, error):
        try:
            me = self.client.get_user(894072003533877279)
            await me.send(f"Erron on KellyCore:{error}")
        except:
            print("Could not dm error")
        print("error in kelly core: ", error)

    def addUser(self,guildid, id):
        if id not in Server_Settings[str(guildid)]['block_list']:
            self.realtion[str(id)] = 1

    def getUserChatData(self, userid):
        if str(userid) in Chats:
            all_user_chats = Chats[str(userid)]
            res = "\n".join(all_user_chats)
            return res
        return ""

    def addUserChatData(self, user_message, kelly_message, id):
        user_message = user_message.replace("\n","").replace(":","")
        kelly_message = kelly_message.replace("\n","").replace(":","")
        if str(id) not in Chats:
            Chats[str(id)] = [f"User:{user_message}\nKelly:{kelly_message}"]
        else:
            Chats[str(id)].append(f"User:{user_message}\nKelly:{kelly_message}")
            if len(Chats[str(id)]) > 4:
                Chats[str(id)].pop(0)

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
        try: 
            #------Initializing------#
            mood = self.mood.getMood()
            persona = self.personality.getRequiredPersona()
            relation = self.relations.getUserRelation(message.author.id)
            behave = self.relations.getUserInfo(message.author.id)
            type = ""
            if message.author.id == 894072003533877279:
                type = "God aka your creator"
            if message.author.id == message.guild.owner_id:
                type += " Server owner"
                if not Server_Settings[str(message.guild.id)]["owner"]:
                    Server_Settings[str(message.guild.id)]["owner"] = message.author.id
            elif any(r.permissions.administrator or r.permissions.kick_members or r.permissions.ban_members or r.permissions.manage_roles or r.permissions.mute_members or r.permissions.deafen_members or r.permissions.manage_permissions or r.permissions.manage_channels for r in message.author.roles):
                type = "Moderator"
                if message.author.id not in Server_Settings[str(message.guild.id)]["moderators"]:
                    Server_Settings[str(message.guild.id)]["moderators"].append(message.author.id)
            else:
                type = "Member"
            prompt = f"""Roleplay Kelly, a Discord Mod (human like with mood and sass). Current mood: {mood}, perosna: {persona}, relation: {self.relations.getUserRelation(message.author.id)}, User: {{Name: {message.author.display_name}, type:{type}, id:{message.author.id}}}\nGenerate response in 20 words with 0-4 emojiy. keep chat interesting and fun by interacting with user and must asking enagaging questions at last"""

            #first Giyu the bodyguard handles the message before getting to kelly
            if await self.giyu.giyuQuery(message, self.mood.mood):#if giyu already sent msg so here will not send so here we'll simply return
                return
            
            #------Generating message session id------#
            #self.generateSessionId(message)            

            #kelly Mood
            if self.mood.mood["mischevious"] > 80:
                prompt += " Kelly is feeling extra mischevious today"
            elif self.mood.mood["sad"] > 80 or self.mood.mood["depressed"] > 80:
                prompt += " Kelly is extremely sad and depressed"

            #------Sending message------#
            async with message.channel.typing():
                msg = await message.channel.send(f"-# {choice(['thinking','busy','playing games','sleeping','yawning','drooling','watching','understanding','remembring','wondering','imagining','dreaming','creating','chatting','looking','helping'])}... {EMOJI[choice(list(EMOJI.keys()))]}")
                assist = self.getUserChatData(message.author.id) #getting previous chats
                kelly_reply = getResponse(message.content, prompt, assistant= assist, client=0)
                self.addUserChatData(message.content, kelly_reply, message.author.id) #Saving chat
                await msg.delete()
                await message.reply(self.getEmoji(kelly_reply))  #Replying in channel

            #------Getting Convo summary------#
            if not self.commands:
                cmds = {}
                for command in self.client.get_cog("Moderation").get_commands():
                    cmds[command.name] = list(command.clean_params.keys())
                self.commands = cmds
            current_status = {"respect": relation,"mood": mood, "persona": persona}
            prompt2 = f"""You are Kelly/Kasturi kelly discord mod bot(lively with mood attitude and sass)
                Current status: {current_status}
                Generate Json dict using kelly response and mood
                - respect: (-10 : +10) (int)
                - mood: (happy(default)/sad/depressed/angry/annoyed/lazy/sleepy/busy/mischevious) (from these only)
                - personality_change: {{(personality_name): +/- 10 (int)}}
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
            if "mood" in result:
                self.mood.modifyMood({result["mood"]: randint(1,15)})
                if result["mood"] == "happy":
                    self.relations.modifyUserRespect(2, message.author.id)
            if "personality_change" in result and isinstance(result["personality_change"], int):
                self.personality.modifyPersonality(result['personality_change'])
            if "relation" in result:
                self.relations.modifyUserRespect(result["respect"], message.author.id)
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

    def getEmoji(self, message):
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
            "happy": {"kellypat", "kellylaugh", "kellygigle", "kellyowolove","kellypopcorn", "kellyenjoying", "kellyok", "kellyacting","kellyjuice", "kellyvibing"},
            "sad": {"kellycry", "kellysob", "kellydaydreaming"},
            "angry": {"kellywatching", "kellyfight", "kellyannoyed"},
            "annoyed": {"kellyannoyed", "kellyidontcare", "kellybored", "kellywatching", "kellycheekspull"},
            "depressed": {"kellydead", "kellydaydreaming", "kellycry"},
            "mischevious": {"kellybweh", "kellyacting", "kellydumbfounded", "kellysimping",},
            "busy": {"kellysalute", "kellyhandraise", "kellywatching"},
            "sleepy": {"kellytired", "kellyyawn", "kellysleeping", "kellydrooling" },
            "lazy": {"kellytired", "kellysleeping", "kellyyawn", "kellychips"}
        }
        for emoji, kellyemoji in emoji_exchanger.items():
            if emoji in message:
                message = message.replace(emoji, EMOJI[kellyemoji])

            for mood, triggers in mood_map.items():
                if kellyemoji in triggers:
                    self.mood.modifyMood({mood: randint(1, 15)})
            
        return message

    def save(self):
        self.relations.save()
        self.personality.save()
        with open("res/kellymemory/chats.json", "w") as f:
            dump(Chats, f, indent=4)

