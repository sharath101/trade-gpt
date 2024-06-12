import pickle
from typing import List

from app import logger, socketio, strategy_events
from dataclass import MarketQuoteData, Order
from order_manager import OrderManager
from utils import CandleManager

from .market_feed import MarketFeed


class LiveTrade:

    def __init__(
        self, symbols: List[str], channel: str, market_feed: MarketFeed, candle_interval
    ):
        self.market_feed: MarketFeed = market_feed
        self.symbols = symbols
        self.channel = channel
        self.order_manager = OrderManager(symbols, 20000)
        self.candle_manager = CandleManager(candle_interval)
        self.socketio = socketio
        self.register_order_channel(channel)
        self.market_feed.set_credentials(symbols, self.analyse)

    async def connect(self):
        print("connecting in liveTrade")
        await self.market_feed.connect_feed()

    def analyse(self, data: MarketQuoteData):
        self.candle_manager.process_tick(
            data.timestamp, data.price, data.quantity, data.symbol
        )
        for symbol in self.symbols:
            current_candle = self.candle_manager.get_latest_candle(symbol)
            self.order_manager.next(
                symbol,
                current_candle,
                data.timestamp,
                strategy_events.emit,
                self.channel,
                True,
            )

    def register_order_channel(self, channel: str):

        @self.socketio.on(channel)
        def handle_order(data):
            order: Order = pickle.loads(data)["order"]
            logger.info(f"Order received: {order}")
            self.order_manager.place_order(order)
