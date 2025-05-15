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

    async def reportError(self, error):
        try:
            me = self.bot.get_user(894072003533877279)
            await me.send(f"Erron on KellyCore:{error}")
        except:
            pass
        print(error)


    def getResponse(self, message):
        return self.client.chat.completions.create(
            model="deepseek/deepseek-prover-v2:free",
            messages=message,
            max_tokens=200,
        ) 

    def get_relation_status(self, userid):
        status = self.relation.get(userid)
        if status is None:
            return {"respect": 0, "friend": False, "unknown": True}
        return status

    def kellyTalk(self, message, reply_to=None):
        """Normal chit-chat with kelly. Returns a response string and modifies Kelly moods and user relation"""
        kelly_state = {"mood": self.mood, "personality": self.personality, "relation": self.get_relation_status(message.author.id)}
        system_prompt = f"""
        You are Kelly, an human, does all‑purpose Discord work with attitude and mood.
        Current Mood: {kelly_state}
        1. Generate reply in less than 50 words
        2. Add Json code with variables: satisfaction: 1-100, friend: True if added friend no else no change, respect: 1-100, <mood_type>:1-100
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
        satisfaction = resp
        msg = resp.choices[0].message.content.strip() #response talk that kely sent
        try:
            data = msg[msg.index("{"):]
            msg = msg[:msg.index("{")]
        except ValueError:
            data = {"satisfaction": random.randint(1,100), "relation_change": {"respect": random.randint(-10,10)},"mood_change": {"happy": random.randint(1,100)}}
        print(f"Kelly TALK EXPERIENCE: {resp.choices[0].message.content}")
        return msg

    def kellyDecide(self, userid, difficulty):
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

    async def kellyPerform(self,task, difficulty, userid, message):
        '''Decides and then performst the task'''
        kelly_state = {"mood": self.mood, "personality": self.personality, "relation": self.get_relation_status(userid)}

        system_prompt = f"""
        You are Kelly, an all‑purpose Discord bot with attitude and mood.
        Current state: {kelly_state}

        When the user asks you to do a task of difficulty {{difficulty}}:
        1. Decide whether to do it using the state variables.
        2. Reply in 50 words or fewer, with Kelly’s characteristic tone.
        3. Then output a JSON with keys:
        - task_performed: True/False
        - satisfaction: 0–100 (how Kelly feels after)
        - relation_change: {{…}}
        - mood_change: {{…}}
        """
        try:
            # 1. Compose messages
            messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Task: {task} (difficulty: {difficulty})"},
            ]

            # 2. Call the model
            resp = self.getResponse(messages)
            # 3. Parse the reply
            text = resp.choices[0].message.content.strip()
            print(text)
            # split into reply and JSON summary
            # parts = text.rsplit("```json", 1)
            # reply_text = parts[0].strip()
            # summary_json = parts[1].strip().strip("```").strip()
            try:
                data = text[text.index("{"):]
                result = eval(data, {"__builtins__": {}})
                if isinstance(result, dict):
                    task_performed = result.get("task_performed", "none").lower()
            except Exception as parse_error:
                print("Could not parse AI response:", parse_error)
            decision = self.kellyDecide(userid, difficulty)
            print("kelly descision: ", decision)
            await messages.reply(text[:text.index("{")])

            if task_performed:
                print("Kelly accepted to perform: ", task)
                ctx = await self.bot.get_context(message)
                command = self.bot.get_command(task)  # use your actual command name here
                if command:
                    await ctx.invoke(command)
                else:
                    await message.reply(f"Command {task} not found.")
            
            #Now adjusting mood change and relation change
            

        except Exception as e:
            await self.reportError(e)

    def kellyRequest(self, message):
        pass

    async def kellyProcess(self, message):
        try:
            tasks = {"ban": 20, "mute": 4, "kick": 5}
            system_prompt = f"""
            You are task(from list {list(tasks.keys())}) and tone finder
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
            for i in (tasks.keys()):
                if i in message_without_prefix:
                    task = i
            user_tone = "told"
            try:
                result = eval(text, {"__builtins__": {}})
                if isinstance(result, dict):
                    task = result.get("task", "none").lower()
                    user_tone = result.get("user_tone", "told").lower()
            except Exception as parse_error:
                print("Could not parse AI response:", parse_error)
            print(f"Kelly scanned message -> task: {task}, tone: {user_tone}, msg: {message.content}")
            if task == "none":
                original = await message.channel.fetch_message(message.reference.message_id)
                with open("res/server/server_settings.json", "r") as f:
                    data = load(f)
                if data.get(str(message.guild.id), {}).get("allowed_channels", []) == []:
                    return
                if original.author.id == self.bot.user.id:
                    await message.reply(self.kellyTalk(message,reply_to=original))
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


    def kellyUpdate(self, updates):
        pass

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