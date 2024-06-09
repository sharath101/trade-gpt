from app.utils.misc import analyser
from app.utils.schedule import *
from utils import candles
from utils.processor import Processor

from .dhan_market_feed import *

marketDataQuote = DhanMarketFeed(analyser=analyser)
marketDataQuote.subscription_code = 17
marketFeedQuote = Processor(marketDataQuote)

# scheduler.add_job(
#     func=schedule_until_sunday,
#     trigger="cron",
#     day_of_week="mon",
#     hour=5,
#     minute=30,
#     replace_existing=True,
#     id="schedule_week",
# )
