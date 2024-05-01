from abc import ABCMeta, abstractmethod
from typing import List, Literal

from talipp.ohlcv import OHLCV

from order_manager import Order, OrderManager
from utils import redis_instance


class Strategy(ABCMeta):
    current_position: Literal["LONG", "SHORT", "NONE"] = "NONE"
    order_status: Literal["PENDING", "TRADED", "CANCELLED", "CLOSED", "REJECTED"] = (
        "PENDING"
    )
    current_order: Order = None

    def __init__(
        self,
        symbol: str,
        candle_range: int,
        backtesting: bool = False,
    ):
        self.backtesting = backtesting
        self.candles: List[OHLCV] = []
        self.symbol = symbol
        self.candle_range = candle_range

    @abstractmethod
    def analyse(self, candle: OHLCV) -> tuple[Order, float]:
        pass

    def fetchData(self):
        if not self.backtesting:
            redis_key = f"candle_{self.symbol}_{self.candle_range}"
            data = redis_instance.get(redis_key)
            self.candles = data

    def longOrder(
        self, price: float, quantity: int, takeprofit: float, stoploss: float
    ) -> Order:
        order = Order(
            symbol=self.symbol,
            quantity=quantity,
            price=price,
            trigger_price=price,
            transaction_type="BUY",
            bo_takeprofit=takeprofit,
            bo_stoploss=stoploss,
        )

        return order

    def shortOrder(
        self, price: float, quantity: int, takeprofit: float, stoploss: float
    ) -> Order:
        order = Order(
            symbol=self.symbol,
            quantity=quantity,
            price=price,
            trigger_price=price,
            transaction_type="SELL",
            bo_takeprofit=takeprofit,
            bo_stoploss=stoploss,
        )

        return order

    def exit_position(
        self,
        currnt_position: Literal["LONG", "SHORT", "NONE"],
        price: float,
        quantity: int,
        limit: bool = False,
    ):
        if currnt_position == "LONG":
            if limit:
                order_type = "LIMIT"
            else:
                order_type = "MARKET"
            order = Order(
                symbol=self.symbol,
                quantity=quantity,
                price=price,
                trigger_price=0,
                transaction_type="SELL",
                bo_takeprofit=0,
                bo_stoploss=0,
                order_type=order_type,
            )

        elif currnt_position == "SHORT":
            if limit:
                order_type = "LIMIT"
            else:
                order_type = "MARKET"
            order = Order(
                symbol=self.symbol,
                quantity=quantity,
                price=price,
                trigger_price=0,
                transaction_type="BUY",
                bo_takeprofit=0,
                bo_stoploss=0,
                order_type=order_type,
            )

        return order
