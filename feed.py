import asyncio
import threading


class Feed:
    def __init__(self, task, *args, **kwargs):
        self.loop = None
        self.task = task
        self.args = args
        self.kwargs = kwargs
        self.thread = None
        self.tasks = []

    def run_event_loop(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    async def _run_task(self):
        try:
            task_coro = self.task(*self.args, **self.kwargs)
            task = asyncio.create_task(task_coro)
            self.tasks.append(task)
            await task
        except asyncio.CancelledError:
            pass

    def start(self):
        if callable(self.task):
            self.loop = asyncio.new_event_loop()
            self.thread = threading.Thread(
                target=self.run_event_loop, args=(self.loop,)
            )
            self.thread.start()
            self.loop.call_soon_threadsafe(self.loop.create_task, self._run_task())

    def stop(self):
        if self.loop:
            self.loop.call_soon_threadsafe(self.loop.stop)
            self.thread.join()  # Wait for the thread to finish
            for task in self.tasks:
                task.cancel()  # Cancel all pending tasks
            self.loop.call_soon_threadsafe(self.loop.close)
            self.thread = None  # Reset the thread reference
            self.loop = None  # Reset the loop reference
