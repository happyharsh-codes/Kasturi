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

    def __init__(self):
        pass

    def isBusy(self, mood, uid, type):
        """Return whether Kelly is busy. Based on Mood not on Schedule."""
        #Never busy for friends
        if uid in Database["friends"]:
            return False 
        if mood["lazy"] > 90 or mood["sleepy"] > 90:
            #Server Owners 40% chance listen on even busy
            if "Server owner" in type and randint(1,10) <= 4:
                return False
            #Server Moderators 20% chance listens even on busy
            elif "Moderator" in type and randint (1,5) == 1:
                return False
            elif mood["lazy"] > 90:
                return "lazy"
            elif mood["sleepy"] > 90:
                return "sleepy"
        return False

    # ----------------------------------------------------------------------
    #   AVAILABILITY CHECK
    # ----------------------------------------------------------------------

    def isKellyFree(self, guild_id):
        """
        Returns True if Kelly has free slots on her schedule.
        """
        if str(guild_id) not in Memory["schedules"]:
            return True
        if Memory["schedules"][str(guild_id)] and len(Memory["schedules"][str(guild_id)]) > 5:
            return False
        return True
        
    def getNextAvailableTime(self, guild_id):
        """
        Returns Kelly's next free time slot today.
        Returns only when empty slot is available on Kelly's schedule.
        Otherwise returns None
        """
        if not str(guild_id) in Memory["schedules"]:
            return None
        schedules = Memory["schedules"][str(guild_id)]
        if schedules:
            if len(schedules) > 5:
                return None
            last_time = max(entry["time"] for entry in schedules)
            return last_time
        return None
            
