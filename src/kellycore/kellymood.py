import random
from __init__ import*

class KellyMood:
    '''#-----Class to handle Kelly Mood-----#
    -mood: {"happy": 1-100, "lazy": 1-100, "sleepy": 1-100}
    the first element in mood is the main current mood trait
    while the first mood may change to different mood traits others are permanent
    
    Mood Traits : ["happy", "sad" , "angry", "annoyed", "depressed", "mischievous", "sleepy", "lazy"]
    
    '''
    _MOODS = ["depressed", "sleepy", "annoyed", "angry", "lazy", "sad", "mischievous", "happy"]
    _OPPOSITE_TRAIT_CHART = {"happy": "sad", "angry": "annoyed", "sleepy": "depressed", "lazy": "mischievous", "annoyed": "angry", "mischievous": "lazy", "sad": "happy", "depressed": "sleepy" }
    
    def __init__(self, bot, kelly):
        self.mood = self.generateRandomMood()
        self.client = bot
        self.kelly = kelly

    def getMood(self):
        return max(self.mood, key=self.mood.get)
                
    def generateRandomMood(self):
        from random import randint
        mood = {}
        mood["happy"] = randint(1,100)
        mood["sleepy"] = randint(1,100)
        mood["lazy"] = randint(1,100)
        mood["sad"] = 100 - mood["happy"]
        mood["angry"] = 0 # triggered by chatting
        mood["annoyed"] = 0 # triggerede by chatting
        mood["depressed"] = 100 - mood["sleepy"]
        mood["mischievous"] = 100 - mood["lazy"]
        print(mood)
        return mood

    async def setStatus(self):
        prev_mood = self.kelly.status
        self.kelly.status = self.getMood()
        new_mood = self.kelly.status
        mood_shift = None
        action = {"happy": "-# Kelly is so haply now 😃","sleepy": "-# Kelly is sleeping 😴","depressed": "-# Kelly is depressed 😔","angry": "-# Kelly is angry 😡","annoyed": "-# Kelly is very annoyed right now 😣","lazy": "-# Kelly is too lazy to respond now 😪","sad": "-# Kelly is so sad right now 😭","mischievous": "-# Kelly is feeling a little mischievous 😉", "woke_up": "-# Kelly just woke up 🤤", "went_to_sleep": "-# Kelly is sleeping now 🛏️"} 
        if new_mood == prev_mood:
            return
        if prev_mood == "sleepy":
            mood_shift = "woke_up"
        elif new_mood == "sleepy":
            mood_shift = "went_to_sleep"
        else:
            mood_shift = new_mood
        
        for gid, settings in Server_Settings.items():
            if not settings["last_message"]:
                continue
            channel = self.client.get_channel(settings["last_message"])
            if not channel:
                try:
                    channel = self.client.fetch_channel(settings["last_message"])
                except:
                    continue
            if settings["timer_messages"]:
                reply = None
                if randint(1,25) == 3:
                    text = "Kelly got to revive the ded chat"
                    prompt = "Roleplay Kelly, a cute Discord Mod (human like with mood and sass). Generate response activating ded chat in 20 words with 1-4 emojis"
                    loop = asyncio.get_event_loop()
                    response = await loop.run_in_executor(None, getResponse, text, prompt, "", 0)
                    reply = self.kelly.kellyEmojify(response)
                if reply:
                    await channel.send(reply)
            if mood_shift:
                await channel.send(self.kelly.kellyEmojify(action[mood_shift]), delete_after=120)
                await channel.send(self.kelly.kellyEmojify(DATA["kelly_responses"]["mood_flex"][mood_shift]), delete_after=150)
    
    async def modifyMood(self, mood_change):
        for mood in mood_change:
            self.mood[mood] += mood_change[mood]
            if self.mood[mood] > 100:
                self.mood[mood] = 100
            elif self.mood[mood] < 0:
                self.mood[mood] = 0
            trait = self._OPPOSITE_TRAIT_CHART.get(mood)
            if trait:
                self.mood[trait] -= mood_change[mood]
                if self.mood[trait] < 0:
                    self.mood[trait] = 0
                if self.mood[trait] > 100:
                    self.mood[trait] = 100
        await self.setStatus()
        
    async def moodSwing(self):
        for mood in self.mood:
            if mood in ["sad", "depressed", "angry", "annoyed"] and randint(1,2) != 2:
                continue
            self.mood[mood] -= randint(1, 7)
            if self.mood[mood] < 0:
                if mood == "sleepy":
                    self.mood[mood] = 0
                else:
                    self.mood[mood] = randint(91,100)
        await self.setStatus()
        print(f"===== MOOD SWING =====\n{self.mood}, {self.kelly.status}")
    
    def moodToDoTasks(self):
        mood = self.mood
        #Kelly wont perform tasks in these situations
        if mood['sleepy'] > 90:
            return "sleepy"
        if mood['lazy'] > 60:
            return "lazy"
        if mood['mischievous'] > 70:
            return "mischievous"
        if mood['sad'] > 60:
            return "sad"
        if mood['angry'] > 65:
            return "angry"
        if mood["depressed"] > 40:
            return "depressed"
        if mood["annoyed"] > 60:
            return "annoyed"
        return "perform" #finally may perform task
    
    
