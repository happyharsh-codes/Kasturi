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
            return 0
        return self.relation[str(id)]
    
    def modifyUserRespect(self, val, id):
        if str(id) not in self.relation:
            self.relation[str(id)] = val
            return
        self.relation[str(id)] += val
        if self.relation[str(id)] > 80: # Think of making Friend
            pass
        if self.relation[str(id)] < -20: # Think of ban
            pass

    def save(self):
        with open("res/kellymemory/relations.json", "w") as f:
            dump(self.relation, f, indent=4)