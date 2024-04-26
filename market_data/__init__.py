from .dhan_market_feed import DhanMarketFeed
from utils.processor import Processor
from .misc import analyser
from .schedule import schedule_week
from utils import scheduler

marketDataQuote = DhanMarketFeed(analyser=analyser)
marketDataQuote.subscription_code = 17
marketFeedQuote = Processor(marketDataQuote)

scheduler.add_job(
    func=schedule_week,
    trigger="cron",
    day_of_week="sun",
    hour=23,
    minute=55,
    replace_existing=True,
    id="schedule_week",
)
