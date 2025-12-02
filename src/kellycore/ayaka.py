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
            if isinstance(content, Embed):
                await webhook.send(content= f"<@{uid}> ", embed=content, username="Ayaka", avatar_url=f"https://raw.githubusercontent.com/happyharsh-codes/Kasturi/refs/heads/main/assets/ayaka_{randint(1,3)}.png")
            else:
                await webhook.send(content= f"<@{uid}> " + content, username="Ayaka", avatar_url=f"https://raw.githubusercontent.com/happyharsh-codes/Kasturi/refs/heads/main/assets/ayaka_{randint(1,3)}.png")
            await webhook.delete()
        except:
            if isinstance(content, Embed):
                await channel.send(f"**Ayaka**: <@{uid}> ", embed=content)
            else:
                await channel.send(f"**Ayaka**: <@{uid}> " + content)

    # ----------------------------------------------------------------------
    #   KELLY'S SCHEDULE MANAGER
    # ----------------------------------------------------------------------

    def addTask(self, guild_id, message_id, channel_id, ai_result):
        """Adds taks to Kelly's schedule. And automatically sets it schedule."""
        if not str(guild_id) in Memory["schedules"]:
            due = datetime.now() + timedelta(seconds=randint(1,2))
            Memory["schedules"][due.isoformat()] = {"message": message_id, "channel": channel_id, "task": ai_result } 
        else:
            due = self.busy.getNextAvailableTime(guild_id) + timedelta(seconds=randint(1,2))
            Memory["schedules"][due.isoformat()] = {"message": message_id, "channel": channel_id, "task": ai_result}
        
    async def performTask(self):
        """Automatically performs the task on her schedule"""
        schedules = []
        now = datetime.now()
        for due_str in list(Memory["schedules"].keys()):
            due = datetime.fromisoformat(due_str)
            if now >= due:
                schedules.append(Memory["schedules"][due_str])
                del Memory["schedules"][due_str]
        if not schedules:
            return
        for do_now in schedules:
            try:
                channel = await self.kelly.client.fetch_channel(do_now["channel"])
                msg = await channel.fetch_message(do_now["message"])
                await self.kelly.runCommand(msg, do_now["task"])
            except:
                continue 
            
    # ----------------------------------------------------------------------
    #   REMINDERS
    # ----------------------------------------------------------------------

    def addReminder(self, task, message, delay_minutes=20):
        """
        Add reminder to check on a task later.
        """
        due = datetime.now() + timedelta(minutes=delay_minutes)
        Memory["reminders"][due.isoformat()] = {"message": message.id, "channel": message.channel.id, "task": task}

    def getDueReminders(self):
        """
        Get reminders whose time has come.
        """
        now = datetime.now()
        due_list = []
        for due_str in list(Memory["reminders"].keys()):
            due = datetime.fromisoformat(due_str)
            if now >= due:
                due_list.append(Memory["reminders"][due_str])
                del Memory["reminders"][due_str]
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
            return False
        
        # If schedule is overloaded -> Clear Decline
        if not self.busy.isKellyFree(message.guild.id):
            prompt = f"You are Akaya, Kelly's Assistant\nKelly's schedules are overloaded already, clearly decline user request.\nGenerate: Your Response in 20 words with emojis"
            response = getResponse(f"{message.author.display_name}: {message.content}", prompt)
            await self.ayakasend(message.channel, self.akayaEmojify(response), message.author.id)
            return False

        # If schedules but slot available -> Schedule task
        upnext = self.busy.getNextAvailableTime(message.guild.id)
        if upnext:
            prompt2 = f"""You are Kelly discord mod bot(lively with mood attitude and sass). Generate Json dict containing - command: (default none for talking) {self.kelly.commands} (eg: {{"command_name":{{"param1": "value"}}}})"""
            raw_result = getResponse(f"User(id = {message.author.id}): {message.content}", prompt2).lower()
            try:
                if not raw_result.startswith("```"):
                    raw_result = "```json " + raw_result + " ```"
                result = loads(raw_result.split("```json")[1].split('```')[0])
                if not result["command"]:
                    return True
            except Exception as parse_error:
                print("Could not parse Ayaka AI response:", parse_error) 
                return True
            
            prompt = f"You are Akaya, Kelly's Assistant\nKelly is currently busy so you schedule user task for later.\nGenerate: Your Response telling the user that their task is scheduled after {upnext}s in 20 words with emojis"
            response = getResponse(f"{message.author.display_name}: {message.content}", prompt)
            await self.ayakasend(message.channel, self.akayaEmojify(response), message.author.id)
            
            self.addTask(message.guild.id, message.id, message.channel.id, result)
            return False
            
        return True # Kelly may proceed

    def akayaEmojify(self, message):
        return message
