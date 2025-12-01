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
    _OPPOSITE_TRAIT_CHART = {"happy": {"sad", "angry", "annoyed", "depressed"}, "angry": {"happy"}, "sleepy": {"angry", "annoyed", "depressed"}, "lazy": {"depressed"}, "annoyed": {"happy"}, "mischievous": {"sad", "annoyed", "angry"}, "sad": {"happy"}, "depressed": {"happy", "sleepy", "mischievous"} }
    
    def __init__(self, bot):
        self.mood = self.generateRandomMood()
        self.client = bot


    def generateRandomMood(self):
        from random import randint
        mood = {}
        mood["happy"] = 100
        mood["sleepy"] = 0
        mood["lazy"] = 0
        mood["sad"] = 0
        mood["angry"] = 0 # triggered by chatting
        mood["annoyed"] = 0 # triggerede by chatting
        mood["depressed"] = 0
        mood["mischievous"] = 0
        print(mood)
        return mood
    
    def modifyMood(self, mood_change):
        for mood in mood_change:
            self.mood[mood] += mood_change[mood]
            if self.mood[mood] > 100:
                self.mood[mood] = 100
            elif self.mood[mood] < 0:
                self.mood[mood] = 0
            for trait in self._OPPOSITE_TRAIT_CHART[mood]:
                self.mood[trait] -= mood_change[mood]
                if self.mood[trait] < 0:
                    self.mood[trait] = 0

    def moodSwing(self):
        initial_mood = self.getCurrentMood()
        depreciating_moods = ["sleepy", "lazy", "happy", "annoyed", "mischievous"]
        for mood in depreciating_moods:
            self.mood[mood] -= 5
            if self.mood[mood] < 0:
                self.mood[mood] = 0
                if mood == "happy":
                    self.mood["sad"] = 100
                elif mood == "lazy":
                    self.mood[choice(["happy", "mischievous"])] = 100
                elif mood == "mischievous":
                    self.mood["lazy"] = 100
                elif mood == "sleepy":
                    self.mood[choice(["happy", "lazy"])] = 100
                elif mood == "annoyed":
                    self.mood["happy"] = 100
        mood_change = self.getCurrentMood()
        if mood_change == initial_mood:
            return None
        return mood_change, initial_mood
    
    def getCurrentMood(self):
        maxz = max(self.mood.values())
        candidates = [m for m, v in self.mood.items() if v == maxz]
        if len(candidates) == 1:
            return candidates[0]
        for mood in self._MOODS:
            if mood in candidates:
                return mood
                
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
    
    
