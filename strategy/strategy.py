from typing import List

from talipp.ohlcv import OHLCV

from order_manager import Order, OrderManager
from utils import redis_instance


class Strategy:
    def __init__(self, symbol, candle_range, backtesting=False):
        self.backtesting = backtesting
        self.candles = List[OHLCV]
        self.symbol = symbol
        self.candle_range = candle_range
        self.order_manager = OrderManager()

    def fetchData(self):
        if not self.backtesting:
            redis_key = f"candle_{self.symbol}_{self.candle_range}"
            data = redis_instance.get(redis_key)
            self.candles = data

    def buyOrder(self, price, quantity, takeprofit, stoploss):
        order = Order(
            symbol=self.symbol,
            quantity=quantity,
            price=price,
            transaction_type="BUY",
            bo_profit_val=takeprofit,
            bo_stoploss_val=stoploss,
        )
        self.order_manager.place_order(order)

    def sellOrder(self, price, quantity, takeprofit, stoploss):
        order = Order(
            symbol=self.symbol,
            quantity=quantity,
            price=price,
            transaction_type="SELL",
            bo_profit_val=takeprofit,
            bo_stoploss_val=stoploss,
        )
        self.order_manager.place_order(order)

    def exit_position(self):
        self.order_manager.exit_position(self.symbol)
