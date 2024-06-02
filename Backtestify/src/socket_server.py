import asyncio
import json
import threading

import socketio
from aiohttp import web
from dataclass import Order


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
        task_coro = self.task(*self.args, **self.kwargs)
        task = asyncio.create_task(task_coro)
        self.tasks.append(task)
        await task

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
            self.loop.close()  # Close the loop
            self.thread = None  # Reset the thread reference
            self.loop = None  # Reset the loop reference


class SocketServer:
    # TODO: better way to manage place_order, without having dependency issues
    def __init__(
        self, place_order, server_ready_event, backtest=None, host="0.0.0.0", port=5001
    ):
        self.host = host
        self.port = port
        self.server_ready_event = server_ready_event
        self.sio = socketio.AsyncServer()

        # Define event handlers
        self.sio.on("connect", self.on_connect)
        self.sio.on("disconnect", self.on_disconnect)
        self.sio.on("order", self.on_order)

        self.app = web.Application()
        self.sio.attach(self.app)
        self.place_order = place_order
        self.backtest = backtest

    async def on_connect(self, sid, environ):
        print("Client connected:", sid)
        await self.sio.emit("message_from_server", "Welcome to the server!", room=sid)

    async def on_disconnect(self, sid):
        print("Client disconnected:", sid)

    async def on_order(self, sid, data):
        # print('Message from client:', data, Order)
        # extract order
        order: Order = json.loads(data)
        # print(data)

        # place order
        if order is not None:
            # TODO: How to set symbol
            # order.symbol = symbol
            order.exchange = "NSE_EQ"
            self.place_order(order)

    def emitter(self, payload):
        asyncio.create_task(self.sio.emit("order", json.dumps(payload)))

    async def run(self):
        print(f"Starting server on {self.host}:{self.port}")
        runner = web.AppRunner(self.app)

        await runner.setup()

        site = web.TCPSite(runner, self.host, self.port)
        print(f"Server started on http://{self.host}:{self.port}")

        await site.start()

        self.server_ready_event.set()

        await asyncio.Event().wait()
