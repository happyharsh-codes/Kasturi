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

        return mood
    
    def modifyMood(self, mood_change):
        for mood in mood_change:
            if mood in self.mood:
                if mood_change[mood] > self.mood[mood]:
                    self.mood.pop(mood)
                    self.mood[mood] = mood_change[mood]

            else: 
                self.mood[mood] = mood_change[mood]

    def moodSwing(self):
        pass

    def getMood(self):
        mood = self.mood
        lazy = mood.pop("lazy")
        sleepy = mood.pop("sleepy")
        busy = mood.pop("busy")
        main_moood = list(mood.values())[0]

        if lazy > main_moood:
            return {"lazy" : lazy}
        if sleepy > main_moood:
            return {"sleepy" : sleepy}
        if busy > main_moood:
            return {"busy" : busy}
        return mood    


    def moodToDoTasks(self):
        mood = self.mood
        #Kelly wont perform tasks in these situations
        if mood['busy'] > 80:
            return False
        if mood['sleepy'] > 80:
            return False
        if mood['lazy'] > 60:
            return False
        if "mischevious" in mood and mood['mischevious'] > 60:
            return False
        if "sad" in mood and mood['sad'] > 40:
            return False
        if "angey" in mood and mood['angry'] > 35:
            return False
        if "depressed" in mood and mood["angry"] > 20:
            return False
        if "annoyed" in mood and mood["annoyed"] > 50:
            return False
        return True #finally may perform task
    
    