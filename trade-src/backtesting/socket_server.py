import asyncio
import json

import socketio
from aiohttp import web
from dataclass import Order


class SocketServer:
    # TODO: better way to manage place_order, without having dependency issues
    def __init__(self, place_order, host="0.0.0.0", port=5001):
        self.host = host
        self.port = port
        self.sio = socketio.AsyncServer()

        # Define event handlers
        self.sio.on("connect", self.on_connect)
        self.sio.on("disconnect", self.on_disconnect)
        self.sio.on("order", self.on_order)

        self.app = web.Application()
        self.sio.attach(self.app)
        self.place_order = place_order

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

        await asyncio.Event().wait()
