# from apscheduler.executors.pool import ProcessPoolExecutor, ThreadPoolExecutor

from candles import CandleManager

from .common import *
from .constants import DHAN_INSTRUMENTS
from .dockerd import *

# scheduler.start()
from .handler import *
from .processor import Processor

# from api.config import SQLALCHEMY_DATABASE_URI
from .redis_manager import BacktestRedis, RedisManager

redis_instance: RedisManager = RedisManager()
redis_instance_backtest: BacktestRedis = BacktestRedis()

# from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
# from apscheduler.schedulers.background import BackgroundScheduler


# jobstores = {"default": SQLAlchemyJobStore(url=SQLALCHEMY_DATABASE_URI)}
# executors = {"default": ThreadPoolExecutor(20), "processpool": ProcessPoolExecutor(5)}
# job_defaults = {"coalesce": False, "max_instances": 3}
# scheduler = BackgroundScheduler(
#     jobstores=jobstores, executors=executors, job_defaults=job_defaults
# )
