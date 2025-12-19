from __init__ import*

class Giyu:
    """
    Kelly's personal guard.
    You have to pass through him compulsorily.
    Filters:
        - Bad words
        - Spam
        - Attitude detection
    Checks Before Kellyquery:
        - Check if user is Blocked
        - Check is user is Muted
        - Check is user is new
        - Checks availability from Assistant
            - Check if Kelly is busy:
                - If busy, talk but queue the request.
            - Checks if Kelly is Lazy:
                - If lazy only special person can talk to kelly.
            - Check if Kelly is sleeping:
                - If sleeping does not let anyone 
            - (A small percentage of chance server owner and moderator can bypass this )
        - Chek if someone touches kelly or does kelly pat:
            - if not good relation: not allowed 
            
    """

    def __init__(self, client, kelly):
        self.client = client
        self.kelly = kelly
        self._giyu = load_mongo_dict("Giyu", "kellymemory")
        self._giyu.setdefault("new_user", [])
        self._giyu.setdefault("block_list", [])
        self._giyu.setdefault("muted", {})

    async def giyusend(self, channel, content, uid):
        try:
            webhook = await channel.create_webhook(name="Giyu")
            async with channel.typing():
                if isinstance(content, Embed):
                    await webhook.send(content= f"<@{uid}> ", embed=content, username="Giyu", avatar_url=f"https://raw.githubusercontent.com/happyharsh-codes/Kasturi/refs/heads/main/assets/giyu_{randint(1,14)}.png")
                else:
                    await webhook.send(content= f"<@{uid}> " + content, username="Giyu", avatar_url=f"https://raw.githubusercontent.com/happyharsh-codes/Kasturi/refs/heads/main/assets/giyu_{randint(1,14)}.png")
            await webhook.delete()
        except:
            async with channel.typing():
                if isinstance(content, Embed):
                    await channel.send(f"**Giyu**: <@{uid}> ", embed=content)
                else:
                    await channel.send(f"**Giyu**: <@{uid}> " + content)
                                                    
        
    async def giyuFilter(self, message):
        """Filters:
        - Bad words
        - Simp Detector
        - Attitude detection"""
        content = message.content.lower()

        #Default Internal Bad Words
        bad = ["kill", "fuck", "abuse", "dick", "pussy", "chut", "asshole"]
        for w in bad:
            if w in content:
                prompt = f"You are Giyu, Kelly's Chief Guard\nThis user is detected saying bad words in the chat. As cheif guard scold user in a single sentence."
                response = getResponse(f"{message.author.display_name}: {message.content}", prompt)
                try:
                    await message.delete()
                except:
                    pass
                await self.giyusend(message.channel, self.giyuEmojify(response), message.author.id)
                return True

        #Simp Detector
        simp_score = 0
        simp_words = { "coochie": 4, "hot": 1, "sexy": 2, "makeup": 1, "only fans": 5, "onlyfans": 5, "smell": 3, "blacked": 1, "pretty": 1, "I have": 2, "feelings": 3, "pain": 2, "hey": 1, "heyy": 2, "heyyy": 4, "cute": 1, "cutie": 2, "qt": 3, "smash": 3, "DM": 3, "dm": 3, "piss on me": 500, "damn": 2, "I want you": 4, "I love you": 4, "Ily": 4, "ass": 1, "😩": 2, "🍆": 3, "🍑": 3, "💦": 3, "fart": 3}
        for simp_word in simp_words.keys():
            if simp_word.lower() in content:
                simp_score += simp_words[simp_word]
        
        if simp_score >= 5:
            print("SIMP DETECTED")
            prompt = f"You are Giyu, Kelly's Chief Guard\nThis user is detected simping in the chat. As cheif guard scold user in a single sentence."
            response = getResponse(f"{message.author.display_name}: {message.content}", prompt)
            try:
                await message.delete()
            except:
                pass
            await self.giyusend(message.channel, self.giyuEmojify(response), message.author.id)
            return True

        #Attitude Detector
        return False

    async def giyuQuery(self, message, mood, type="member"):
        """
        Checks Before Kellyquery:
        - Checks Filters
        - Checks if unknown DMs
        - Check if user is New
        - Check if user is Blocked
        - Check if user is Muted
        - Check if Kelly is Sleeping:
            - If sleeping does not let anyone intefere
                - A small percentage of chance server owner and moderator can bypass this 
        - Chek if someone touches kelly or does kelly pat:
            - if not good relation: not allowed 
        """    
        #Check Filters
        if await self.giyuFilter(message):
            return False

        #Dm messages Rules:
        #Kelly handles all by herself 
        #Only friends and allowed members can dm her
        #Hidden treasures and rewards 
        if isinstance(message.channel, discord.DMChannel):
            if message.author.id in self.kelly.memory._memory["friends"]:
                return True 
            prompt = f"You are Giyu, Kelly's Chief Guard\nThis user is not even on Kelly's friend list and still Dms Kelly.\nGenerate: Your Response in 20 words with emojis"
            response = getResponse(f"{message.author.display_name}: {message.content}", prompt, assistant=self.kelly.memory.getUserChats(message.author.id))
            await self.giyusend(message.channel, self.giyuEmojify(response), message.author.id)
            return False 

        #New User Initialisation 
        if message.author.id not in self._giyu["new_user"]:
            prompt = f"You are Giyu, Kelly's Chief Guard\nGenerate: Your Response in 20 words with 2-3 emoji. Generate a Initializing message for new user. name : {message.author.name} id: {message.author.id}"
            response = getResponse(message.content, prompt, assistant=self.kelly.memory.getUserChats(message.author.id))
            await message.channel.send(response)
            em = Embed(title= f"Hi I'm Giyu {EMOJI2['giyuhi']}", description="Hi I'm Giyu Kelly's Personal Bodyguard. Kelly's security is my responsibility as you know so dms off unless Kelly adds you in friend list. Alright so keep chatting in servers with Kelly. Respect boundaries and follow chat policy.", color = Color.green())
            em.set_thumbnail(url= f"https://raw.githubusercontent.com/happyharsh-codes/Kasturi/refs/heads/main/assets/giyu_{randint(1,14)}.png")
            dm_channel = message.author.dm_channel
            self.kelly.memory.addUserChat(message.content, response, message.author.id, reply_by="Giyu")
            if not dm_channel:
                dm_channel = await message.author.create_dm()
            try:
                await dm_channel.send(embed = em)
            except:
                await self.giyusend(message.channel, em, message.author.id)
            self.kelly.memory.modifyUserRelation(message.author.id, 2)
            self._giyu["new_user"].append(message.user.id)
            return True

        #Blocked User
        elif message.author.id in self._giyu["block_list"]:
            prompt = f"You are Giyu, Kelly's Chief Guard\nThis user is already BANNED by kelly shoo him away.\nGenerate: Your Response in 20 words with emojis"
            response = getResponse(f"{message.author.display_name}: {message.content}", prompt, assistant=self.kelly.memory.getUserChats(message.author.id))
            self.kelly.memory.addUserChat(message.content, response, message.author.id, reply_by="Giyu")
            await message.reply(self.giyuEmojify(f"**Giyu**: {response}"))
            if "Server owner" in type and randint(1,6) == 1:
                return True
            if "Moderator" in type and randint (1,10) == 1:
                return True
            return False

        #Muted User
        elif str(message.author.id) in self._giyu["muted"]:
            prompt = f"You are Giyu, Kelly's Chief Guard\nThis user is muted by kelly for sometime, shoo him away.\nGenerate: Your Response in 20 words with emojis"
            response = getResponse(f"{message.author.display_name}: {message.content}", prompt, assistant=self.kelly.memory.getUserChats(message.author.id))
            self.kelly.memory.addUserChat(message.content, response, message.author.id, reply_by="Giyu")
            await self.giyusend(message.channel, self.giyuEmojify(response), message.author.id)
            return False

        #Kelly touch / pat
        elif "pats" in message.content.lower() or "pat" in message.content.lower(): #only friends can pat kelly
            prompt = f"You are Giyu, Kelly's Chief Guard\nKelly is highly dignified cute mod girl, don't let anyone touch or pat her. Generate: Your Response in 20 words with emojis"
            response = getResponse(f"{message.author.display_name}: {message.content}", prompt, assistant=self.kelly.memory.getUserChats(message.author.id))
            self.kelly.memory.addUserChat(message.content, response, message.author.id, reply_by="Giyu")
            await self.giyusend(message.channel, self.giyuEmojify(response), message.author.id)
            if "Server owner" in type or message.author.id in self.kelly.memory._memory["friends"]:
                return True 
            if "Moderator" in type and randint (1,5) == 1:
                return True
            return False

        #Sleeping
        elif self.kelly.status == "sleeping":
            if "Server owner" in type:
                return True
            if "Moderator" in type and randint (1,5) == 1:
                return True
            prompt = f"You are Giyu, Kelly's Chief Guard\nKelly is currently sleeping\nGenerate Your Response in 20 words with emojis. Inform user about Kelly's state. Chat with user and keep convo active. If task send by user Tell Ayasaka(Kelly's assistant) to add it in Kelly's schedule."
            response = getResponse(f"{message.author.display_name}: {message.content}", prompt, assistant=self.kelly.memory.getUserChats(message.author.id))
            self.kelly.memory.addUserChat(message.content, response, message.author.id, reply_by="Giyu")
            await self.giyusend(message.channel, self.giyuEmojify(response), message.author.id)
            command = self.kelly.search_commands(message)
            if command:
                await self.kelly.ayasaka.ayasakaQueueTasks(message, command)
            return False

        #Finally Let talk with Kelly 🤣 
        return True

    async def giyuTalk(self, message):
        prompt = f"You are Giyu, Kelly's Chief Guard\nGenerate Your Response in 20 words with emojis. Chat with user and keep convo active. If task send by user Tell Ayasaka(Kelly's assistant) to add it in Kelly's schedule. Keep stern face and provide user with all help function and rules and regulations and details."
        response = getResponse(f"{message.author.display_name}: {message.content}", prompt, assistant=self.kelly.memory.getUserChats(message.author.id))
        self.kelly.memory.addUserChat(message.content, response, message.author.id, reply_by="Giyu")
        await self.giyusend(message.channel, self.giyuEmojify(response), message.author.id)
        command = self.kelly.search_commands(message)
        if command:
            await self.kelly.ayasaka.ayasakaQueueTask(message, command)
                
    def giyuEmojify(self, message):
        emoji_exchanger = {
            "😫": "giyutedio",
            "💤": "giyutedio",
            "😪": "giyutedio",
            "😩": "giyutedio",
            "😴": "giyutedio",
            "🎭": "giyusweat",
            "🎬": "giyusweat",
            "🎥": "giyusweat",
            "📽": "giyusweat",
            "🎦": "giyusweat",
            "📼": "giyusweat",
            "🎞": "giyusweat",
            "📹": "giyusweat",
            "📷": "giyusweat",
            "📸": "giyusweat",
            "😣": "giyuangry",
            "😳": "giyulove",
            "😚": "giyulove",
            "😏": "giyufuck",
            "😒": "giyuangry",
            "😛": "giyufuck",
            "😜": "giyufuck",
            "😝": "giyufuck",
            "🤪": "giyufuck",
            "😵": "giyushocked",
            "🍟": "giyuhype",
            "😭": "giyusad",
            "👊": "giyuangry",
            "💪": "giyuangry",
            "🦾": "giyuangry",
            "😁": "giyusmiley",
            "👋": "giyuhi",
            "🙌": "giyuhi",
            "♥": "giyulove",
            "😬": "giyushock",
            "🙄": "giyuoffended",
            "😒 ": "giyfuck",
            "🧩": "giyukawai",
            "🧐": "giyukawai",
            "🥤": "giyuhype",
            "🧃": "giyuhype",
            "😂": "giyusmiley",
            "🤣": "giyusmiley",
            "😄": "giyusmiley",
            "😆": "giyusmiley",
            "😃": "giyusmiley",
            "👌": "giyuok",
            "🆗": "giyuok",
            "🙆‍♀️": "giyuok",
            "🙆‍♂️": "giyuok",
            "😍": "giyulove",
            "😘": "giyulove",
            "🥰": "giyulove",
            "😻": "giyulove",
            "🤗": "giyulove",
            "🍿": "giyuhype",
            "🎉": "giyuhype",
            "🍾": "giyuhype",
            "🛐": "giyukawai",
            "🙇": "giyukawai",
            "🙇‍♀️": "giyukawai",
            "😙": "giyusmiley",
            "💤": "giyutedio",
            "😴": "giyutedio",
            "🛌": "giyutedio",
            "🤔": "giyuoffended",
            "😁": "giyuhi",
            "🤨": "giyushock",
            "😠": "giyushock",
            "😡": "giyushock",
            "😤": "giyushock",
            "😗": "giyushock",
            "🥱": "giyutedio"
        }
        for emoji, kellyemoji in emoji_exchanger.items():
            if emoji in message:
                message = message.replace(emoji, EMOJI2[kellyemoji])
                
        return message
