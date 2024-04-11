import asyncio
import threading


def list_pending_tasks(loop):
    pending_tasks = [task for task in asyncio.all_tasks(loop) if not task.done()]
    return pending_tasks


class Feed:
    def __init__(self, task, *args, **kwargs):
        self.loop = None
        self.task = task
        self.args = args
        self.kwargs = kwargs
        self.thread = None

    def run_event_loop(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def start(self):
        if callable(self.task):
            self.loop = asyncio.new_event_loop()
            self.thread = threading.Thread(
                target=self.run_event_loop, args=(self.loop,)
            )
            self.thread.start()
            self.loop.call_soon_threadsafe(
                self.loop.create_task, self.task(*self.args, **self.kwargs)
            )
            print("Feed started.")

    def stop(self):

        if self.loop:
            print("Stopping feed...")
            self.loop.call_soon_threadsafe(self.loop.stop)
            print("Loop stopped.")
            self.thread.join()  # Wait for the thread to finish
            print("Thread joined.")
            for task in list_pending_tasks(self.loop):
                print(f"Cancelling task {task}.")
                task.cancel()
            for task in list_pending_tasks(self.loop):
                print(f"Task {task} is still pending.")
            self.loop.call_soon_threadsafe(self.loop.close)
            print("Loop closed.")
            self.thread = None  # Reset the thread reference
            self.loop = None  # Reset the loop reference
            print("Feed stopped.")
