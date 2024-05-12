from gevent import monkey

monkey.patch_all()
import logging
import os
import socketio as s
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

app = Flask(__name__)
app.config.from_pyfile("config.py")

CORS(app, resources={r"/*": {"origins": "*"}})
client_manager = s.RedisManager()
socketio = SocketIO(
    app, async_mode="gevent", cors_allowed_origins="*", client_manager=client_manager
)

logger = app.logger
logger.setLevel("DEBUG")
# handler = logging.FileHandler(app.config["LOG_FILE"])
# logger.addHandler(handler)


from api import events, routes
from backtesting import *
from baseclasses import *
from brokers import *
from database import *
from dataclass import *
from market_data import *
from order_manager import *
from strategy import *
from utils import *

if not os.path.isdir(app.config["DATA"]):
    os.mkdir(os.path.join(app.config["DATA"]))
