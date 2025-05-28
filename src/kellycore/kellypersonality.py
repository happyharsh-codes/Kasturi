from __init__ import*

class KellyPersona:
    """Controls Kelly Personality and Behaviour:
    list of all possible personality traits:- 
    ["duty", "mischevious", "interlligent", "caring"]"""


    def __init__(self, filedata=Persona):
        self.persona = filedata

    def getPersonality(self):
        return self.persona
    
    def modifyPersonality(self, persona_change): 
        for persona in persona_change:
            self.persona[persona] = persona_change[persona]

    def getRequiredPersona(self, msg):
        pass

    def getTaskSuccessRate(self, msg):
        pass

    def save(self):
        with open("res/kellymemory/personality.json", "w") as f:
            from json import dump
            dump(self.persona, f, indent=4)