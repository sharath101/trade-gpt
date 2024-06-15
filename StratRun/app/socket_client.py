import json
import os
import pickle
from typing import Optional

import socketio
from dataclass import Order
from utils.type_dict import MarketData, Stocks

from .strategy_manager import StrategyManager


class SocketClient:

    def __init__(self, strategy_manager: StrategyManager):
        self.strategy_manager = strategy_manager

        self.sio = socketio.Client()
        self.channel = os.environ.get("CHANNEL", "order")
        # Define event handlers
        self.sio.on("connect", self.on_connect)
        self.sio.on("disconnect", self.on_disconnect)
        self.sio.on(self.channel, self.on_order)

    def on_connect(self):
        data = {"status": "success", "order": None}
        self.sio.emit(self.channel, pickle.dumps(data))

    def on_disconnect(self):
        pass

    def emit(self, event, data):
        if self.sio.connected:
            self.sio.emit(event, data)

    def on_order(self, data):
        """Data received from backtester via websocket"""
        message_data = pickle.loads(data)

        """Available Data extraction"""
        symbol: Stocks = message_data.get("symbol")
        market_data: MarketData = message_data.get("market_data")

        """This runs all the strategies for the received data"""
        order: Optional[Order] = self.strategy_manager.run_strategies(
            symbol, market_data
        )
        if order:
            print(f"Order: {order}")

        data = {"status": "success", "order": None}
        if order:
            data["order"] = order
        self.emit(self.channel, pickle.dumps(data))

    def start(self, socket_url):
        """Attempt to connect to socket"""
        self.sio.connect(socket_url)
        # Wait for events
        self.sio.wait()
