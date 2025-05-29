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

    async def kellyQuery(self, message: discord.Message):
        try:
            if self.relations.getUserRelation(message.author.id) == 0:
                #that is user in unknown so Shiba will process the message instead
                addOrNot = await self.shiba.shibaQuery(message, querytype = 1)
                if addOrNot:
                    self.relations.modifyUserRespect(+1, message.author.id)
                return
            
            #------Initializing------#
            start = time.time()
            mood = self.mood.getMood()
            persona = self.personality.getRequiredPersona()
            prompt1 = f"""You are Kelly, a Discord Mod Bot kelly discord mod bot(lively with mood attitude and sass). Current mood: {mood}, perosna: {persona}, relation: {self.relations.getUserRelation(message.author.id)}, behavior: {{}}\nGenerate response in 30 words"""
            tasks = {"none":0, "ban":50, "mute":4, "unmute":10, "unban": 60, "deafen": 4, "add yt": 4, "rank": 5, "cash": 4, "beg": 5, "github": 10, "help": 1, "kick": 4, "play": 50, "pat": 90} 

            #------Generating message session id------#
            #self.generateSessionId(message)

            #------Sending message------#
            async with message.channel.typing():
                assist = self.getUserChatData(message.author.id) #getting previous chats
                kelly_reply = getResponse(message.content, prompt1, assistant= assist, client=3)
                self.addUserChatData(message.content, kelly_reply, message.author.id) #Saving chat
                msg = await message.reply(kelly_reply)  #Replying in channel
            emoji = self.getEmoji(message.content, kelly_reply) #Updating reply with an emoji afterwarder bcoz model takes time in each request
            if randint(1,2) == 1:
                await message.channel.send(emoji)
            else:
                await msg.edit(content= kelly_reply + " " + emoji)

            #------Getting Convo summary------#
            prompt2 = f"""You are Kelly/Kasturi kelly discord mod bot(lively with mood attitude and sass)
                Generate Json dict using kelly response and mood
                - task: (task detected from convo/ null)
                - task_performed: True/False/None(if no task)
                - respect: +/- (int)
                - mood_change: +/- (int)
                - personality_change: +/- (int)
                - info: [optional info about user to store important only]"""
            raw_result = getResponse(f"User: {message.content}\nKelly: {kelly_reply}", prompt2, client=2)
            try:
                result = loads(raw_result.split("```json")[1].split('```')[0])
            except Exception as parse_error:
                print("Could not parse AI response:", parse_error) 
                result = {"task": None, "task_performed": False, "respect": 0, "mood_change": 0, "personality_change": 0, "info": []}

            #-----Updating Kelly Now-----#
            self.mood.modifyMood({list(mood.keys())[0], result['mood_change']})
            self.personality.modifyPersonality({list(persona.keys())[0]: result['personality_change']})
            self.relations.modifyUserRespect(result["respect"], message.author.id)

            #------Performing Task/Command Now------#
            if result["task"] in tasks:
                if self.kellyDecide(result['task']):
                    message.content = ""
                else:
                    print(f"Kelly refused to perform {result['task']} requested by {message.author.name} at {time.time()}")
        except Exception as error:
            await self.reportError(error)
        print("Latency: ", time.time()-start)
        self.logTask(datetime.now(), message, kelly_reply, result)

    def chatSummerize(self):
        ChatsCopy = Chats
        prompt = 'summerise user behavior in one single sentence, from the user list of responses'
        for user, chats in ChatsCopy.items():
            if len(chats) > 2:
                Chats.pop(user)
                Behaviours[user] = getResponse(chats, prompt, client=3)

    def getEmoji(self, user_message, kelly_message):
        emoji = ["tired","acting","annoyed","blush","bored","bweh","cheekspull","chips","cry","droolling","embaress","fight","gigle","handraise","heart","hiding","idontcare","interesting","juice","laugh","ok","owolove","pat","popcorn","salute","simping","sleeping","thinking","vibing","watching","yawn"]
        prompt = f"Select one emoji from the list based on user message and kelly response and RETUTN SINGLE ELEMENT (NO BLOCK)\nList: {emoji}"
        reply_emoji = getResponse("kelly:" + kelly_message, prompt, client=2)
        for emj in emoji:
            if emj in reply_emoji:
                return EMOJI["kelly" + emj]
        else:
            print("selected random emoji")
            emj = choice(emoji)
            return EMOJI["kelly" + emj]

    def save(self):
        self.relations.save()
        self.personality.save()
        with open("res/kellymemory/chats.json", "w") as f:
            dump(Chats, f, indent=4)
        with open("res/kellymemory/logs.json", "w") as f:
            dump(Logs, f, indent=4)
        with open("res/kellymemory/behaviors.json", "w") as f:
            dump(Behaviours, f, indent=4)

    def logTask(self,time, message, reply, result):
        Logs[time.strftime('%Y-%m-%d %H:%M:%S')] = f"{time.strftime('%Y-%m-%d %H:%M:%S')}\n{message.author.name}({message.author.id}): {message.content}\n{self.name}: {reply}\nResult: {result}"
