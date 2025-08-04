from __init__ import*
from json import dump

class KellyRealtion:
    """Controls all Kelly Relation with every user via chat
    -relation: (int)
    stores respect which can be positive or negative or zero:
    -positive relaion: good relation, can be increased by helping kelly, talking and behaving nicely
    -very high positive relaion can lead to be friends with kelly.
    -negative relation: bad relation, usually due to bad words, bad behaviour, or ordering kelly
    -very negative relation can lead to ban the user from ever talking to kelly
    -zero respect means unknown user
    """


    def __init__(self, filedata=Relation):
        self.relation = filedata


    def getUserRelation(self, id):
        '''Returs user realtion with Kasturi- an integer: good relation= +ve, bad = -ve, unknown = zero. more respect more relation no bad respect negative relation on.'''
        if not str(id) in self.relation:
            return None
        return self.relation[str(id)]
    
    def modifyUserRespect(self, val, id):
        if str(id) not in self.relation:
            self.relation[str(id)] = val
            if self.relation[str(id)] == 0:
                self.relation[str(id)] += 1
            return
        self.relation[str(id)] += val
        if self.relation[str(id)] > 80: # Think of making Friend
            pass
        if self.relation[str(id)] < -20: # Think of ban
            pass
    
    def addUserInfo(self, info, userid):
        if str(userid) in Behaviours:
            Behaviours[str(userid)] += info
            if len(Behaviours[str(userid)]) > 512:
                self.updateUserInfo(userid)
        else:
            Behaviours[str(userid)] = [info]

    def updateUserInfo(self, userid):
        prompt = "summarize user behaviour and shorten it. Respond with shorten sentence only"
        response = getResponse(Behaviours[str(userid)], prompt, client=3)
        Behaviours[str(userid)] = response
    
    def getUserInfo(self, userid):
        if not str(userid) in Behaviours:
            return ""
        return Behaviours[str(userid)]

    def save(self):
        with open("res/kellymemory/relations.json", "w") as f:
            dump(self.relation, f, indent=4)
        with open("res/kellymemory/behaviors.json", "w") as f:
            dump(Behaviours, f, indent=4)