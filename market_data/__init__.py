import importlib
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import create_engine
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.jobstores.redis import RedisJobStore
import os


app_path = os.path.abspath(os.path.dirname(__file__))
dbpath = os.path.join(app_path, "market_data.db")
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{dbpath}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# app.config["SCHEDULER_JOBSTORES"] = {
#     "default": RedisJobStore(host="localhost", port=6379, password=None, db=0)
# }
# app.config["SCHEDULER_API_ENABLED"] = True

jobstore = RedisJobStore(host="localhost", port=6379, password=None, db=0)
scheduler = BackgroundScheduler(jobstore={"redis": jobstore})
# scheduler = APScheduler(background_scheduler, app)
db = SQLAlchemy(app)

from market_data.models import APIKey
from market_data import routes

engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
connection = engine.connect()
table_models = importlib.import_module("market_data.models")

if not engine.dialect.has_table(connection, "APIKey"):
    ORMTable = getattr(table_models, "APIKey")
    ORMTable.__table__.create(bind=engine, checkfirst=True)
