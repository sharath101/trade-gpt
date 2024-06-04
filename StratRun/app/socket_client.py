import json
import pickle

import socketio

from .order import Order
from .strategy_manager import StrategyManager


class SocketClient:

    def __init__(self, run_strategies):
        self.run_strategies = run_strategies

        self.sio = socketio.Client()

        # Define event handlers
        self.sio.on("connect", self.on_connect)
        self.sio.on("disconnect", self.on_disconnect)
        self.sio.on("order", self.on_order)

    def init_app(self, run_strategies):
        self.run_strategies = run_strategies

    def on_connect(self):
        print("connected")

    def on_disconnect(self):
        pass

    def emit(self, event, data):
        if self.sio.connected:
            self.sio.emit(event, pickle.dumps(data))

    def on_order(self, data):
        """Data received from backtester via websocket"""
        message_data = json.loads(data)
        print(message_data)

        """Available Data extraction"""
        symbol = message_data.get("symbol")
        candle = pickle.loads(message_data.get("candle"))

        """This runs all the strategies for the received data"""
        order: Order = self.run_strategies(symbol, candle)
        print(order)

        if self.sio.connected and order:
            """TODO:order to be emitted must be json"""
            self.emit("order", order)
        else:
            print("Unable to send order, socket disconnected")

    def start(self, socket_url):
        """Attempt to connect to socket"""
        print("try connecting")
        self.sio.connect(socket_url)
        print("connected")
        # Wait for events
        self.sio.wait()
