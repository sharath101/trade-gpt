from .redis_manager import RedisManager
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from sqlalchemy import create_engine
import importlib
from api import app


jobstores = {"default": SQLAlchemyJobStore(url=app.config["SQLALCHEMY_DATABASE_URI"])}
executors = {"default": ThreadPoolExecutor(20), "processpool": ProcessPoolExecutor(5)}
job_defaults = {"coalesce": False, "max_instances": 3}
scheduler = BackgroundScheduler(
    jobstores=jobstores, executors=executors, job_defaults=job_defaults
)

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

if not engine.dialect.has_table(connection, "MarketHolidays"):
    ORMTable = getattr(table_models, "MarketHolidays")
    ORMTable.__table__.create(bind=engine, checkfirst=True)
