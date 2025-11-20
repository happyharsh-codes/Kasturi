from __init__ import*

class KellyPersona:
    """Controls Kelly Personality and Behaviour:
    list of all possible personality traits:- 
    ["duty", "mischevious", "interlligent", "caring"]"""


    def __init__(self, filedata=Persona):
        self.persona = filedata

    def modifyPersonality(self, persona_change): 
        for persona in persona_change:
            self.persona[persona] = persona_change[persona]
            if self.persona[persona] < 0:
                self.persona[persona] = 0

    def getRequiredPersona(self):
        return self.persona

    def getTaskSuccessRate(self, msg):
        pass
