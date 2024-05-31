from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

from api import app

db = SQLAlchemy(app)

from .api_key import APIKey
from .market_holidays import MarketHolidays
from .order_book import OrderBook
from .symbol import Symbol
from .dhan_order_book import DhanOrderBook
from .virtual_order_book import VirtualOrderBook
from .strategy_book import StrategyBook
from .users import Users

engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
connection = engine.connect()

with app.app_context():
    db.create_all()
