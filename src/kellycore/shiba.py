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

        prompt = f"You are Kelly's(Real like discord bot with moods and attitudes) Chief Guard\nGenerate: Your Response in 30 words"
        response = getResponse(message.content, prompt, client=2)
        await message.reply(response)

        if querytype == 1:
            descision = getResponse(message.content, "You are Kelly's(Real like discord bot with moods and attitudes) Chief Guard\nDecide wether user should be allowed to talk to kelly or not\nReturn ONLY True or False", client=1)
            if "true" in descision.lower():
                print("#=====Shiba allowed user to talk to kelly=====#")
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