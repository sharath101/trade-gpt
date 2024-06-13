from app import logger, redis_instance
from flask_socketio import SocketIO


class ClientEvents:
    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
        self.register_events()

    def register_events(self):

        @self.socketio.on("connect")
        def handle_connect(data):
            """Handle authentication here, link SID with user.id and store in DB"""
            print(f"client connected: {data}")
            return True

        @self.socketio.on("live")
        def handle_backtest_all(data):
            pass

    def emit(self, event: str, data):
        self.socketio.emit(event, data)
