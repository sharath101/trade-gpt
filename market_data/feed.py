import asyncio
import multiprocessing


class Feed:
    def __init__(self, obj, *args, **kwargs):
        self.obj = obj
        self.args = args
        self.kwargs = kwargs
        self.loop = None
        self.process = None

    async def starter(self):
        asyncio.set_event_loop(self.loop)
        await self.obj.connect(*self.args, **self.kwargs)

    def start(self):
        if self.process is None:
            pass
        else:
            if self.process.is_alive():
                self.stop()
        self.process = multiprocessing.Process(target=self._start)
        self.process.start()

    def stop(self):
        if self.process is None:
            return
        self.process.terminate()
        self.process.join()

    def _start(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.starter())
