from __init__ import*

class KellyRealtion:
    """
    Controls all Kelly Relation with every user via chat
    -relation: (int)
    stores respect which can be positive or negative or zero:
    -positive relaion: good relation, can be increased by helping kelly, talking and behaving nicely
    -very high positive relaion can lead to be friends with kelly.
    -negative relation: bad relation, usually due to bad words, bad behaviour, or ordering kelly
    -very negative relation can lead to ban the user from ever talking to kelly
    -zero respect means unknown user
    """

    def getUserRelation(self, id):
        '''Returs user realtion with Kasturi- an integer: good relation= +ve, bad = -ve, unknown = zero. more respect more relation no bad respect negative relation on.'''
        if not str(id) in Relation:
            return None
        return Relation[str(id)]

    def modifyUserRespect(self, val, user_id):
        uid = str(user_id)

        if uid not in Relation:
            Relation[uid] = val
        else:
            Relation[uid] += val

        # Avoid 0 neutral dead zone
        if Relation[uid] == 0:
            Relation[uid] += 1

        respect = Relation[uid]

        # --- FRIEND LOGIC ---
        if respect > 80:
            return "friend"
        # --- BAN LOGIC ---
        if respect < -20:
            return "ban"
        return "neutral"
    
