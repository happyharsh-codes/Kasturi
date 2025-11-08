import random
from __init__ import*

class KellyMood:
    '''#-----Class to handle Kelly Mood-----#
    -mood: {"happy": 1-100, "busy": 1-100, "lazy": 1-100, "sleepy": 1-100}
    the first element in mood is the main current mood trait
    while the first mood may change to different mood traits others are permanent
    
    Mood Traits : ["happy", "sad" , "angry", "annoyed", "depressed", "mischevious", "busy", "sleepy", "lazy"]
    
    '''
    _MOODS = ["happy", "sad" , "angry", "annoyed", "depressed", "mischevious", "busy", "sleepy", "lazy"]
    _OPPOSITE_TRAIT_CHART = {"happy": {"sad", "angry", "annoyed", "depressed"}, "angry": {"happy"}, "sleepy": {"angry", "annoyed", "depressed"}, "lazy": {"depressed", "busy"}, "annoyed": {"happy"}, "busy": {"happy"}, "mischievous": {"sad", "annoyed", "angry"}, "sad": {"happy"}, "depressed": {"happy", "sleepy", "mischievous"} }
    
    def __init__(self, bot):
        self.mood = self.generateRandomMood()
        self.client = bot


    def generateRandomMood(self):
        from random import randint
        mood = {}
        mood["happy"] = randint(30,100)
        mood["busy"] = randint(1,90)
        mood["sleepy"] = randint(1,90)
        mood["lazy"] = randint(1,90)
        mood["sad"] = max(0, 100 - mood["happy"])
        mood["angry"] = 0 # triggered by chatting
        mood["annoyed"] = 0 # triggerede by chatting
        mood["depressed"] = randint(1,25) if mood["sad"] >= 60 else 0
        mood["mischevious"] = randint(1,100)
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
                self.mood[trait] -= mood_change[mood]//2
                if self.mood[trait] < 0:
                    self.mood[trait] = 0

    def moodSwing(self):
        initial_mood = self.getMood()
        for mood, val in self.mood.items():
            if val > 30:
                self.mood[mood] -= randint(1,15)
                if self.mood[mood] < 0:
                    self.modifyMood({mood: randint(0,40)})
        mood_change = self.getMood()
        if mood_change == initial_mood:
            return None
        return mood_change, initial_mood
    
    def getMood(self):
        maxz = max(self.mood.values())
        candidates = [m for m, v in self.mood.items() if v == maxz]
        mood = random.choice(candidates)
        return mood

    def moodToDoTasks(self):
        mood = self.mood
        #Kelly wont perform tasks in these situations
        if mood['busy'] > 80:
            return "busy"
        if mood['sleepy'] > 80:
            return "sleepy"
        if mood['lazy'] > 60:
            return "lazy"
        if mood['mischevious'] > 70:
            return "mischevious"
        if mood['sad'] > 60:
            return "sad"
        if mood['angry'] > 65:
            return "angry"
        if mood["depressed"] > 40:
            return "depressed"
        if mood["annoyed"] > 60:
            return "annoyed"
        return "perform" #finally may perform task
    
    
