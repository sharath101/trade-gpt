from flask import Flask
from flask_socketio import SocketIO
import os
import logging

app = Flask(__name__)
app.config.from_pyfile("config.py")

socketio = SocketIO()
socketio.init_app(app)

logger = app.logger
logger.setLevel("DEBUG")
handler = logging.FileHandler(app.config["LOG_FILE"])
logger.addHandler(handler)


from baseclasses import *
from dataclass import *
from database import *
from market_data import *
from brokers import *
from utils import *
from strategy import *
from order_manager import *
from backtesting import *

from api import routes, events

if not os.path.isdir(app.config["DATA"]):
    os.mkdir(os.path.join(app.config["DATA"]))
