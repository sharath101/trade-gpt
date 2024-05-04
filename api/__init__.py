import logging

from flask import Flask
import os

app = Flask(__name__)
logger = app.logger
logger.setLevel("DEBUG")
app.config.from_pyfile("config.py")

from baseclasses import *
from dataclass import *
from database import *
from market_data import *
from brokers import *
from utils import *
from strategy import *
from order_manager import *
from backtesting import *

from api import routes

if not os.path.isdir(app.config["DATA"]):
    os.mkdir(os.path.join(app.config["DATA"]))
