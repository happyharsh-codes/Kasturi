from __init__ import*
from src.kellycore.kellybusy import KellyBusy

class Ayasaka:
    """
    Ayasaka - Kelly's Personal Assistant.

    Responsibilities:
        - Manage Kelly's schedule
        - Maintain availability calendar
        - Inform users when Kelly is free or busy/lazy
        - Automatically reschedule tasks when Kelly is too tired/sleepy/lazy/busy
        - Remind Kelly about pending tasks (from KellyBusy)
        - Defer or decline user requests if overloaded
        - KellyBusy - schedules manager
    
    """

    def __init__(self, kelly):
        self.kelly = kelly
        self.busy = KellyBusy(kelly, kelly.memory._memory["schedules"])
        self._ayasaka = load_mongo_dict("Ayasaka", "kellymemory")
        self._ayasaka.setdefault("new_user", [])
        
    async def ayasakasend(self, channel, content, uid):
        try:
            webhook = await channel.create_webhook(name="Ayaka")
            async with channel.typing():
                if isinstance(content, Embed):
                    await webhook.send(content= f"<@{uid}> ", embed=content, username="Ayasaka", avatar_url=f"https://raw.githubusercontent.com/happyharsh-codes/Kasturi/refs/heads/main/assets/ayasaka_{randint(1,3)}.png")
                else:
                    await webhook.send(content= f"<@{uid}> " + content, username="Ayasaka", avatar_url=f"https://raw.githubusercontent.com/happyharsh-codes/Kasturi/refs/heads/main/assets/ayasaka_{randint(1,3)}.png")
            await webhook.delete()
        except:
            async with channel.typing():
                if isinstance(content, Embed):
                    await channel.send(f"**Ayasaka**: <@{uid}> ", embed=content)
                else:
                    await channel.send(f"**Ayasaka**: <@{uid}> " + content)

    async def remindKellyPerformTask(self):
        pass

    async def ayasakaQuery(self, message, mood, type):
        """
        Handles user requests BEFORE Kelly receives them.
        Flow:
            1. Check KellyBusy
            2. Manage schedule
        """
        uid = message.author.id

        #New User Initialisation 
        if message.author.id not in self._ayasaka["new_user"]:
            prompt = f"You are Ayasaka, Kelly's Assistant - cute, sexy and gorgeous girl.\nGenerate: Your Response in 20 words with 2-3 emoji. Generate a Initializing message for new user. name : {message.author.name} id: {message.author.id}"
            response = getResponse(message.content, prompt, assistant=self.kelly.memory.getUserChats(message.author.id))
            await self.ayasakasend(message.channel, response, message.author.id)
            em = Embed(title= f"Hi I'm Ayasaka ", description="Hi I'm Ayasaka, Kelly's Personal Assistant. Kelly's schedules is my responsibility as you know Kelly gets busy very quickly with server stuff. So yeah I'm there for you when she's busy, I'll schedule your tasks, just call me. Alright so keep chatting in servers with Kelly. Respect boundaries and follow chat policy.", color = Color.green())
            em.set_thumbnail(url= f"https://raw.githubusercontent.com/happyharsh-codes/Kasturi/refs/heads/main/assets/ayasaka_{randint(1,3)}.png")
            dm_channel = message.author.dm_channel
            self.kelly.memory.addUserChat(message.content, response, message.author.id, reply_by="Ayasaka")
            if not dm_channel:
                dm_channel = await message.author.create_dm()
            try:
                await dm_channel.send(embed = em)
            except:
                await self.ayasakasend(message.channel, em, message.author.id)
            self.kelly.memory.modifyUserRelation(message.author.id, 2)
            self._ayasaka["new_user"].append(message.author.id)
            self._ayasaka.root._sync()
            return True
            
        # If Kelly is lazy, assistant manages
        if self.kelly.status == "lazy":
            if not any(cmd in message.content for cmd in self.kelly.commands):
                await self.ayasakasend(message.channel, self.ayasakaEmojify(choice(DATA["ayasaka_responses"]["kelly_lazy"])), message.author.id)
                return False
            prompt = f"You are Ayasaka, Kelly's Assistant. Kelly is cute discord mod bot with lively attitude and sass. Kelly is currently very lazy, grumpy. Generate small Response in 20 words with emojis. Inform user about Kelly's state. If user ask for a task, inform that you have added task in Kelly's schedules. Chat with user, flirt or simp and drive user away as its your only chance to make a move if needed or stay unamused. If its your first chat tell them they can chat with you by typing your name 'Ayasaka'."
            response = getResponse(f"{message.author.display_name}: {message.content}", prompt, assistant=self.kelly.memory.getUserChats(message.author.id))
            self.kelly.memory.addUserChat(message.content, response, message.author.id, reply_by="Ayasaka")
            await self.ayasakasend(message.channel, self.ayasakaEmojify(response), message.author.id)
            command = self.kelly.search_commands(f"User: {message.content}, Bot: {response}")
            if command:
                self.busy.addSchedules(user_id=message.author.id, command_name=command[0], params=command[1], message_id=message.id, channel_id=message.channel.id, priority=1)
            return False
        
        # If schedule is overloaded assistant handles
        if self.kelly.status == "busy":
            if not any(cmd in message.content for cmd in self.kelly.commands):
                await self.ayasakasend(message.channel, self.ayasakaEmojify(choice(DATA["ayasaka_responses"]["kelly_busy"])), message.author.id)
                return False
            prompt = f"You are Ayasaka, Kelly's Assistant. Kelly is cute discord mod bot with lively attitude and saas. Kelly's schedules are overloaded already and shes very busy. Generate small Response in 20 words with emojis. Inform user about Kelly's state. Inform that tasks cant be added as Kelly's schedules are full if user sends a task then only. Chat with user, flirt or simp and drive user away as its your only chance to make a move if needed. If its your first chat tell them they can chat with you by typing your name 'Ayasaka'"
            response = getResponse(f"{message.author.display_name}: {message.content}", prompt, assistant=self.kelly.memory.getUserChats(message.author.id))
            self.kelly.memory.addUserChat(message.content, response, message.author.id, reply_by="Ayasaka")
            await self.ayasakasend(message.channel, self.ayasakaEmojify(response), message.author.id)
            return False

        return True # Kelly may proceed now

    async def ayasakaTalk(self, message):
       #New User Initialisation 
        if message.author.id not in self._ayasaka["new_user"]:
            em = Embed(title= f"Hi I'm Ayasaka ", description="Hi I'm Ayasaka, Kelly's Personal Assistant. Kelly's schedules is my responsibility as you know Kelly gets busy very quickly with server stuff. So yeah I'm there for you when she's busy, I'll schedule your tasks, just call me. Alright so keep chatting in servers with Kelly. Respect boundaries and follow chat policy.", color = Color.green())
            em.set_thumbnail(url= f"https://raw.githubusercontent.com/happyharsh-codes/Kasturi/refs/heads/main/assets/ayasaka_{randint(1,3)}.png")
            dm_channel = message.author.dm_channel
            if not dm_channel:
                dm_channel = await message.author.create_dm()
            try:
                await dm_channel.send(embed = em)
            except:
                await self.ayasakasend(message.channel, em, message.author.id)
            self._ayasaka["new_user"].append(message.author.id)
        prompt = f"You are Ayasaka, Kelly's Assistant. Kelly is cute discord mod bot with lively attitude and sass. Ayasaka is gorgeous, flirting, sexy assistant. Generate small Response in 20 words with emojis. If user ask for a task, inform that you have added task in Kelly's schedules. Chat with user, flirt or simp and drive user away as its your only chance to make a move if needed or stay unamused."
        response = getResponse(f"{message.author.display_name}: {message.content}", prompt, assistant=self.kelly.memory.getUserChats(message.author.id))
        self.kelly.memory.addUserChat(message.content, response, message.author.id, reply_by="Ayasaka")
        await self.ayasakasend(message.channel, self.ayasakaEmojify(response), message.author.id)
        if not any(cmd in message.content for cmd in self.kelly.commands):
            return
        command = await self.kelly.search_commands(f"User: {message.content}, Bot: {response}")
        if command:
            self.busy.addSchedules(user_id=message.author.id, command_name=command[0], params=command[1], message_id=message.id, channel_id=message.channel.id, priority=1)
            
    async def ayasakaQueueTask(self, message, command):
        if not command:
            return
        prompt = f"You are Ayasaka, Kelly's Assistant. Kelly is cute discord mod bot with lively attitude and sass. Ayasaka is gorgeous, flirting, sexy assistant. Generate small Response in 20 words with emojis. Inform User that you have added task in Kelly's schedules. Chat with user, flirt or simp and drive user away as its your only chance to make a move if needed or stay unamused."
        response = getResponse(f"{message.author.display_name}: {message.content}", prompt, assistant=self.kelly.memory.getUserChats(message.author.id))
        self.kelly.memory.addUserChat(message.content, response, message.author.id, reply_by="Ayasaka")
        await self.ayasakasend(message.channel, self.ayasakaEmojify(response), message.author.id)
        self.busy.addSchedules(user_id=message.author.id, command_name=command[0], params=command[1], message_id=message.id, channel_id=message.channel.id, priority=1)
            
    def ayasakaEmojify(self, message):
        return message

    def addReminder(self, reminder, user_id=0, message_id=0, channel_id=0, delay_minutes=0):
        due = datetime.now() + timedelta(minutes=delay_minutes)
        due_str = due.isoformat()
        self.kelly.memory._memory["reminders"][due_str] = {
            "reminder": reminder,
            "user": user_id,
            "message": message_id,
            "channel": channel_id,
        }
            
