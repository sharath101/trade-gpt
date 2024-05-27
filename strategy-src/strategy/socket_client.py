import json
from datetime import datetime

import socketio

from .order import Order


class SocketClient:

    def __init__(self, run_strategies):
        self.run_strategies = run_strategies
        self.sio = socketio.Client()

        # Define event handlers
        self.sio.on("connect", self.on_connect)
        self.sio.on("disconnect", self.on_disconnect)
        self.sio.on("order", self.on_order)

    def on_connect(self):
        print("Connected")

    def on_disconnect(self):
        print("Disconnected")

    def emit(self, event, data):
        if self.sio.connected:
            self.sio.emit(event, json.dumps(data))

    def on_order(self, data):
        # print('Message received:', data)
        message_data = json.loads(data)
        # print(message_data)

        # extract data
        symbol = message_data.get("symbol")
        current_price = float(message_data.get("current_price"))
        timestamp = datetime.fromisoformat(message_data.get("timestamp"))
        volume = int(message_data.get("volume"))

        # run strategy
        order: Order = self.run_strategies(symbol, current_price, timestamp, volume)

        if self.sio.connected:
            self.emit("order", order)
        else:
            print("Cannot emit, not connected")

    def start(self):
        # Connect to the server
        self.sio.connect("http://host.docker.internal:5001")
        # Wait for events
        self.sio.wait()
