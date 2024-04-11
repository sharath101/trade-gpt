from dhanhq import marketfeed
from dotenv import load_dotenv
from market_data import DhanMarketFeed
from feed import Feed
import time
import schedule

load_dotenv()


async def ticker_analyser(data):
    print(data)


async def quote_analyser(data):
    print(data)


async def depth_analyser(data):
    print(data)


marketFeedTicker = DhanMarketFeed(ticker_analyser, [(1, "1333")], marketfeed.Ticker)

mf = Feed(marketFeedTicker.connect)

schedule.every().minute.at(":30").do(mf.start)
schedule.every().minute.at(":40").do(mf.stop)

while True:
    schedule.run_pending()
    time.sleep(1)
    print("scheduled task running...")
