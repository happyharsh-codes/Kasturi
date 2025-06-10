from __init__ import*
from src.kellycore.kellymood import KellyMood
from src.kellycore.kellyrelation import KellyRealtion
from src.kellycore.kellypersonality import KellyPersona
from src.kellycore.shiba import Shiba

class Kelly:

    def __init__(self, name, bot):
        self.name = name
        self.client = bot #discord bot
        self.mood = KellyMood()
        self.personality = KellyPersona(Persona)
        self.relations = KellyRealtion(Relation)
        self.chats = Chats
        self.mood.generateRandomMood()
        self.shiba = Shiba()
                
    async def reportError(self, error):
        try:
            me = self.client.get_user(894072003533877279)
            await me.send(f"Erron on KellyCore:{error}")
        except:
            print("Could not dm error")
        print(error)

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

    async def runCommand(self, message, cmd, params):
        ctx = await self.client.get_context(message)
        await ctx.invoke(self.client.get_command(cmd), **params)

    async def kellyQuery(self, message: discord.Message):
        try:
            if self.relations.getUserRelation(message.author.id) == 0:
                #that is user in unknown so Shiba will process the message instead
                addOrNot = await self.shiba.shibaQuery(message, querytype = 1)
                if addOrNot:
                    self.relations.modifyUserRespect(+1, message.author.id)
                return
            
            #------Initializing------#
            mood = self.mood.getMood()
            persona = self.personality.getRequiredPersona()
            relation = self.relations.getUserRelation(message.author.id)
            behave = self.relations.getUserInfo(message.author.id)
            prompt1 = f"""You are Kelly, a Discord Mod (human like lively with mood attitude and sass). Current mood: {mood}, perosna: {persona}, relation: {self.relations.getUserRelation(message.author.id)}, behavior: {{behave}}\nGenerate response in 30 words with emojis"""

            #------Generating message session id------#
            #self.generateSessionId(message)

            #------Sending message------#
            async with message.channel.typing():
                assist = self.getUserChatData(message.author.id) #getting previous chats
                kelly_reply = getResponse(message.content, prompt1, assistant= assist, client=3)
                self.addUserChatData(message.content, kelly_reply, message.author.id) #Saving chat
                await message.reply(self.getEmoji(kelly_reply))  #Replying in channel

            #------Getting Convo summary------#
            cmd = None
            for commands in commandz:
                if commands in message.content:
                    cmd = {commands: commandz[commands]}
                    break
            current_status = {"relation": relation,"mood": mood, "persona": persona}
            prompt2 = f"""You are Kelly/Kasturi kelly discord mod bot(lively with mood attitude and sass)
                Current status: {current_status}
                command: {cmd}
                Generate Json dict using kelly response and mood
                - command_performed: true/false/null(based on mood, tone and task difficulty)
                - command_params: (only when command is not None) (a dict with keys from list values having values from message)
                - respect: +/- (int)
                - mood_change: +/- (int)
                - personality_change: +/- (int)
                - info: optional info about user to store important only: str)"""
            raw_result = getResponse(f"User: {message.content}\nKelly: {kelly_reply}", prompt2, client=2)
            try:
                result = loads(raw_result.split("```json")[1].split('```')[0])
            except Exception as parse_error:
                print("Could not parse AI response:", parse_error) 
                result = {"command_performed": None, "command_params": None, "respect": 0, "mood_change": 0, "personality_change": 0, "info": []}

            #------Performing Task/Command Now------#
            if cmd and result["command_performed"]:
                await self.runCommand(message, cmd, params=result["command_params"])

            #-----Updating Kelly Now-----#
            if isinstance(result["mood_change"], int):
                self.mood.modifyMood({list(mood.keys())[0]: result['mood_change']})
            if isinstance(result["personality_change"], int):
                self.personality.modifyPersonality({list(persona.keys())[0]: result['personality_change']})
            self.relations.modifyUserRespect(result["respect"], message.author.id)
            if "info" in result and result['info']:
                self.relations.addUserInfo(result["info"], message.author.id)

        except Exception as error:
            await self.reportError(error)
        print(f">==<\n{self.mood.mood}\n>==<")

    def chatSummerize(self):
        ChatsCopy = Chats
        prompt = 'summerise user behavior in one single sentence, from the user list of responses'
        for user, chats in ChatsCopy.items():
            if len(chats) > 2:
                Chats.pop(user)
                Behaviours[user] = getResponse(chats, prompt, client=3)

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
            "💪": "kellyfight",
            "🦾": "kellyfight",
            "😁": "kellygigle",
            "🙌": "kellyhandraise",
            "♥": "kellyheart",
            "😬": "kellyhiding",
            "🙄": "kellyidontcare",
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
            "💤": "kellysleeping",
            "😴": "kellysleeping",
            "🛌": "kellysleeping",
            "🤔": "kellythinking",
            "😁": "kellyvibing",
            "🤨": "kellywatching",
            "😗": "kellywatching",
            "🥱": "kellyyawn"
        }
        for emoji, kellyemoji in emoji_exchanger.items():
            if emoji in message:
                message = message.replace(emoji, EMOJI[kellyemoji])
        return message

    def save(self):
        self.relations.save()
        self.personality.save()
        with open("res/kellymemory/chats.json", "w") as f:
            dump(Chats, f, indent=4)

