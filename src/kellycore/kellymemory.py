from __init__ import *

class KellyMemory:
    """
    Stores and manages Kelly's Memory
    Stores:
        - Users Info
           - Chat details
           - User behaviour patterns 
           - Likes / dislikes
           - Relations
               -positive relaion: good relation, can be increased by helping kelly, talking and behaving nicely
               -very high positive relaion can lead to be friends with kelly.
               -negative relation: bad relation, usually due to bad words, bad behaviour, or ordering kelly
               -very negative relation can lead to ban the user from ever talking to kelly
        - Friend list
        - Kelly Personality
        - Schedules
            -just there in memory , managed by KellyBusy class
    """

    def __init__(self):
        self._memory = load_mongo_dict("memory", "kellymemory")
        
    def getUserChats(self, user_id, limit: int = 4):
        if not self._memory["users"][str(user_id)]:
            return ""
        chats = self._memory["users"][str(user_id)]["chats"]
        all_user_chats = chats[-limit:]
        return ", ".join(all_user_chats)

    def addUserChat(self, message, response, uid, reply_by="Kelly"):
        """Store last conversation detail."""
        message = message.replace("\n", "").replace(":", "")
        response = response.replace("\n", "").replace(":", "")

        user = self._memory["users"].get(str(uid))
        line = f"User:{message}, {reply_by}:{response}"

        if not user:
            self._memory["users"][str(uid)] = {
                "chats": [line],
                "behaviours": "",
                "likes": [],
                "dislikes": [],
                "relations": 1,
            }
        else:
            user["chats"].append(line)
            if len(user["chats"]) > 8:
                user["chats"].pop(0)
        self._memory._sync()

    def addFriend(self, uid):
        """Add user to friend list."""
        uid = int(uid)
        if uid not in self._memory["friends"]:
            self._memory["friends"].append(uid)
            self._memory._sync()
  
    def removeFriend(self, uid):
        """Removes User from friend list."""
        uid = int(uid)
        if uid in self._memory["friends"]:
            self._memory["friends"].remove(uid)
            self._memory._sync()
            
    def _ensure_user(self, uid: str):
        """Internal helper to create a blank user record if missing."""
        if uid not in self._memory["users"]:
            self._memory["users"][uid] = {
                "chats": [],
                "behaviours": "",
                "likes": [],
                "dislikes": [],
                "relations": 1,
            }
        return self._memory["users"][uid]

    def addLikes(self, uid, like_item):
        """Adds item to users liked items in memory"""
        user = self._ensure_user(str(uid))
        user["likes"].append(like_item)
        self._memory._sync()
        
    def addDislikes(self, uid, dislike_item):
        """Adds item to users disliked items in memory"""
        user = self._ensure_user(str(uid))
        user["dislikes"].append(dislike_item)
        self._memory._sync()
        
    def getUserLikes(self, uid):
        """Provides users liked items from the memory"""
        user = self._memory["users"].get(str(uid))
        if not user:
            return []
        return user.get("likes", [])

    def getUserDislikes(self, uid):
        """Provides users disliked items from the memory"""
        user = self._memory["users"].get(str(uid))
        if not user:
            return []
        return user.get("dislikes", [])

    def addUserBehaviour(self, uid, behave: str):
        """
        Adds user behaviour to the core memory.
        If stored behaviours becomes very long, summarises and stores it.
        """
        user = self._ensure_user(str(uid))
        user["behaviours"] = (user.get("behaviours", "") + " " + behave).strip()
        if len(user["behaviours"]) > 1024:
            user["behaviours"] = self.summarizeBehaviour(user["behaviours"])
        self._memory._sync()
        
    def summarizeBehaviour(self, long_behaviour: str) -> str:
        prompt = (
            "Summarize user behaviour and shorten it. "
            "Respond with shortened sentence only."
        )
        short_behaviour = getResponse(long_behaviour, prompt)
        return short_behaviour

    def getUserBehaviour(self, uid):
        user = self._memory["users"].get(str(uid))
        if not user:
            return ""
        return user.get("behaviours", "")

    def getUserRelation(self, uid):
        user = self._memory["users"].get(str(uid))
        if not user:
            return 0
        return user.get("relations", 0)

    def modifyUserRelation(self, uid, value: int):
        user = self._ensure_user(str(uid))
        user["relations"] = user.get("relations", 0) + value
        self._memory._sync()
        if user["relations"] > 80 and uid not in self._memory["friends"]:
            return "friend"
        elif user["relations"] < -20:
            return "ban"
        return ""

    def getPersona(self):
        return self._memory["personality"]

    def modifyPersona(self, persona, value: int):
        self._memory["personality"][persona] = (
            self._memory["personality"].get(persona, 0) + value
        )
        self._memory._sync()
