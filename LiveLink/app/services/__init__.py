from app.utils.schedule import *

from .binance_market_feed import BinanceMarketFeed
from .dhan_market_feed import DhanMarketFeed
from .live_trade import LiveTrade
from .market_feed import MarketFeed

# scheduler.add_job(
#     func=schedule_until_sunday,
#     trigger="cron",
#     day_of_week="mon",
#     hour=5,
#     minute=30,
#     replace_existing=True,
#     id="schedule_week",
# )
