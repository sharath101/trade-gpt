from abc import abstractmethod
from typing import List, Literal
from talipp.ohlcv import OHLCV
from utils import redis_instance, redis_instance_backtest
from dataclass import Order
from api import logger


class Strategy:
    current_position: Literal["LONG", "SHORT", "NONE"] = "NONE"
    order_status: Literal["PENDING", "TRADED", "CANCELLED", "CLOSED", "REJECTED"] = (
        "PENDING"
    )
    symbol: str
    current_order: Order = None
    backtesting: bool = False

    def __init__(self):
        self.candles: List[OHLCV] = []

    @abstractmethod
    def analyse(self, candle: OHLCV) -> tuple[Order | None, float]:
        pass

    def current_candle(self, interval: int) -> dict:
        return self.fetch_current_candle(interval)

    def all_candles(self, interval: int) -> List[dict]:
        return self.fetch_candles(interval)

    def fetch_current_candle(self, candle_range: int) -> dict:
        try:
            candle_key = f"candle_{self.symbol}_{candle_range}_current"
            if not self.backtesting:
                data = redis_instance.get(candle_key)
            else:
                data = redis_instance_backtest.get(candle_key)
        except Exception as e:
            logger.error(f"Error fetching current candle: {e}")
            return {}
        if data is None:
            return {}
        return data

    def fetch_candles(self, candle_range: int) -> List[dict]:
        try:
            candles_key = f"candle_{self.symbol}_{candle_range}"
            if not self.backtesting:
                data = redis_instance.get(candles_key)
            else:
                data = redis_instance_backtest.get(candles_key)
        except Exception as e:
            logger.error(f"Error fetching candles: {e}")
            return []
        if data is None:
            return []
        return data

    def longOrder(
        self, price: float, quantity: int, takeprofit: float, stoploss: float
    ) -> Order:
        order = Order(
            symbol="idk",
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
            symbol="idk",
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
                symbol="idk",
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
                symbol="idk",
                quantity=quantity,
                price=price,
                trigger_price=0,
                transaction_type="BUY",
                bo_takeprofit=0,
                bo_stoploss=0,
                order_type=order_type,
            )

        return order
