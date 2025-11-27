from __init__ import*

class KellyBusy:
    """
    Handles busy-state task queuing.
    If Kelly is busy:
        - Incoming tasks get queued
        - Kelly still replies but performs later
    If user insists repeatedly:
        - Kelly eventually performs task immediately
    """

    def __init__(self, kelly):
        self.kelly = kelly
        self.busy = False
        self.queue = []
        self.initiateBreakCounter = 0

    def isBusy(self):
        """Return whether Kelly is busy."""
        return self.busy

    def setBusy(self, val=True):
        """Set busy state."""
        self.busy = val

    def queueTask(self, message):
        """Add task to queue."""
        self.queue.append(message)
        self.initiateBreakCounter += 1

        # If user pushes too much → perform now
        if self.initiateBreakCounter >= 3:
            self.busy = False

    async def processQueue(self):
        """Execute all queued tasks when free."""
        while self.queue:
            task = self.queue.pop(0)
            await self.kelly.kellyQuery(task)

      
