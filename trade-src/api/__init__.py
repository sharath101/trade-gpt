import logging
import os

from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS

app = Flask(__name__)
app.config.from_pyfile("config.py")

CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, async_mode="gevent", cors_allowed_origins="*")

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
