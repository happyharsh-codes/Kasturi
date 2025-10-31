from __init__ import*

class Giyu:

    def __init__(self, client):
        self.client = client

    async def giyuQuery(self, message, mood):
        '''Gives giyu (kelly's guard) response'''

        async with message.channel.typing():
            if str(message.author.id) not in Relation:
                prompt = f"You are Giyu, Kelly's Chief Guard\nGenerate: Your Response in 20 words with 2-3 emoji. Generate a Initializing message for new user. name : {message.author.name} id: {message.author.id}"
                response = getResponse(message.content, prompt, client=0)
                await message.reply(self.giyuEmojify(f"**Giyu**: {response}"))
                badges = []
                flags = message.author.public_flags
                if flags.hypesquad_bravery: badges.append("🦁 Bravery")
                if flags.hypesquad_brilliance: badges.append("🧠 Brilliance")
                if flags.hypesquad_balance: badges.append("⚖️ Balance")
                if flags.verified_bot: badges.append("✅ Verified Bot")
                if flags.staff: badges.append("🛡️ Discord Staff")
                badge_text = ", ".join(badges) if badges else "No Public Badges"
                created = int(message.author.created_at.timestamp())
                joined = int(message.author.joined_at.timestamp())
                
                def get_device(member):
                    devices = []
                    if str(member.mobile_status) != "offline":
                        devices.append("📱 Mobile")
                    if str(member.desktop_status) != "offline":
                        devices.append("🖥️ Desktop")
                    if str(member.web_status) != "offline":
                        devices.append("🌐 Web")

                    return ", ".join(devices) if devices else "❌ Offline / Invisible"

                if message.author.premium_since:
                    booster_text= f"Boosting since <t:{int(message.author.premium_since.timestamp())}:D>"
                else:
                    booster_text = 'Not Boosting'
                invite_text = "unknown"
                inviter_guild = INVITER.get(str(message.guild.id), None)
                if inviter_guild:    
                    inviter_id = inviter_guild.get(str(message.author.id),None)
                    if inviter_id:
                        inviter = self.client.get_user(inviter_id)
                        invite_text = f"{inviter.mention} - {inviter.name}"
                em = Embed(title = "⚙️ New Member Initialisation 🛠️", description= f"**📛 Username**:{message.author.name}\n**👤 Name:** {message.author.display_name}\n**🪪 ID**: {message.author.id}\n**🏅 Badges**: {badge_text}\n**📅 Account Created**: <t:{created}:F>\n**🚪 Joined Server**: <t:{joined}:F>\n**📌 Device**: {get_device(message.author)}\n**🚀 Server Booster**: {booster_text}\n**Invited By**: {invite_text}", color= Color.purple())
                em.set_thumbnail(url= message.author.avatar)
                em.set_author(name = f"{message.author.name}")
                await message.channel.send(f"{message.author.mention}", embed= em)
                Relation[str(message.author.id)] = 1
                em = Embed(title= "Welcome to Kelly", description="Thanks for beginning your chat with Kelly.\nThis chat is only for light entertainment purpose and Moderation and running commands.\nPlease Make sure your chat complies with [Discord TOS](https://discord.com/terms) And our [Kelly TOC](https://top.gg/bot/1368884334076891136?s=05ffa0896dc29).Hope you like my bot, have fun\nIn case you want to contact me, Meet me [here](https://discord.gg/y56na8kN9e)", color = Color.green())
                emoji = choice(list(EMOJI.values()))
                if "a:" in emoji:
                    ext = ".gif"
                else:
                    ext = ".png"
                emoji = emoji.split(":")[2]
                dm_channel = message.author.dm_channel
                em.set_thumbnail(url= f"https://cdn.discordapp.com/emojis/{emoji}{ext}")
                if not dm_channel:
                    dm_channel = await message.author.create_dm()
                try:
                    await dm_channel.send(embed=em)
                except:
                    pass
                return False
            elif message.author.id in Server_Settings[str(message.guild.id)]["block_list"]:
                prompt = f"You are Giyu, Kelly's Chief Guard\nThis user is already BANNED by kelly shoo him away.\nGenerate: Your Response in 20 words with emojis"
                response = getResponse(message.content, prompt, client=0)
                await message.reply(self.giyuEmojify(f"**Giyu**: {response}"))
                return True
            elif str(message.author.id) in Server_Settings[str(message.guild.id)]["muted"]:
                prompt = f"You are Giyu, Kelly's Chief Guard\nThis user is muted by kelly for sometime, shoo him away.\nGenerate: Your Response in 20 words with emojis"
                response = getResponse(message.content, prompt, client=0)
                await message.reply(self.giyuEmojify(f"**Giyu**: {response}"))
                return True
                
            elif "pats" in message.content.lower(): #only friends can pat kelly
                pass

            if mood["busy"] > 90:
                prompt = f"You are Giyu, Kelly's Chief Guard\nkelly is currently busy\nGenerate: Your Response in 20 words with emojis"
                response = getResponse(message.content, prompt, client=0)
                await message.reply(self.giyuEmojify(f"**Giyu**: {response}"))
                return True
            elif mood["lazy"] > 90:
                if Relation[str(message.author.id)] > 80: #exceptional members
                    return False
                prompt = f"You are Giyu, Kelly's Chief Guard\nkelly is currently very lazy to reply\nGenerate: Your Response in 20 words with emojis"
                response = getResponse(message.content, prompt, client=0)
                await message.reply(self.giyuEmojify(f"**Giyu**: {response}"))
                return True
            elif mood["sleepy"] > 90:
                prompt = f"You are Giyu, Kelly's Chief Guard\nkelly is currently sleeping\nGenerate: Your Response in 20 words with emojis"
                response = getResponse(message.content, prompt, client=0)
                await message.reply(self.giyuEmojify(f"**Giyu**: {response}"))
                return True
            return False

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
