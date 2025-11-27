from __init__ import*

class KellyMemory:
    """
    Stores Chat details and User Behaviors(likes, dislikes, personality etc) 
    Stores:
        - Last 4 chats
        - Likes / dislikes #can also set manually from k memory command
        - Frequently used words
        - User behaviour patterns
        - Friend list
    """

    def __init__(self):
        if not Memory["users"]:
            Memory["users"] = {}
        pass

    def getUserChatData(self, user_id):
        if str(userid) in Chats:
            all_user_chats = Chats[str(user_id)]
            res = "\n".join(all_user_chats)
            return res
        return ""
      
    def storeChatData(self, message, response, uid):
        """Store last conversation detail."""
        message = message.replace("\n","").replace(":","")
        response = response.replace("\n","").replace(":","")
        if str(uid) not in Chats:
            Chats[str(uid)] = [f"User:{message}\nKelly:{response}"]
        else:
            Chats[str(id)].append(f"User:{message}\nKelly:{response}")
            if len(Chats[str(id)]) > 4:
                Chats[str(id)].pop(0)

        self.data["users"][uid]["messages"].append({
            "said": message,
            "kelly_reply": response
        })

    def addFriend(self, uid):
        """Add user to friend list."""
        Database["friends"].append(int(uid))
      
    def removeFriend(self, uid):
        """Removes User from friend list."""
        Database["friends"].remove(int(uid))
      
    def getUserInfo(self, uid):
        """Returns memory stored on user."""
        memory = Memory["users"].get(str(uid), {"likes": None, "dislikes": None})
        return {"behaviour": Behaviours[str(uid)], "likes": memory["likes"], "dislikes": memory["dislikes"]}

    def addUserInfo(self, info, userid):
        if str(userid) in Behaviours:
            Behaviours[str(userid)] += info
            if len(Behaviours[str(userid)]) > 512:
                self.updateUserInfo(userid)
        else:
            Behaviours[str(userid)] = info

    def updateUserInfo(self, userid):
        prompt = "summarize user behaviour and shorten it. Respond with shorten sentence only"
        response = getResponse(Behaviours[str(userid)], prompt)
        Behaviours[str(userid)] = response
    
