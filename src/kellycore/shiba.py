from __init__ import*

class Shiba:

    def __init__(self):
        pass

    async def shibaQuery(self, message, querytype=1):
        '''Gives shiba (kelly's guard) response
        querytype = 1: for unknown user message kasturi
        querytype = 2 for restricting the user
        querytype = 3 to ban the user from ever using kasturi
        querytype = 4 if kelly is sleeping or too lazy
        quertytype = 5 if kelly is busy'''

        async with message.channel.typing():
            prompt = f"You are Kelly's(Real like discord bot with mood attitudes and sass) Chief Guard\nGenerate: Your Response in 30 words"
            response = getResponse(message.content, prompt, client=3)
            await message.reply(f"**SHIBA**: {response}")

        if querytype == 1:
            descision = getResponse(f"User:{message.content}\nGuard: {response}", "You are Kelly's(Real like discord bot with moods attitude and sass) Chief Guard\nDecide wether user should be allowed to talk to kelly or not\nReturn ONLY True or False", client=2)
            if "true" in descision.lower():
                print("#=====Shiba allowed user to talk to kelly=====#")
                await message.channel.send(f"-# {message.author.name} is allowed to talk to Kelly")
                return True
            else:
                return False
        elif querytype == 2:
            pass
        elif querytype == 3:
            pass
        elif querytype == 4:
            pass
        elif querytype == 5:
            pass