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

    def __init__(self, bot):
        self.mood = self.generateRandomMood()
        self.client = bot


    def generateRandomMood(self):
        from random import randint
        mood = {}
        mood["happy"] = randint(1,100)
        mood["busy"] = randint(1,100)
        mood["sleepy"] = randint(1,100)
        mood["lazy"] = randint(1,100)
        mood["sad"] = 100 - mood["happy"]
        mood["angry"] = 0 # triggered by chatting
        mood["annoyed"] = 0 # triggerede by chatting
        if mood["sad"] >= 60:
            mood["depressed"] = randint(1,20)
        else: 
            mood["depressed"] = 0
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
            if mood == "happy":
                opposite_traits = ["sad", "depressed", "angry", "annoyed"]
                for trait in opposite_traits:
                    self.mood[trait] -= mood_change[mood]
                    if self.mood[trait] < 0:
                        self.mood[trait] = 0
            elif mood in ["sad", "depressed", "angry", "annoyed"]:
                self.mood["happy"] -= mood_change[mood]
                if self.mood["happy"] < 0:
                    self.mood["happy"] = 0
            elif mood in ["depressed"]:
                self.mood["sleepy"] -= mood_change[mood]
                if self.mood["sleepy"] < 0:
                    self.mood["sleepy"] = 0

    def moodSwing(self):
        initial_mood = list(self.getMood().keys())[0]
        for mood in ["angry", "annoyed"]:
            self.mood[mood] -= 6
            if self.mood[mood] < 0:
                self.mood[mood] = 0
        for mood in ["happy", "busy","sleepy","lazy", "mischevious"]:
            self.mood[mood] -= 6
            if self.mood[mood] < 0:
                self.modifyMood({mood: randint(0,100)})
        mood_change = list(self.getMood().keys())[0]
        if mood_change == initial_mood:
            return None
        return mood_change
    
    def getMood(self):
        maxz = max(list(self.mood.values()))
        for mood in self.mood:
            if self.mood[mood] == maxz:
                return {mood: maxz}

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
    
    
