from __init__ import*

class Akira:
    """
    Akira - Kelly's Personal Assistant.

    Responsibilities:
        - Manage Kelly's daily schedule
        - Maintain availability calendar
        - Inform users when Kelly is free or busy/sleepy/lazy
        - Automatically reschedule tasks when Kelly is too tired/sleepy)busy
        - Remind Kelly about pending tasks (from KellyBusy)
        - Defer or decline user requests if overloaded

    This works closely with:
        - KellyBusy (task queue)
        - KellyMood (sleepy/lazy/hectic moods)
        - KellyMemory (long-term reminders)
    """

    def __init__(self, kelly):
        self.kelly = kelly

        # Kelly's availability system
        self.schedule = []  # [{"task": str, "time": datetime}]
        self.daily_limit = 10   # max tasks per day
        self.reminders = []     # [{"task": str, "due": datetime}]

    # ----------------------------------------------------------------------
    #   AVAILABILITY CHECK
    # ----------------------------------------------------------------------

    def isKellyFree(self):
        """
        Returns True if Kelly has free slots today.
        """
        today_tasks = [t for t in self.schedule if self._sameDay(t["time"], datetime.now())]
        return len(today_tasks) < self.daily_limit

    def getNextAvailableTime(self):
        """
        Returns Kelly's next free time slot today.
        """
        today_tasks = sorted(
            [t for t in self.schedule if self._sameDay(t["time"], datetime.now())],
            key=lambda x: x["time"]
        )

        if not today_tasks:
            return datetime.now()

        last_task = today_tasks[-1]["time"]
        return last_task + timedelta(minutes=30)

    # ----------------------------------------------------------------------
    #   ADD TASK TO KELLY'S SCHEDULE
    # ----------------------------------------------------------------------

    def bookTask(self, task_name, duration=10):
        """
        Books a new task for Kelly.

        If Kelly is too busy:
            - defer the task
            - assistant speaks politely to user
        """
        next_time = self.getNextAvailableTime()

        self.schedule.append({
            "task": task_name,
            "time": next_time
        })

        return next_time

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

    async def assistUserRequest(self, message):
        """
        Handles user requests BEFORE Kelly receives them.
        
        Flow:
            1. Check GIYU
            2. Check KellyBusy
            3. Check schedule
        """
        uid = message.author.id

        # If Kelly is too sleepy/lazy, assistant manages
        mood = self.kelly.mood.getMood()
        if mood in ["sleepy", "lazy"]:
            await message.reply("Kelly is a bit tired right now. I'll handle this for her.")
            return False  # Assistant takes over
        
        # If schedule is overloaded
        if not self.isKellyFree():
            next_free = self.getNextAvailableTime()
            text = f"Kelly is fully booked right now. She'll be free at **{next_free.strftime('%I:%M %p')}**."
            await message.reply(text)
            self.kelly.busy.queueTask(message)  # Queue for later
            return False

        return True  # Kelly may proceed

    # ----------------------------------------------------------------------
    #   INTERNAL HELPERS
    # ----------------------------------------------------------------------

    def _sameDay(self, t1, t2):
        """Check if two datetimes belong to the same day."""
        return t1.date() == t2.date()
