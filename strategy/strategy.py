from typing import List

from talipp.ohlcv import OHLCV

from order_manager import Order, OrderManager
from utils import redis_instance


class Strategy:
    def __init__(self, symbol: str, candle_range: int, balance: int, backtesting=False):
        self.backtesting = backtesting
        self.candles: List[OHLCV] = []
        self.symbol = symbol
        self.candle_range = candle_range
        self.order_manager = OrderManager(balance, backtesting)

    def fetchData(self):
        if not self.backtesting:
            redis_key = f"candle_{self.symbol}_{self.candle_range}"
            data = redis_instance.get(redis_key)
            self.candles = data

    def longOrder(
        self, price: float, quantity: int, takeprofit: float, stoploss: float
    ):
        order = Order(
            symbol=self.symbol,
            quantity=quantity,
            price=price,
            trigger_price=price,
            transaction_type="BUY",
            bo_takeprofit=takeprofit,
            bo_stoploss=stoploss,
        )
        self.order_manager.place_order(order)

    def shortOrder(
        self, price: float, quantity: int, takeprofit: float, stoploss: float
    ):
        order = Order(
            symbol=self.symbol,
            quantity=quantity,
            price=price,
            trigger_price=price,
            transaction_type="SELL",
            bo_takeprofit=takeprofit,
            bo_stoploss=stoploss,
        )
        self.order_manager.place_order(order)

    def exit_position(self):
        self.order_manager.exit_position(self.symbol)
