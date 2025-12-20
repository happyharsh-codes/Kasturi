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

    def setStatus(self):
        if self.mood["sleepy"] > 90:
            self.kelly.status = "sleeping"
        elif self.mood["lazy"] > 90:
            self.kelly.status = "lazy"
        elif self.mood["mischievous"] > 90:
            self.kelly.status = "mischievous"
        else:
            self.kelly.status = "active"
    
    def modifyMood(self, mood_change):
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
        self.setStatus()
        
    def moodSwing(self):
        initial_mood = self.getMood()
        for mood in self.mood:
            if mood in ["mischievous", "lazy", "sad", "depressed", "angry", "annoyed"] and randint(1,2) != 3:
                continue
            self.mood[mood] -= randint(1, 7)
            if self.mood[mood] < 0:
                if mood == "sleepy":
                    self.mood[mood] = 0
                else:
                    self.mood[mood] = randint(91,100)
        final_mood = self.getMood()
        self.setStatus()
        print(f"===== MOOD SWING =====\n{self.mood}, {self.kelly.status}")
        return final_mood, initial_mood
    
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
    
    
