import asyncio

from src.utils.helpers import Helpers

class LoopControl:
    def __init__(self):
        self.inactive_task = None
        self.alone_task = None

    async def inactive(self, halt_time, callback):
        await asyncio.sleep(halt_time)
        Helpers.cancel_task(self.alone_task)
        self.alone_task = None
        await callback()

    async def alone(self, halt_time, callback):
        await asyncio.sleep(halt_time)
        Helpers.cancel_task(self.inactive_task)
        self.inactive_task = None
        await callback()

    async def become_inactive(self, timeout, callback):
        self.inactive_task = asyncio.create_task(self.inactive(timeout, callback))

    async def become_alone(self, timeout, callback):
        self.alone_task = asyncio.create_task(self.alone(timeout, callback))

    def cancel_tasks(self):
        Helpers.cancel_task(self.inactive_task)
        Helpers.cancel_task(self.alone_task)
        self.inactive_task = None
        self.alone_task = None

    def cancel_inactive(self):
        Helpers.cancel_task(self.inactive_task)

    def cancel_alone(self):
        Helpers.cancel_task(self.alone_task)
