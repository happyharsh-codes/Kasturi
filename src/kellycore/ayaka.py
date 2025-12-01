from __init__ import*
from src.kellycore.kellybusy import KellyBusy

class Ayaka:
    """
    Ayaka - Kelly's Personal Assistant.

    Responsibilities:
        - Manage Kelly's daily schedule
        - Maintain availability calendar
        - Inform users when Kelly is free or busy/sleepy/lazy
        - Automatically reschedule tasks when Kelly is too tired/sleepy/lazy/busy
        - Remind Kelly about pending tasks (from KellyBusy)
        - Defer or decline user requests if overloaded

    This works closely with:
        - KellyBusy (task queue)
        - KellyMood (sleepy/lazy/hectic moods)
        - KellyMemory (long-term reminders)
    """

    def __init__(self, kelly):
        self.kelly = kelly
        self.busy = KellyBusy()
    
    async def ayakaasend(self, channel, content, uid):
        try:
            webhook = await channel.create_webhook(name="Ayaka")
            await webhook.send(content= f"<@{uid}>" + content, username="Ayaka", avatar_url=f"https://raw.githubusercontent.com/happyharsh-codes/Kasturi/refs/heads/main/assets/ayaka_{ranint(1,3)}")
            await webhook.delete()
        except:
            await channel.send(f"**Ayaka**: <@{uid}>" + content)

    # ----------------------------------------------------------------------
    #   KELLY'S SCHEDULE MANAGER
    # ----------------------------------------------------------------------

    def addTask(self, guild_id, message_id, channel_id, ai_result):
        """Adds taks to Kelly's schedule. And automatically sets it schedule."""
        if not str(guild_id) in Memory["schedules"]:
            Memory["schedules"][str(guild_id)] = [ {"message": message_id, "channel": channel_id, "task": ai_result, "time": datetime.now() + timedelta(seconds=randint(1,2)) } ]
        else:
            time = self.busy.getNextAvailableTime(guild_id) + timedelta(seconds=randint(1,2))
            Memory["schedules"][str(guild_id)].append({"message": message_id, "channel": channel_id, "task": ai_result, "time": time})
        
    async def performTask(self, guild_id):
        """Automatically performs the first task on her schedule"""
        schedules = Memory["schedules"].get(str(guild_id), None)
        if not schedules:
            return
        do_now = schedules.pop(0)
        try:
            channel = await self.kelly.client.fetch_channel(do_now["channel"])
            msg = await channel.fetch_message(do_now["message"])
        except:
            return
        await self.kelly.runCommand(msg, do_now["task"])
        if schedule:
            Memory["schedules"][str(guild_id)] = schedule 
        else:
            del Memory["schedules"][str(guild_id)]
            
    # ----------------------------------------------------------------------
    #   REMINDERS
    # ----------------------------------------------------------------------

    def addReminder(self, task, delay_minutes=20):
        """
        Add reminder to check on a task later.
        """
        due = datetime.now() + timedelta(minutes=delay_minutes)
        self.reminders.append({"task": task, "due": due})

    def getDueReminders(self):
        """
        Get reminders whose time has come.
        """
        now = datetime.now()
        due_list = [r for r in self.reminders if r["due"] <= now]
        self.reminders = [r for r in self.reminders if r["due"] > now]
        return due_list

    # ----------------------------------------------------------------------
    #   USER INTERACTION WRAPPER
    # ----------------------------------------------------------------------

    async def ayakaQuery(self, message, mood, type):
        """
        Handles user requests BEFORE Kelly receives them.
        
        Flow:
            1. Check KellyBusy
            2. Manage schedule
        """
        uid = message.author.id

        # If Kelly is too busy/sleepy/laz/tiredy, assistant manages
        state = self.busy.isBusy(mood, message.author.id, type)
        if state:
            prompt = f"You are Ayaka, Kelly's Assistant\nKelly is currently very {state}\nGenerate: Your Response in 20 words with emojis"
            response = getResponse(f"{message.author.display_name}: {message.content}", prompt)
            await self.ayakasend(message.channel, self.akayaEmojify(response), message.author.id)
            return True 
        
        # If schedule is overloaded -> Clear Decline
        if not self.busy.isKellyFree(message.guild.id):
            prompt = f"You are Akaya, Kelly's Assistant\nKelly's schedules are overloaded already, clearly decline user request.\nGenerate: Your Response in 20 words with emojis"
            response = getResponse(f"{message.author.display_name}: {message.content}", prompt)
            await self.ayakasend(message.channel, self.akayaEmojify(response), message.author.id)
            return True

        # If schedules but slot available -> Schedule task
        upnext = self.busy.getNextAvailableTime(message.guild.id)
        if upnext:
            prompt = f"You are Akaya, Kelly's Assistant\nKelly is currently busy so you schedule user task for later.\nGenerate: Your Response telling the user that their task is scheduled after {upnext}s in 20 words with emojis"
            response = getResponse(f"{message.author.display_name}: {message.content}", prompt)
            await self.ayakasend(message.channel, self.akayaEmojify(response), message.author.id)
            prompt2 = f"""You are Kelly/Kasturi kelly discord mod bot(lively with mood attitude and sass)
                Current status: {current_status}
                Generate Json dict using kelly response and mood
                - respect: (-10 : +10) (int)
                - mood: (happy(default)/sad/depressed/angry/annoyed/lazy/sleepy/busy/mischevious) (from these only)
                - personality_change: {{(personality_name): +/- 10 (int)}}
                - info: (str) (small info about user behaviour and type)
                - command: (default none for talking) {self.commands} (eg: {{"command_name":{{"param1": "value"}}}})"""
            
            self.addTask(message.guild.id, message.id, message.channel.id, result)
            return True 
            
        return False  # Kelly may proceed

    def akayaEmojify(self, message):
        return message
