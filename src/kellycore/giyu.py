from __init__ import*

class Giyu:

    def __init__(self):
        pass

    async def giyuQuery(self, message, mood):
        '''Gives giyu (kelly's guard) response'''

        async with message.channel.typing():
            if str(message.author.id) not in Relation:
                prompt = f"You are Kelly's Chief Guard\nGenerate: Your Response in 30 words with emojis"
                response = getResponse(message.content, prompt, client=0)
                await message.reply(self.giyuEmojify(f"**Giyu**: {response}"))
                descision = getResponse(f"User:{message.content}\nGuard: {response}", "You are Kelly's Chief Guard\nDecide wether user should be allowed to talk to kelly or not. Always Allow when the user gives id number.\nReturn ONLY True or False", client=1)
                if "true" in descision.lower():
                    print(f"#=====Giyu allowed user {message.author.name} {message.author.id} to talk to kelly=====#")
                    await message.channel.send(f"-# {message.author.name} is allowed to talk to Kelly")
                    Relation[str(message.author.id)] = 1
                return True
            elif message.author.id in Server_Settings[str(message.guild.id)]["block_list"]:
                prompt = f"You are Kelly's Chief Guard\nThis user is already BANNED by kelly shoo him away.\nGenerate: Your Response in 30 words with emojis"
                response = getResponse(message.content, prompt, client=0)
                await message.reply(self.giyuEmojify(f"**Giyu**: {response}"))
                return True
            elif str(message.author.id) in Server_Settings[str(message.guild.id)]["muted"]:
                prompt = f"You are Kelly's Chief Guard\nThis user is muted by kelly for sometime, shoo him away.\nGenerate: Your Response in 30 words with emojis"
                response = getResponse(message.content, prompt, client=0)
                await message.reply(self.giyuEmojify(f"**Giyu**: {response}"))
                return True
                
            elif "pats" in message.content.lower(): #only friends can pat kelly
                pass

            if mood["busy"] > 80:
                prompt = f"You are Kelly's Chief Guard\nkelly is currently busy\nGenerate: Your Response in 30 words with emojis"
                response = getResponse(message.content, prompt, client=0)
                await message.reply(self.giyuEmojify(f"**Giyu**: {response}"))
                return True
            elif mood["lazy"] > 80:
                if Relation[str(message.author.id)] > 80: #exceptional members
                    return False
                prompt = f"You are Kelly's Chief Guard\nkelly is currently very lazy to reply\nGenerate: Your Response in 30 words with emojis"
                response = getResponse(message.content, prompt, client=0)
                await message.reply(self.giyuEmojify(f"**Giyu**: {response}"))
                return True
            elif mood["sleepy"] > 80:
                prompt = f"You are Kelly's Chief Guard\nkelly is currently sleeping\nGenerate: Your Response in 30 words with emojis"
                response = getResponse(message.content, prompt, client=0)
                await message.reply(self.giyuEmojify(f"**Giyu**: {response}"))
                return True
            return False

    async def giyuTakeDescision(self, message, mood):
        prompt = f"""You are Kelly's Chief Guard\n Take strong descision based on Kelly's current mood {mood}. Generate Json dict using kelly response and mood
        - response: (str)
        - action: (pass/mute/ban)"""
        response = getResponse(message.content, prompt, client=1).lower()
        try:
            result = loads(response.split("```json")[1].split('```')[0])
            reply = result["response"]
            action = result["action"]
        except Exception as parse_error:
            print("Could not parse Giyu AI response:", parse_error) 
            response = ""
            reply = "I'll let you go this time"
            action = "pass"
        await message.reply(self.giyuEmojify(f"**Giyu**: {reply}"))
        if action == "ban":
            Server_Settings[str(message.guild.id)]["block_list"].append(message.author.id)
        if action == "mute":
            Server_Settings[str(message.guild.id)]["muted"].update({str(message.author.id): (datetime.now(UTC) + timedelta(minutes=randint(5,15))).isoformat()})


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
                message = message.replace(emoji, EMOJI[kellyemoji])
                
        return message
