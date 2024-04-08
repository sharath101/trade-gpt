import asyncio

from dhanhq import marketfeed
from dotenv import load_dotenv

from candles import candle_1h, candle_1m, candle_5m, candle_15m
from market_feed import DhanMarketFeed

load_dotenv()


async def ticker_analyser(data):
    print(data)
    candle_1m.process_tick(data.timestamp, data.price, data.symbol)
    candle_5m.process_tick(data.timestamp, data.price, data.symbol)
    candle_15m.process_tick(data.timestamp, data.price, data.symbol)
    candle_1h.process_tick(data.timestamp, data.price, data.symbol)


async def quote_analyser(data):
    print(data)


async def depth_analyser(data):
    print(data)


from misc import INSTRUMENTS_LIST


async def main():

    marketFeedDepth = DhanMarketFeed(depth_analyser, INSTRUMENTS_LIST, marketfeed.Depth)
    marketFeedQuote = DhanMarketFeed(quote_analyser, INSTRUMENTS_LIST, marketfeed.Quote)
    marketFeedTicker = DhanMarketFeed(
        ticker_analyser, INSTRUMENTS_LIST, marketfeed.Ticker
    )

    t1 = asyncio.create_task(marketFeedDepth.connect())
    t2 = asyncio.create_task(marketFeedQuote.connect())
    await marketFeedTicker.connect()


asyncio.run(main())
