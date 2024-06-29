import asyncio
import traceback
from datetime import datetime
from typing import Callable, List

from app import logger
from binance import AsyncClient, BinanceSocketManager
from binance.enums import KLINE_INTERVAL_5MINUTE
from config import Config
from dataclass import MarketQuoteData

from .market_feed import MarketFeed


class BinanceMarketFeed(MarketFeed):

    def __init__(self):
        self.symbols = []
        self.analyse = None
        self.client = None
        self.bm = None
        self.api_key = None
        self.api_secret = None

    def set_credentials(self, symbols: List[str], analyse: Callable, interval: int):
        self.symbols = symbols
        self.analyse = analyse
        self.api_key = Config.LiveLink.BINANCE_API_KEY
        self.api_secret = Config.LiveLink.BINANCE_SECRET
        self.interval = f"{interval}m"

    async def connect(self):
        try:
            self.client = await AsyncClient.create(self.api_key, self.api_secret)
            print("Connected to Binance")
            self.bm = BinanceSocketManager(self.client)
            tasks = [self.start_symbol_socket(symbol) for symbol in self.symbols]
            await asyncio.gather(*tasks)
        except asyncio.TimeoutError:
            print(
                "TimeoutError: Could not connect to Binance API. Please check your network and try again."
            )
        except Exception as e:
            print(f"Exception during connect: {e}")
            traceback.print_exc()

    async def connect_feed(self):
        await self.connect()

    async def start_symbol_socket(self, symbol):
        async with self.bm.kline_socket(symbol, interval=self.interval) as stream:
            while True:
                res = await stream.recv()
                self.parse(res)

    def parse(self, data):
        kline = data.get("k")
        if kline:
            data = MarketQuoteData(
                symbol=kline["s"],
                price=float(kline["c"]),
                timestamp=datetime.fromtimestamp(int(kline["T"]) / 1000),
                volume=float(kline["v"]),
                open=float(kline["o"]),
                close=float(kline["c"]),
                high=float(kline["h"]),
                low=float(kline["l"]),
            )
            print(f"data: {data}")
            self.analyse(data)
        else:
            logger.error("Failed to recieve data from Binance")

    # "k": {
    #     "t": 1499404860000, 		# start time of this bar
    #     "T": 1499404919999, 		# end time of this bar
    #     "s": "ETHBTC",				# symbol
    #     "i": "1m",					# interval
    #     "f": 77462,					# first trade id
    #     "L": 77465,					# last trade id
    #     "o": "0.10278577",			# open
    #     "c": "0.10278645",			# close
    #     "h": "0.10278712",			# high
    #     "l": "0.10278518",			# low
    #     "v": "17.47929838",			# volume
    #     "n": 4,						# number of trades
    #     "x": false,					# whether this bar is final
    #     "q": "1.79662878",			# quote volume
    #     "V": "2.34879839",			# volume of active buy
    #     "Q": "0.24142166",			# quote volume of active buy
    #     "B": "13279784.01349473"	# can be ignored
    #     }
