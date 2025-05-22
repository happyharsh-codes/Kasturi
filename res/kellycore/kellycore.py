import os, discord
from openai import OpenAI
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage, AssistantMessage
from azure.core.credentials import AzureKeyCredential
from json import load, dump
from random import choice, randint
import time, datetime

class Kelly:

    def __init__(self, name, bot):
        self.name = name
        self.bot = bot #discord bot
        self.last_request = datetime.datetime.now()
        self.client1 = OpenAI(base_url="https://openrouter.ai/api/v1",api_key= os.getenv("KEY"))#ai model connection
        self.client2 = ChatCompletionsClient(endpoint="https://models.github.ai/inference",credential=AzureKeyCredential(os.environ["GITHUB_TOKEN"]))
        self.mood = self.generateMood()
        with open("res/kellycore/kellymemory/personality.json", "r") as f:
            self.personality = load(f)
        with open("res/kellycore/kellymemory/relation.json", "r") as f:
            self.relation = load(f)
    
    def generateMood(self):
        return {"happy":75, "busy": 45, "bored":50, "lazy": 20, "sleepy":5}
    
    def moodChange(self, change_dict):
        if change_dict is None:
            return
        mood = self.mood
        for items, values in change_dict.items():
            mood[items] += values
        self.mood = mood
                
    async def reportError(self, error):
        try:
            me = self.bot.get_user(894072003533877279)
            await me.send(f"Erron on KellyCore:{error}")
        except:
            pass
        print(error)

    def getResponse(self, usermessage, prompt, assistant=""):
        messages= [SystemMessage(prompt)]
        messages2 = [{"role":"system","content": prompt}]
        
        if assistant != "":
            #adding history
            for msg in assistant.split("\n"):
                user = msg.split(":")
                if user[0] == "User":
                    messages.append(UserMessage(user[1]))
                    messages2.append({"role":"user","content":user[1]})
                else:
                    messages.append(AssistantMessage(user[1]))
                    messages2.append({"role":"assistant","content":user[1]})
        #adding current message
        messages.append(UserMessage(usermessage))
        messages2.append({"role":"user","content": usermessage})
        response = self.client1.chat.completions.create(
                model= "deepseek/deepseek-chat-v3-0324:free",
                messages= messages2,
                max_tokens=200,
                top_p=1.0
        )
        if response.choices is None:
            print("Model Changed")
            response = self.client2.complete(
            messages= messages,
            temperature=1.0,
            top_p=1.0,
            max_tokens=200,
            model= "deepseek/DeepSeek-V3-0324"
            )
        return response.choices[0].message.content

    def get_relation_status(self, userid):
        status = self.relation.get(userid)
        if status is None:
            return {"respect": 0, "friend": False, "unknown": True}
        return status
    
    def userRespect(self, respect, id):
        if not str(id) in self.relation:
            self.relation[str(id)] = {"respect": respect, "friend": False}
        else:
            self.relation[str(id)]["respect"] += respect

    def userFriend(self, friend, id):
        if not str(id) in self.relation:
            self.relation[str(id)] = {"respect": 0, "friend": False}
        if friend:
            self.relation[str(id)]["friend"] = True

    def modify_persona(self, persona_change, id):
        persona = self.personality
        for type in persona_change:
            persona[type] += persona_change[type]
        self.personality = persona

    def getUserChatData(self, userid):
        with open("res/kellycore/kellymemory/chats.json", "r") as f:
            chats = load(f)
            if str(userid) in chats:
                all_user_chats = chats[str(userid)]
                res = "\n".join(all_user_chats)
                return res
            return ""

    def addUserChatData(self, user_message, kelly_message, id):
        with open("res/kellycore/kellymemory/chats.json", "r") as f:
            chats = load(f)
        with open("res/kellycore/kellymemory/chats.json", "w") as f:
            if str(id) not in chats:
                chats[str(id)] = [f"User:{user_message}\nKelly:{kelly_message}"]
            else:
                chats[str(id)].append(f"User:{user_message}\nKelly:{kelly_message}")
                if len(chats[str(id)]) > 8:
                    chats[str(id)].pop(0)
            dump(chats, f, indent=4)

    async def kellyQuery(self, message: discord.Message):
        try:
            start = time.time()
            current_state = {"mood": self.mood, "personality": self.personality, "relation": self.get_relation_status(message.author.id)}
            prompt1 = f"""You are Kelly, a Discord Mod with human-like attitude and emotional states.
                Your State:{current_state}
                Use state for analysis
                Respond naturally (under 50 words) in Kelly's voice.(no block no emoji)"""
            tasks = {"none":0, "ban":50, "mute":4, "unmute":10, "unban": 60, "deafen": 4, "add yt": 4, "rank": 5, "cash": 4, "beg": 5, "github": 10, "help": 1, "kick": 4, "play": 50, "pat": 90} 

            #------Sending message------#
            if message.reference: 
                assist = self.getUserChatData(message.author.id)
            else:
                assist = ""
            kelly_reply = self.getResponse(message.content, prompt1, assistant= assist)
            print("Kelly Responded with:", kelly_reply)
            self.addUserChatData(message.content, kelly_reply, message.author.id) #Saving chat
            msg = await message.reply(kelly_reply)  #Replying in channel
            emoji = self.getEmoji(message.content, kelly_reply) #Updating reply with an emoji afterwarder bcoz model takes time in each request
            if randint(1,2) == 1:
                await message.channel.send(emoji)
            else:
                await msg.edit(content= kelly_reply + " " + emoji)

            #------Getting Convo summary------#
            prompt2 = f"""You are Kelly, a Discord Mod with human-like attitude and emotional states
                Kelly state: {current_state}
                Task list: {list(tasks.keys())}
                Task generate response based on kelly state:
                Then return a PYTHON block with:
                - task: (task from task list None if not any)
                - task_performed: True/False/None(if no task)
                - satisfaction: 1–100
                - relation_change: {{ respect: +/-N, friend: True/False, unknown: False }}
                - mood_change: {{happy, busy, lazy, sleepy: +/-N}}
                - personality_change: {{duty, mischevious: +/-N}}
                - info: [optional info about user to store important only]"""
            #raw_result = self.getResponse("", prompt2, f"User: {message.content}\nKelly: {kelly_reply}")
            raw_result = self.getResponse(f"User: {message.content}\nKelly: {kelly_reply}", prompt2)
            print("1: ", raw_result)
            #print("2: ", raw_result_2)

            try:
                result = raw_result.split("```python")
                result = result[1].replace("```", "").replace("\n","").replace("false", "False").replace("true", "True").replace("none", "None")
                result = eval(result, {"__builtins__": {}})
            except Exception as parse_error:
                print("Could not parse AI response:", parse_error) 
                result = {"task": None, "task_performed": False, "satisfaction": randint(1,100), "relation_change": {"respect": 0, "friend": False}, "mood_change": {}, "personality_change": {}, "info": []}

            #-----Updating Kelly Now-----#
            if result["satisfaction"] >= 50:
                self.userRespect(+2, message.author.id)
            self.modify_persona(result["personality_change"], message.author.id)
            self.moodChange(result["mood_change"])
            self.userRespect(result["relation_change"]["respect"], message.author.id)
            self.userFriend(result["relation_change"]["friend"], message.author.id)

            #------Performing Task/Command Now------#
            if result["task"] is not None:
                if result["task_performed"]:
                    pass
        
        except Exception as error:
            await self.reportError(error)
        print("Latency: ", time.time()-start)
        self.logTask(datetime.datetime.now(), message, kelly_reply, result)

    def getEmoji(self, user_message, kelly_message):
        emoji = ["tired","acting","annoyed","blush","bored","bweh","cheekspull","chips","cry","droolling","embaress","fight","gigle","handraise","heart","hiding","idontcare","interesting","juice","laugh","ok","owolove","pat","popcorn","salute","simping","sleeping","thinking","vibing","watching","yawn"]
        prompt = f"Select one emoji from the list based on user message and kelly response\n{emoji}\nResponse should be only single element from list"
        reply_emoji = self.getResponse("kelly:" + kelly_message, prompt)
        if reply_emoji not in emoji:
            print("selected random emoji")
            reply_emoji = choice(emoji)
        with open("assets/info.json", "r") as f:
            data = load(f)
        return data["emoji"]["kelly" + reply_emoji]

    def save(self):
        with open("res/kellycore/kellymemory/reation.json", "w") as f:
            dump(self.relation, f, indent=4)
        with open("res/kellycore/kellymemory/personality.json", "w") as f:
            dump(self.personality, f, indent=4)

    def logTask(self,time, message, reply, result):
        with open("res/kellycore/kellymemory/perfomedTasksLog.json", "r") as f:
            data = load(f)
        with open("res/kellycore/kellymemory/perfomedTasksLog.json", "w") as f:
            data[time] = f"{time.strftime('%Y-%m-%d %H:%M:%S')}\n{message.author.name}({message.author.id}): {message.content}\n{self.name}: {reply}\nResult: {result}"
            dump(data, f, indent=4)
