from __init__ import*

class KellyMemory:
    """
    Stores and manages Kelly's Memory
    Stores:
        - User chats
        - Likes / dislikes #can also set manually from k memory command
        - Frequently used words
        - User behaviour patterns
        - Friend list
        - Kelly Personality
        - Relations
        - Schedules
    """

    def __init__(self):
        self._memory = load_mongo_dict("memory", "kellymemory")
        if not self._memory["schedules"]:
            self._memory["schedules"] = {}
        if not self._memory["users"]:
            self._memory["users"] = {}
        if not self._memory["friends"]:
            self._memory["friends"] = []
        if not self._memory["reminders"]:
            self._memory["reminders"] = {}

    def getUserChats(self, user_id, limit = 4):
        if self._memory["users"][user_id]:
            all_user_chats = self._memory["users"][user_id]["chats"][-1:-limit]
            res = ", ".join(all_user_chats)
            return res
        return ""
      
    def addUserChat(self, message, response, uid, reply_by="Kelly"):
        """Store last conversation detail."""
        message = message.replace("\n","").replace(":","")
        response = response.replace("\n","").replace(":","")
        if not self._memory["users"][uid]:
            self._memory["users"][uid] = { "chats": [f"User:{message}\n{reply_by}:{response}"], "behaviours": "", "likes": [], "dislikes": [], "relations": 1}
        else:
            self._memory["users"][uid]["chats"].append(f"User:{message}\n{reply_by}:{response}")
            if len(self._memory["users"][uid]["chats"]) > 8:
                self._memory["users"][uid]["chats"].pop(0)

    def addFriend(self, uid):
        """Add user to friend list."""
        self._memory["friends"].append(int(uid))
      
    def removeFriend(self, uid):
        """Removes User from friend list."""
        self._memory["friends"].remove(int(uid))

    def addLikes(self, uid, like_item):
        """Adds item to users liked items in memory"""
        if not self._memory["users"][uid]:
            self._memory["users"][uid] = { "chats": [], "behaviours": "", "likes": [like_item], "dislikes": [], "relations": 1 }
        else:
            self._memory["users"][uid]["likes"].append(like_item)

    def addDislikes(self, uid, dislike_item):
        """Adds item to users disliked items in memory"""
        if not self._memory["users"][uid]:
            self._memory["users"][uid] = { "chats": [], "behaviours": "", "likes": [], "dislikes": [dislike_item], "relations": 1 }
        else:
            self._memory["users"][uid]["dislikes"].append(dislike_item)

    def getUserLikes(self, uid):
        """Provides users liked items from the memory"""
        if not self._memory["users"][uid]:
            return []
        return self.memory["users"][uid]["likes"]

    def getUserDislikes(self, uid):
        """Provides users disliked items from the memory"""
        if not self._memory["users"][uid]:
            return []
        return self.memory["users"][uid]["dislikes"]

    def addUserBehaviour(self, uid, behave: str):
        """Adds user behaviour to the core memory. Is stored behaviours becomes very long, summerises it and stores it."""
        if not self._memory["users"][uid]:
            self._memory["users"][uids] = { "chat": [], "behaviours": behave, "likes": [], "dislikes": [], "relations": 1 }
        else:
            self._memory["users"][uid]["behaviours"] += " " + behave
            if len(self._memory["users"][uid]["behaviours"]) > 1024:
                self._memory["users"][uid]["behaviours"] = self.summarizeBehaviour(self._memory["users"][uid]["behaviours"])
    
    def summarizeBehaviour(self, long_behaviour):
        prompt = "Summarize user behaviour and shorten it. Respond with shorten sentence only"
        shor_behaviour = getResponse(long_behaviour, prompt)
        return short_behaviour

    def getUserBehaviour(self, uid):
        if not self._memory["users"][uid]:
            return ""
        return self._memory["users"][uid]["behaviours"]

    def getUserRelation(self, uid):
        if not self._memory["users"][uid]:
            return 0
        return self._memory["users"][uid]["relations"]

    def modifyUserRelation(self, uid, value):
        if not self._memory["users"][uid]:
            self._memory["users"][uids] = { "chat": [], "behaviours": "", "likes": [], "dislikes": [], "relations": value }
        else:
            self._memory["users"][uids]["relations"] += value

    def getPersona(self):
        return self._memory["personality"]

    def modifyPersonality(self, persona, value):
        self._memory["personality"][persona] = self._memory["personality"].get(persona, 0) + value
