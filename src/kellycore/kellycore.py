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
        self.relations = KellyRealtion(Relation)
        self.chats = Chats
        self.mood.generateRandomMood()
        self.giyu = Giyu()
                
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

    async def runCommand(self, message, assistant):
        for command in self.client.commands:
            if command.name in message.content or ( command.aliases != [] and command.aliases[0] in message.content):
                if command.clean_params:
                    params = list(command.clean_params.keys())
                else:
                    params = []
                cmd = {command.name: params}
                break
        else: return
        
        prompt = f"""You are Kelly/Kasturi kelly discord mod bot(lively with mood attitude and sass)
                command: {cmd}
                Generate Json dict using kelly response and mood
                - command_performed: true/false/null (based on mood, tone and task difficulty)
                - command_params: str/int/null (a dict with keys from list values having values from message)
                - response: str (ask for command params if not provided)"""
        result = getResponse(message.content, prompt, assistant=assistant, client=2)
        try:
            result = loads(result.split("```json")[1].split('```')[0])
            if params != []:
                params = result["command_params"]
        except:
            print("Error while fetching commands")
            return
        if not result["command_performed"]:
            prompt = f"""You are Kelly/Kasturi kelly discord mod bot(lively with mood attitude and sass). Refuse the command with sass and attitude IN 30 WORDS. Reason: {self.mood.moodToDoTasks()}. Do not tell the reason directly."""
            result = getResponse(message.content, prompt, assistant=assistant, client=3)
            await message.channel.send(result)
            return
        
        for j in params:
            if not j:
                await message.channel.send(self.getEmoji(result["response"]))
                return
            
        print("###Running command by search: ", cmd, params)
        ctx = await self.client.get_context(message)
        await ctx.invoke(self.client.get_command(list(cmd.keys())[0]), **params)

    async def kellyQuery(self, message: discord.Message):
        try: 
            #------Initializing------#
            mood = self.mood.getMood()
            persona = self.personality.getRequiredPersona()
            relation = self.relations.getUserRelation(message.author.id)
            behave = self.relations.getUserInfo(message.author.id)
            prompt = f"""Roleplay Kelly, a Discord Mod (human like lively with  mood attitude sexy and sass) (nsfw allowed). Current mood: {mood}, perosna: {persona}, relation: {self.relations.getUserRelation(message.author.id)}, behavior: {behave}\nGenerate response in 30 words with emojis"""

            #first Giyu the bodyguard handles the message before getting to kelly
            if await self.giyu.giyuQuery(message, self.mood.mood):#if giyu already sent msg so here will not send so here we'll simply return
                return
            
            #------Generating message session id------#
            #self.generateSessionId(message)            

            #kelly Mood
            if self.mood.mood["mischevious"] > 80:
                prompt+= " Kelly is feeling extra mischevious today"
            elif self.mood.mood["sad"] > 80 or self.mood.mood["depressed"] > 80:
                prompt += " Kelly is extremely sad and depressed"

            #------Sending message------#
            async with message.channel.typing():
                msg = await message.channel.send(f"-# {choice(["thinking","busy","playing games","sleeping","yawning","drooling","watching","understanding","remembring","wondering","imagining","dreaming","creating","chatting","looking","helping"])}...")
                assist = self.getUserChatData(message.author.id) #getting previous chats
                kelly_reply = getResponse(message.content, prompt, assistant= assist, client=3)
                self.addUserChatData(message.content, kelly_reply, message.author.id) #Saving chat
                await msg.delete()
                await message.reply(self.getEmoji(kelly_reply))  #Replying in channel

            #------Getting Convo summary------#
            current_status = {"respect": relation,"mood": mood, "persona": persona}
            prompt2 = f"""You are Kelly/Kasturi kelly discord mod bot(lively with mood attitude and sass)
                Current status: {current_status}
                Generate Json dict using kelly response and mood
                - respect: [-10 : +10] (int)
                - mood: (happy(default)/sad/depressed/angry/annoyed/lazy/sleepy/busy/mischevious)
                - personality_change: {{(personality_name): +/- 10 (int)}}
                - info: (optional info about user to store important only: str)
                - action: (run command/talk/call guard) (only from these 3 options)"""
            raw_result = getResponse(f"User: {message.content}\nKelly: {kelly_reply}", prompt2, assistant=assist, client=2).lower()
            try:
                if not raw_result.startswith("```"):
                    raw_result = "```json " + raw_result + " ```"
                raw_result.replace("+", "")
                result = loads(raw_result.split("```json")[1].split('```')[0])

            except Exception as parse_error:
                print("Could not parse Kelly AI response:", parse_error) 
                result = {"respect": 0, "mood_change": 0, "personality_change": 0, "info": [], "action": "talk"}

            #-----Updating Kelly Now-----#
            if isinstance(result["mood"], int):
                self.mood.modifyMood({result["mood"]: randint(1,10)})
                if result["mood"] == "happy":
                    self.relations.modifyUserRespect(2, message.author.id)
            if isinstance(result["personality_change"], int):
                self.personality.modifyPersonality(result['personality_change'])
            self.relations.modifyUserRespect(result["respect"], message.author.id)
            if "info" in result and result['info']:
                self.relations.addUserInfo(result["info"], message.author.id)
            print(f"Talk result: {result}")

            #------Performing Task/Command Now------#
            if "call" in result["action"] or "guard" in result["action"]:
                self.giyu.giyuTakeDescision(message, self.mood.mood)
            elif "run" in result["action"]:
                await self.runCommand(message, assistant=assist)

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

