import pickle

from app import logger
from flask_socketio import SocketIO


class StrategyEvents:
    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
        self.register_events()

    def register_events(self):
        @self.socketio.on("connect")
        def handle_connect(data):
            logger.info("Strategy service connected")
            return True

        @self.socketio.on("disconnect")
        def handle_strategy_disconnect():
            logger.info("Strategy service disconnected")

    def emit(self, event: str, data):
        logger.info(f"Emitting Event: channel: {event}, data: {data}")
        self.socketio.emit(event, pickle.dumps(data))
