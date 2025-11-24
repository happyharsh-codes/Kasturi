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

    def getUserRelation(self, id):
        '''Returs user realtion with Kasturi- an integer: good relation= +ve, bad = -ve, unknown = zero. more respect more relation no bad respect negative relation on.'''
        if not str(id) in Relation:
            return None
        return Relation[str(id)]
    
    import random

    async def modifyUserRespect(self, val, user_id):
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
            await self.thinkFriendAction(user_id)

        # --- BAN LOGIC ---
        if respect < -20:
            await self.thinkBanAction(user_id)

        return

    async def thinkFriendAction(self, user_id):
        """Bot thinks of making user a friend when respect is high."""
        user = self.client.get_user(int(user_id))
        if not user:
            return

        # Think message
        if user_id in Database["friends"]:
            return
        # Action chance
        roll = random.randint(1, 100)
        # 60% think only
        if roll <= 60:
            await user.send("I think we can be great friends someday 😊")
        # 25% make friend
        elif roll <= 85:
            await user.send("🎉 I have decided! You are now my friend!")
            Database["friends"].append(user_id)
        # 15% small reward
        else:
            await user.send("✨ You're special! Here's a small gift for being nice. Join official Server to recieve your reward")
            # Give reward logic here

    async def thinkBanAction(self, user_id):
        """Bot thinks of punishing the user when respect is low."""
        user = self.client.get_user(int(user_id))
        if not user:
            return

        # Think message
        await user.send("😠 I’m thinking… You’re being a bit rude to me.")

        roll = random.randint(1, 100)

        # 60% think only
        if roll <= 60:
            await user.send("I'll ignore this for now.")
        # 25% mute instead of ban
        elif roll <= 85:
            await user.send("🔇 I’m muting you for a bit...")
            # Mute
            await self.muteUser(user)
        # 15% actual ban
        else:
            await user.send("⛔ You crossed the line. Goodbye!")
            # Ban 
            await self.banUser(user)
    
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
