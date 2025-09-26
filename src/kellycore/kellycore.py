from __init__ import*
from src.kellycore.kellymood import KellyMood
from src.kellycore.kellyrelation import KellyRealtion
from src.kellycore.kellypersonality import KellyPersona
from src.kellycore.giyu import Giyu

class Kelly:

    def __init__(self, name, bot):
        self.name = name
        self.client = bot #discord bot
        self.mood = KellyMood()
        self.personality = KellyPersona(Persona)
        self.relations = KellyRealtion()
        self.chats = Chats
        self.mood.generateRandomMood()
        self.giyu = Giyu()
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
                    final_params[item] = int(val[2:-1]) 
                elif isinstance(val,str) and val.isdigit():
                    final_params[item] = int(val)
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
            if message.author.id == 894072003533877279:
                type = "God aka your creator"
            elif message.author.id == message.guild.owner_id:
                type = "Server owner"
            elif any(r.permissions.administrator or r.permissions.kick_members or r.permissions.ban_members or r.permissions.manage_roles or r.permissions.mute_members or r.permissions.deafen_member or r.permissions.manage_channels for r in message.author.roles):
                type = "Moderator"
            else:
                type = "Member"
            prompt = f"""Roleplay Kelly, a Discord Mod (human like with mood and sass). Current mood: {mood}, perosna: {persona}, relation: {self.relations.getUserRelation(message.author.id)}, User: {{Name: {message.author.display_name}, type:{type}}}\nGenerate response in 20 words with 0-4 emojiy. keep chat interesting and fun by interacting with user and must asking enagaging questions at last"""

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
                msg = await message.channel.send(f"-# {choice(["thinking","busy","playing games","sleeping","yawning","drooling","watching","understanding","remembring","wondering","imagining","dreaming","creating","chatting","looking","helping"])}... {EMOJI[choice(list(EMOJI.keys()))]}")
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
            raw_result = getResponse(f"User: {message.content}\nKelly: {kelly_reply}", prompt2, assistant=assist, client=0).lower()
            try:
                if not raw_result.startswith("```"):
                    raw_result = "```json " + raw_result + " ```"
                result = loads(raw_result.replace("+","").split("```json")[1].split('```')[0])

            except Exception as parse_error:
                print("Could not parse Kelly AI response:", parse_error) 
                result = {"respect": 0, "mood": "happy", "personality_change": {}, "info": [], "command": None}

            #-----Updating Kelly Now-----#
            if "mood" in result and isinstance(result["mood"], int):
                self.mood.modifyMood({result["mood"]: randint(1,10)})
                if result["mood"] == "happy":
                    self.relations.modifyUserRespect(2, message.author.id)
            if "personality_change" in result and isinstance(result["personality_change"], int):
                self.personality.modifyPersonality(result['personality_change'])
            if "relation" in result:
                self.relations.modifyUserRespect(result["respect"], message.author.id)
            #------Performing Task/Command Now------#
            if "command" in result and result["command"] and result["command"] != "none":
                await self.runCommand(message, result)

        except Exception as error:
            await self.reportError(error)
        print(f">==<\n{self.mood.mood}\n>==<")
        print(f">==<\n{self.personality.persona}\n>==<")

    def getEmoji(self, message):
        emoji_exchanger = {
            "😫": "kellytired",
            "💤": "kellytired",
            "😪": "kellytired",
            "😩": "kellytired",
            "😴": "kellytired",
            "🎭": "kellyacting",
            "🎬": "kellyacting",
            "🎥": "kellyacting",
            "📽": "kellyacting",
            "🎦": "kellyacting",
            "📼": "kellyacting",
            "🎞": "kellyacting",
            "📹": "kellyacting",
            "📷": "kellyacting",
            "📸": "kellyacting",
            "😣": "kellyannoyed",
            "😳": "kellyblush",
            "😚": "kellyblush",
            "😏": "kellybored",
            "😒": "kellybored",
            "😛": "kellybweh",
            "😜": "kellybweh",
            "😝": "kellybweh",
            "🤪": "kellybweh",
            "😵": "kellycheekspull",
            "🍟": "kellychips",
            "😭": "kellycry",
            "🤤": "kellydrooling",
            "👅": "kellydrooling",
            "🤭": "kellyembaress",
            "👊": "kellyfight",
            "💪": "kellyfight",
            "🦾": "kellyfight",
            "😊": "kellygigle",
            "😁": "kellygigle",
            "👋": "kellygigle",
            "🙌": "kellyhandraise",
            "♥": "kellyheart",
            "😬": "kellyhiding",
            "🙄": "kellyidontcare",
            "😒 ": "kellyidontcare",
            "🧩": "kellyinteresting",
            "🧐": "kellyinteresting",
            "🥤": "kellyjuice",
            "🧃": "kellyjuice",
            "😂": "kellylaugh",
            "🤣": "kellylaugh",
            "😄": "kellylaugh",
            "😆": "kellylaugh",
            "😃": "kellylaugh",
            "👌": "kellyok",
            "🆗": "kellyok",
            "🙆‍♀️": "kellyok",
            "🙆‍♂️": "kellyok",
            "😍": "kellyowolove",
            "😘": "kellyowolove",
            "🥰": "kellyowolove",
            "😻": "kellyowolove",
            "🤗": "kellypat",
            "🍿": "kellypopcorn",
            "🎉": "kellypopcorn",
            "🍾": "kellypopcorn",
            "🛐": "kellysalute",
            "🙇": "kellysalute",
            "🙇‍♀️": "kellysalute",
            "😙": "kellysimping",
            "😉": "kellysimping",
            "💤": "kellysleeping",
            "😴": "kellysleeping",
            "🛌": "kellysleeping",
            "🤔": "kellythinking",
            "😁": "kellyvibing",
            "🤨": "kellywatching",
            "😠": "kellywatching",
            "😡": "kellywatching",
            "😤": "kellywatching",
            "😗": "kellywatching",
            "🥱": "kellyyawn"
        }
        for emoji, kellyemoji in emoji_exchanger.items():
            if emoji in message:
                message = message.replace(emoji, EMOJI[kellyemoji])
                if kellyemoji == "kellyyawn" or kellyemoji == "kellysleeping" or kellyemoji == "kellydrooling" or kellyemoji == "kellytired":
                    self.mood.modifyMood({"sleepy": randint(1,15)})
                if kellyemoji == "kellycry":
                    self.mood.modifyMood({"sad": randint(1, 15)})
                if kellyemoji == "kellywatching":
                    self.mood.modifyMood({"angry": randint(1, 15)})
                    self.mood.modifyMood({"annoyed": randint(1, 15)})
                if kellyemoji == "kellypat" and kellyemoji == "kellylaugh" and kellyemoji == "kellygigle":
                    self.mood.modifyMood({"happy": randint(1, 10)})
                if kellyemoji == "kellyannoyed" or kellyemoji == "kellyidontcare" or kellyemoji == "kellybored":
                    self.mood.modifyMood({"annoyed": randint(1, 15)})
                
            
        return message

    def save(self):
        self.relations.save()
        self.personality.save()
        with open("res/kellymemory/chats.json", "w") as f:
            dump(Chats, f, indent=4)

