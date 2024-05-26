from abc import abstractmethod
from typing import List, Literal
from talipp.ohlcv import OHLCV
from .order import Order

def final(method):
    def new_method(self, *args, **kwargs):
        raise TypeError(f"Cannot override final method '{method.__name__}'")
    return new_method


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

    @final
    def current_candle(self, interval: int) -> dict:
        return self.fetch_current_candle(interval)

    def all_candles(self, interval: int) -> List[dict]:
        return self.fetch_candles(interval)

    def fetch_current_candle(self, candle_range: int) -> dict:
        pass

    def fetch_candles(self, candle_range: int) -> List[dict]:
        pass

    def longOrder(
        self, price: float, quantity: int, takeprofit: float, stoploss: float
    ) -> Order:
        pass

    def shortOrder(
        self, price: float, quantity: int, takeprofit: float, stoploss: float
    ) -> Order:
        pass

    def exit_position(
        self,
        currnt_position: Literal["LONG", "SHORT", "NONE"],
        price: float,
        quantity: int,
        limit: bool = False,
    ):
        pass