import json
import pickle

from dataclass import Order
from flask_socketio import SocketIO

from app import logger


class StrategyEvents:
    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
        self.register_events()

    def register_events(self):
        @self.socketio.on("strategy_connect")
        def handle_connect(data):
            logger.info("Strategy service connected")
            return True

        @self.socketio.on("order")
        def handle_order(data):
            order: Order = Order(pickle.loads(data))
            logger.info(f"Order received: {order}")

        @self.socketio.on("strategy_disconnect")
        def handle_strategy_disconnect():
            logger.info("Strategy service disconnected")

    def emit(self, event: str, data):
        logger.info(f"Emitting Event: channel: {event}, data: {data}")
        self.socketio.emit(event, pickle.dumps(data))
