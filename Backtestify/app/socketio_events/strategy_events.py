import json

from app import logger
from dataclass import Order


def register_strategy_events(socketio):

    @socketio.on("strategy_connect")
    def handle_connect():
        logger.info("Strategy service connected")
        socketio.send("Strategy service connected")

    @socketio.on("order")
    def handle_order(data):
        order: Order = json.loads(data)
        logger.info(f"Order recieved: {order}")

    @socketio.on("strategy_disconnect")
    def handle_strategy_disconnect():
        logger.info("Strategy service disconnected")
