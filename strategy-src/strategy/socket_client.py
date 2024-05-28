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
        strat_manager = StrategyManager(["SBIN"], 20000, [])
        self.init_app(strat_manager.run_strategies)

    def on_disconnect(self):
        pass

    def emit(self, event, data):
        if self.sio.connected:
            self.sio.emit(event, pickle.dumps(data))

    def on_order(self, data):
        """Data received from backtester via websocket"""
        message_data = json.loads(data)

        """Available Data extraction"""
        symbol = message_data.get("symbol")
        candle = pickle.loads(message_data.get("candle"))

        """This runs all the strategies for the received data"""
        order: Order = self.run_strategies(symbol, candle)

        if self.sio.connected and order:
            """TODO:order to be emitted must be json"""
            self.emit("order", order)
        else:
            print("Unable to send order, socket disconnected")

    def start(self):
        """Attempt to connect to socket"""
        self.sio.connect("http://host.docker.internal:5001")
        # Wait for events
        self.sio.wait()
