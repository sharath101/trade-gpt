import asyncio
import multiprocessing


def list_pending_tasks(loop):
    pending_tasks = [task for task in asyncio.all_tasks(loop) if not task.done()]
    return pending_tasks


class Feed:
    def __init__(self, task, *args, **kwargs):
        self.task = task
        self.args = args
        self.kwargs = kwargs
        self.loop = None
        self.thread = None
        self.process = None

    def run_event_loop(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    async def starter(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        await self.task(*self.args, **self.kwargs)

    def start(self):
        self.process = multiprocessing.Process(target=self._start)
        self.process.start()

    def stop(self):
        self.process.terminate()
        self.process.join()
        print("Feed stopped.")

    def _start(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.starter())
