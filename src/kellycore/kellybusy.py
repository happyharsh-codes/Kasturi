from __init__ import*

class KellyBusy:
    """
    Handles busy-state task queries.
    Kelly is busy when:
        - Kelly is either busy, sleeping, lazy or tired
    Guild owners, moderators and kelly friends and bypass this - smalll chance
    If user insists repeatedly:
        - Kelly eventually performs task immediately
    """

    def __init__(self, kelly, schedules):
        self.kelly = kelly
        self._schedules = schedules 

    def isBusy(self):
        """Return whether Kelly is busy. Based on Mood not on Schedule."""
        if len(self._schedules) > 5:
            return True
        return False
        
    def getNextFreeTime(self):
        """Returns next Kelly free of schedule time"""
        if not self._schedules or len(self._schedules) == 0:
            return datetime.now()
        last_time = max(datetime.fromisoformat(entry) for entry in self._schedules)
        return last_time

    def addSchedules(self, user_id, message_id, channel_id, chatting_in = None, moderating_in = None, command = None, params = None):
        """Adds task on Kelly's schedules"""
        due = self.getNextFreeTime() + timedelta(seconds=randint(1,120))
        self._schedules[due.isoformat()] = {
            "uid": user_id,
            "chatting": chatting_in,
            "moderating": moderating_in,
            "command": command,
            "params": params,
            "message": message_id,
            "channel": channel_id
        }
        if len(self._schedules) > 5:
            self.kelly.status = "busy"
            
    def getSchedules(self):
        return self._schedules
            
            
