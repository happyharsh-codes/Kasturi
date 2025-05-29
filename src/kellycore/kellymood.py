class KellyMood:
    '''#-----Class to handle Kelly Mood-----#
    -mood: {"happy": 1-100, "busy": 1-100, "lazy": 1-100, "sleepy": 1-100}
    the first element in mood is the main current mood trait
    while the first mood may change to different mood traits others are permanent
    
    Mood Traits : ["happy", "sad" , "angry", "annoyed", "depressed", "mischevious"]
    
    '''
    _MOODS = ["happy", "sad" , "angry", "annoyed", "depressed", "mischevious"]

    def __init__(self):
        self.mood = self.generateRandomMood()


    def generateRandomMood(self):
        from random import randint
        mood = {}
        mood["happy"] = randint(1,100)
        mood["busy"] = randint(1,100)
        mood["sleepy"] = randint(1,100)
        mood["lazy"] = randint(1,100)
        mood["sad"] = randint(1,100)
        mood["angry"] = randint(1,100)
        mood["annoyed"] = randint(1,100)
        mood["depressed"] = randint(1,100)
        mood["mischevious"] = randint(1,100)
        return mood
    
    def modifyMood(self, mood_change):
        for mood in mood_change:
            self.mood[mood] += mood_change[mood]
            if mood == "happy":
                self.mood["sad"] -= mood_change
            

    def moodSwing(self):
        pass

    def getMood(self):
        maxz = max(list(self.mood.values()))
        for mood in self.mood:
            if self.mood[mood] == maxz:
                return {mood: maxz}

    def moodToDoTasks(self):
        mood = self.mood
        #Kelly wont perform tasks in these situations
        if mood['busy'] > 80:
            return False
        if mood['sleepy'] > 80:
            return False
        if mood['lazy'] > 60:
            return False
        if mood['mischevious'] > 60:
            return False
        if mood['sad'] > 40:
            return False
        if mood['angry'] > 35:
            return False
        if mood["angry"] > 20:
            return False
        if mood["annoyed"] > 50:
            return False
        return True #finally may perform task
    
    