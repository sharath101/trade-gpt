import json
import pickle

import socketio
from dataclass import Order

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
        message_data = pickle.loads(data)
        print(message_data)

        """Available Data extraction"""
        symbol = message_data.get("symbol")
        market_data = message_data.get("market_data")

        """This runs all the strategies for the received data"""
        order: Order = self.strategy_manager.run_strategies(symbol, market_data)
        print(f"Order: {order}")

        if self.sio.connected:
            if order:
                """TODO:order to be emitted must be json"""
                self.emit("order", pickle.dumps(order))
        else:
            print("Socket is not connected while trying to send order")

    def start(self, socket_url):
        """Attempt to connect to socket"""
        self.sio.connect(socket_url)
        # Wait for events
        self.sio.wait()
