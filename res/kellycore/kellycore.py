import os 
from openai import OpenAI
from json import load, dump
import random

class Kelly:

    def __init__(self, name, bot):
        self.name = name
        self.bot = bot #discord bot
        self.client = OpenAI(base_url="https://openrouter.ai/api/v1",api_key= os.getenv("KEY"),)#ai model connection
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
            mood[items] = values
        self.mood = mood
                
    async def reportError(self, error):
        try:
            me = self.bot.get_user(894072003533877279)
            await me.send(f"Erron on KellyCore:{error}")
        except:
            pass
        print(error)


    def getResponse(self, message):
        model_request = self.client.chat.completions.create(
            model="deepseek/deepseek-prover-v2:free",
            messages=message,
            max_tokens=200,
        )
        if model_request.choices is None:
            self.client.base_url = "https://api.together.xyz/v1"
            self.client.api_key = os.getenv("KEY2")
            model_request = self.client.chat.completions.create(
                model="openchat/openchat-3.5-1210:free",
                messages=message,
                max_tokens=200,
            )
        return model_request

    def get_relation_status(self, userid):
        status = self.relation.get(userid)
        if status is None:
            return {"respect": 0, "friend": False, "unknown": True}
        return status
    
    def modify_realtion(self, relation_change, id):
        relation = self.relation
        for type in relation_change:
            if type == "respect":
                relation[str(id)]["respect"] += relation_change[type]
            elif type == "friend" or type == "unknown":
                relation[str(id)["friend"]] = relation_change[type]
        self.relation = relation

    def modify_persona(self, persona_change, id):
        persona = self.personality
        for type in persona_change:
            persona[type] = persona_change[type]
        self.personality = persona

    def kellyTalk(self, message, reply_to=None):
        """Normal chit-chat with kelly. Returns a response string and modifies Kelly moods and user relation"""
        mood = ["happy", "busy", "lazy", "sleepy"]
        personality = ["duty", "mischevious", "intelligent", "curious"]
        essential_mood = {k: v for k, v in self.mood.items() if k in ["happy", "lazy", "sleepy"]}
        essential_traits = {k: v for k, v in self.personality.items() if k in ["duty", "mischevious"]}
        relation = self.get_relation_status(message.author.id)
        current_state = {"mood": essential_mood, "personality": essential_traits, "relation": relation}
        system_prompt = f"""You are Kelly, a Discord bot with human-like attitude and emotional states.
            Current State:{current_state}
            Task:
            1. Respond naturally (under 50 words) in Kelly's voice.(no emoji)
            2. Then return a JSON block with:
            - satisfaction: 1–100
            - relation_change: {{ respect: +/-N, friend: true/false, unknown: false }}
            - mood_change: {mood}
            - personality_change: {personality}

            Separate the response and JSON clearly.
        """
        messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": message.content},
        ]
        if reply_to is not None:
            messages.append({"role": "assistant", "content": f"Previous msg by Kelly: {reply_to.content}"})

        # Call the model
        resp = self.getResponse(messages)

        # Setting talk experience
        # changing kelly mood and kelly relation
        text = resp.choices[0].message.content.strip() #response talk that kely sent
        print(f"Kelly TALK EXPERIENCE: {text}")
        response = (text.split("```python"))[0] + (text.split("```"))[1]
        json_data = (text.split("```python"))[1].replace("false", "False").replace("true", "True").replace("null", "None")
        try:
            result = eval(json_data, {"__builtins__": {}})
        except Exception as parse_error:
            print("Could not parse AI response:", parse_error)
            result = {"satisfaction": random.randint(1,100)," relation_change": {"respect": random.randint(-10,10)}, "mood_change": {"happy": random.randint(1,100)}}

        #Now adjusting mood change and relation change
        try:
            if result["satisfaction"] > 50:
                self.modify_realtion("respect", +2)
            self.moodChange(result["mood_change"])
            self.modify_realtion(result["relation_change"], message.author.id)
            self.modify_persona(result["personality_change"])
        except Exception as e:
            print("Unable to update kelly on talk: ", e)
        emoji = self.kellyEmojiGenerator(response)
        return f"{emoji} **|** {response}"

    #def kellyDecide(self, userid, difficulty):
        # e.g. higher lazy → less likely, higher duty → more likely
        # e.g. higher sleepy → very less likely irrespective duty
        relation = self.get_realtion_status(userid)
        score = (
            +self.personality["duty"]              * 0.4
            -self.personality["mischevious"]       * 0.2
            +self.mood["happy"]                    * 0.3
            -self.mood["lazy"]                     * 0.4
            -difficulty                            * 0.1
            +(relation["respect"])                 * 0.2
        )
        if relation["friend"]:
            score += relation['respect'] * 0.2
        return score > difficulty # threshold you tune

    async def kellyPerform(self, task, difficulty, userid, message):
        '''Decides and then performst the task'''
        mood = ["happy", "busy", "lazy", "sleepy"]
        personality = ["duty", "mischevious", "intelligent", "curious"]
        current_state = {"mood": self.mood, "personality": self.personality, "relation": self.get_relation_status(message.author.id)}
        system_prompt = f"""You are Kelly, a Discord bot with human-like attitude and emotional states.
            Current State:{current_state}
            Task:
            1. Respond naturally (under 50 words) in Kelly's voice.(no emoji)
            2. Then return a PYTHON block with:
            - task_performed: True/False (decide based on difficulty,mood,realtion and personality)
            - satisfaction: 1–100
            - relation_change: {{ respect: +/-N, friend: True/False, unknown: False }}
            - mood_change: {mood}
            - perosnality_change: {personality}

            Separate the response and JSON clearly.
        """
        # 1. Compose messages
        messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Task: {task} (difficulty: {difficulty}), message: {message.content}"}
        ]
        # 2. Call the model
        resp = self.getResponse(messages)
        # 3. Parse the reply
        text = resp.choices[0].message.content.strip()
        print("Task perform request: ",text)
        response = (text.split("```python"))[0] + (text.split("```"))[1]
        json_data = (text.split("```python"))[1].replace("false", "False").replace("true", "True").replace("null", "None")
        try:
            result = eval(json_data, {"__builtins__": {}})
        except Exception as parse_error:
            print("Could not parse AI response:", parse_error)
            result = {"task_performed":False, "satisfaction": random.randint(1,100)," relation_change": {"respect": random.randint(-10,10)}, "mood_change": {"happy": random.randint(1,100)}}
        await messages.reply(f"{self.kellyEmojiGenerator(response)} **|** {response}")

        if result["task_performed"]: # means kelly decided to perform the task
            print("Kelly accepted to perform: ", task)
            ctx = await self.bot.get_context(message)
            command = self.bot.get_command(task)  # use your actual command name here
            if command:
                await ctx.invoke(command)
            else:
                await message.reply(f"Command {task} not found.")
        
        #Now adjusting mood change and relation change
        try:
            if result["satisfaction"] > 50:
                self.modify_realtion("respect", +2)
            self.moodChange(result["mood_change"])
            self.modify_realtion(result["relation_change"], message.author.id)
            self.modify_persona(result["personality_change"])
        except Exception as e:
            print("Coudn't update Kelly: ", e)

    async def kellyProcess(self, message):
        try:
            tasks = {"ban": 20, "mute": 4, "kick": 5}
            system_prompt = f"""
            You are task (from list {list(tasks.keys())}) and tone finder
            Response MUST be like -> {{'task': 'none', 'user_tone': 'asked/told/ordered/requested'}}
            """
            message_without_prefix = message.content.lower()
            for prefix in ("kasturi ","kasturi","kelly ","kelly","k ","k"):
                if prefix in message.content.lower():
                    message_without_prefix = message.content.lower().replace(prefix, "")
                    break
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message_without_prefix}
            ]
            resp = self.getResponse(messages)
            text = resp.choices[0].message.content.strip()
            print(f"LLM responded with: {text}")
            # Try to parse the text as a dictionary safely
            task = "none"
            for i in (tasks.keys()):
                if i in message_without_prefix:
                    task = i
                    break
            user_tone = "told"
            try:
                json_data = (task.split("```")[1]).replace("python","").replace("json", "").replace("\n", "")
                result = eval(json_data, {"__builtins__": {}})
                if isinstance(result, dict):
                    task = result.get("task", "none").lower()
                    user_tone = result.get("user_tone", "told").lower()
            except Exception as parse_error:
                print("Could not parse AI response:", parse_error)
            print(f"Kelly scanned message -> task: {task}, tone: {user_tone}, msg: {message.content}")
            if task == "none":
                if message.reference:
                    original = await message.channel.fetch_message(message.reference.message_id)
                    if original.author.id == self.bot.user.id:
                        await message.reply(self.kellyTalk(message,reply_to=original))
                        return
                with open("res/server/server_settings.json", "r") as f:
                    data = load(f)
                if data.get(str(message.guild.id), {}).get("allowed_channels", []) == []:
                    return
                if "kelly" not in message.content.lower():
                    return
                response = self.kellyTalk(message)
                await message.reply(response)
            else:
                tone_difficulty_increase = {
                    "asked": 5,
                    "requested": -10,
                    "ordered": 15,
                    "told": 2
                }.get(user_tone, 0)

                if self.personality.get("sleepy", 0) >= 82:
                    await message.reply("User, Kelly is very sleepy right now, so she won’t!")
                    return
                if self.personality.get("lazy", 0) >= 83:
                    await message.reply("User, Kelly is very lazy right now, so she won’t!")
                    return

                print(f"Kelly Task Perform Requested: {task}, Base: {tasks.get(task, 0)}")
                await self.kellyPerform(task, tasks.get(task, 0) + tone_difficulty_increase, message.author.id, message)

        except Exception as e:
            print("Error in kellyProcess:", e)
            await self.reportError(e)

    def kellyEmojiGenerator(self, context):
        emotions = ["acting", "annoyed", "blush", "bored", "bweh", "cheekspull", "chips", "cry", "drooling", "embaress", "fight", "giggle", "handraise", "heart", "hiding", "idontcare", "interesting", "juice", "laugh", "ok", "owolove","pat", "popcorn", "salute", "simping", "sleeping", "thinking", "tired", "vibing", "waiting", "watching", "yawn"]

        message = [
        {"role": "system", "content": f"You are Kelly, a Discord bot with human-like attitude and emotional states. Current mood: {self.mood} select one emotion from the list and reply only the emotion name Nothing else. {emotions}"},
        {"role": "user", "content": context},
        ]
        emoji = self.getResponse(message)
        emoji = emoji.choices[0].message.content
        print("ai choose emoji: ", emoji)
        if emoji not in emotions:
            emoji = random.choice(emotions)
        return emoji

    def save(self):
        with open("res/kellycore/kellymemory/reation.json", "w") as f:
            dump(self.relation, f, indent=4)
        with open("res/kellycore/kellymemory/personality.json", "w") as f:
            dump(self.personality, f, indent=4)

    def kellyLogTask(self,time, name, realtion_change, mood_change):
        with open("res/kellycore/kellymemory/perfomedTasksLog.json", "w") as f:
            data = load(f)
            data[time] = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {self.name} performed a task - {name}. Relationship Updates: {realtion_change} Mood change: {mood_change}" 
            dump(data)