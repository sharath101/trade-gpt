from market_feed import DhanMarketFeed
from dotenv import load_dotenv
import asyncio
from dhanhq import marketfeed
load_dotenv()

async def ticker_analyser(data):
    print(data)

async def quote_analyser(data):
    print(data)

async def depth_analyser(data):
    print(data)


async def main():

    marketFeedDepth = DhanMarketFeed(depth_analyser, [(marketfeed.NSE, "1333")], 19)
    marketFeedQuote = DhanMarketFeed(quote_analyser, [(marketfeed.NSE, "1333")], 19)
    marketFeedTicker = DhanMarketFeed(ticker_analyser, [(marketfeed.NSE, "1333")], 15)

    t1 = asyncio.create_task(marketFeedDepth.connect())
    t2 = asyncio.create_task(marketFeedQuote.connect())
    await marketFeedTicker.connect()

asyncio.run(main())