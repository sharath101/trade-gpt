from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

from api import app

from .api_key import APIKey
from .market_holidays import MarketHolidays
from .order_book import OrderBook, OrderBookService
from .symbol import Symbol

db = SQLAlchemy(app)

engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
connection = engine.connect()

db.create_all()
