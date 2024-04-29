from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

from api import app

db = SQLAlchemy(app)

from .api_key import APIKey
from .market_holidays import MarketHolidays
from .order_book import OrderBook, order_book_service
from .symbol import Symbol

engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
connection = engine.connect()

with app.app_context():
    db.create_all()
