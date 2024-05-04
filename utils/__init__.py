from apscheduler.executors.pool import ProcessPoolExecutor, ThreadPoolExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler

from api.config import SQLALCHEMY_DATABASE_URI
from .redis_manager import RedisManager, BacktestRedis
from .common import *
from .processor import Processor

jobstores = {"default": SQLAlchemyJobStore(url=SQLALCHEMY_DATABASE_URI)}
executors = {"default": ThreadPoolExecutor(20), "processpool": ProcessPoolExecutor(5)}
job_defaults = {"coalesce": False, "max_instances": 3}
scheduler = BackgroundScheduler(
    jobstores=jobstores, executors=executors, job_defaults=job_defaults
)

redis_instance = RedisManager()
redis_instance_backtest = BacktestRedis()

from .backtest_candles import BacktestCandleManager
