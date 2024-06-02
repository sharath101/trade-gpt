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
    order_status: Literal[
        "TRANSIT", "PENDING", "TRADED", "CANCELLED", "CLOSED", "REJECTED"
    ] = "PENDING"
    symbol: str
    current_order: Order | None = None
    # backtesting: bool = False

    def __init__(self):
        pass

    @abstractmethod
    def analyse(self, candle: OHLCV) -> tuple[Order | None, float]:
        pass

    @final
    def current_candle(self, interval: int):
        pass

    def all_candles(self, interval: int):
        pass
