from .dhan_market_feed import *
from .candles import *
from .indicators import *
from .misc import *
from .schedule import *
from .constants import *

from utils.processor import Processor
from utils import scheduler

marketDataQuote = DhanMarketFeed(analyser=analyser)
marketDataQuote.subscription_code = 17
marketFeedQuote = Processor(marketDataQuote)

scheduler.add_job(
    func=schedule_until_sunday,
    trigger="cron",
    day_of_week="mon",
    hour=5,
    minute=30,
    replace_existing=True,
    id="schedule_week",
)
