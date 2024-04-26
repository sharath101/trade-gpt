from utils import scheduler
from utils.db_models import APIKey
from .dhan_market_feed import DhanMarketFeed
from .misc import analyser
from dhanhq import marketfeed
from .feed import Feed
from datetime import datetime, timedelta


class MarketScheduler:
    def __init__(self):
        self.key = None
        self.secret = None
        self.platform = None
        self.feedTicker = None
        self.feedQuote = None
        self.feedDepth = None

    def get_access_token(self, platform):
        api_keys = APIKey.query.all()
        api_keys = [
            {
                "key": key.key,
                "secret": key.secret,
                "expiry": key.expiry,
                "platform": key.platform,
            }
            for key in api_keys
        ]
        for api_key in api_keys:
            if api_key["platform"] == platform:
                if api_key["expiry"] is not None:
                    current_time = datetime.now()
                    time_later = current_time + timedelta(hours=20)
                    if current_time < time_later:
                        self.key = api_key["key"]
                        self.secret = api_key["secret"]
                        self.platform = api_key["platform"]
                        break
        else:
            self.key = None
            self.secret = None
            self.platform = None
            return False
        return True

    def scheduler_market_data(self, platform, date):
        # Debugging
        time_now = datetime.now()
        time_later = time_now + timedelta(minutes=1)
        print(f"Time later: {time_later}")
        access_keys = self.get_access_token(platform)
        if access_keys is False:
            return {
                "success": False,
                "message": "No access keys found for the platform.",
            }
        if platform == "dhan":
            self.marketTickerData = DhanMarketFeed(
                analyser, [(1, "1333")], marketfeed.Ticker, self.key, self.secret
            )
            self.feedTicker = Feed(self.marketTickerData.connect)
        if self.marketTickerData is None:
            return {
                "success": False,
                "message": "Platform is not supported.",
            }
        scheduler.add_job(
            id=f"market_data_start_{platform}_{date.year}_{date.month}_{date.day}",
            func=self.feedTicker.start,
            trigger="cron",
            year=time_later.year,
            month=time_later.month,
            day=time_later.day,
            hour=time_later.hour,
            minute=time_later.minute,
            replace_existing=True,
        )
        scheduler.add_job(
            id=f"market_data_end_{platform}_{date.year}_{date.month}_{date.day}",
            func=self.feedTicker.stop,
            trigger="cron",
            year=time_later.year,
            month=time_later.month,
            day=time_later.day,
            hour=time_later.hour,
            minute=time_later.minute + 1,
            replace_existing=True,
        )
        return {"success": True, "message": "Market data scheduler started."}
