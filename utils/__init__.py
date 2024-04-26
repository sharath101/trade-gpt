from .redis_manager import RedisManager
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler
from sqlalchemy import create_engine
import os
import importlib
from api import app

app_path = os.path.abspath(os.path.dirname(__file__))
dbpath = os.path.join(app_path, "database.db")

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{dbpath}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

scheduler = APScheduler(app=app)
redis_instance = RedisManager()
db = SQLAlchemy(app)


engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
connection = engine.connect()
table_models = importlib.import_module("utils.db_models")

if not engine.dialect.has_table(connection, "APIKey"):
    ORMTable = getattr(table_models, "APIKey")
    ORMTable.__table__.create(bind=engine, checkfirst=True)

if not engine.dialect.has_table(connection, "Symbol"):
    ORMTable = getattr(table_models, "Symbol")
    ORMTable.__table__.create(bind=engine, checkfirst=True)
