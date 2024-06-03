import logging

import socketio as s
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

socketio = SocketIO()
cors = CORS()
client_manager = s.RedisManager()


def configure_logging(app: Flask):
    logger = logging.getLogger("Backtestify")
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(app.config["LOG_FILE"])
    logger.addHandler(handler)
    return logger
