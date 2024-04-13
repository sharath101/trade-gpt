import importlib
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler
from sqlalchemy import create_engine
from .redis_manager import RedisManager


app_path = os.path.abspath(os.path.dirname(__file__))
dbpath = os.path.join(app_path, "market_data.db")
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{dbpath}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
scheduler = APScheduler(app=app)
db = SQLAlchemy(app)

from .market_feed import DhanMarketFeed
from .feed import Feed

marketData = DhanMarketFeed(analyser=None)
marketFeed = Feed(marketData)
redis_instance = RedisManager()

from market_data import routes


engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
connection = engine.connect()
table_models = importlib.import_module("market_data.models")

if not engine.dialect.has_table(connection, "APIKey"):
    ORMTable = getattr(table_models, "APIKey")
    ORMTable.__table__.create(bind=engine, checkfirst=True)

if not engine.dialect.has_table(connection, "Symbol"):
    ORMTable = getattr(table_models, "Symbol")
    ORMTable.__table__.create(bind=engine, checkfirst=True)
