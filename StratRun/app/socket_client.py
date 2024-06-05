import json
import pickle

import socketio

from .order import Order
from .strategy_manager import StrategyManager


class SocketClient:

    def __init__(self, strategy_manager: StrategyManager):
        self.strategy_manager = strategy_manager

        self.sio = socketio.Client()

        # Define event handlers
        self.sio.on("connect", self.on_connect)
        self.sio.on("disconnect", self.on_disconnect)
        self.sio.on("order", self.on_order)

    def on_connect(self):
        print("connected")

    def on_disconnect(self):
        pass

    def emit(self, event, data):
        if self.sio.connected:
            self.sio.emit(event, json.dumps(data))

    def on_order(self, data):
        """Data received from backtester via websocket"""
        message_data = json.loads(data)
        print(message_data)

        """Available Data extraction"""
        symbol = message_data.get("symbol")
        candle = message_data.get("candle")

        """This runs all the strategies for the received data"""
        order: Order = self.strategy_manager.run_strategies(symbol, candle)
        print(order)

        if self.sio.connected and order:
            """TODO:order to be emitted must be json"""
            self.emit("order", order)
        else:
            print("Unable to send order, socket disconnected")

    def start(self, socket_url):
        """Attempt to connect to socket"""
        self.sio.connect(socket_url)
        # Wait for events
        self.sio.wait()
