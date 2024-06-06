from abc import abstractmethod
from typing import List, Literal

from dataclass import Order
from talipp.ohlcv import OHLCV


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

    def longOrder(
        self,
        order_trigger: float,
        price: float,
        quantity: int,
        takeprofit: float,
        stoploss: float,
    ) -> Order:
        order = Order(
            symbol="SBIN",
            quantity=quantity,
            price=price,
            trigger_price=order_trigger,
            transaction_type="BUY",
            bo_takeprofit=takeprofit,
            bo_stoploss=stoploss,
        )

        return order

    def shortOrder(
        self,
        order_trigger: float,
        price: float,
        quantity: int,
        takeprofit: float,
        stoploss: float,
    ) -> Order:
        order = Order(
            symbol="SBIN",
            quantity=quantity,
            price=price,
            trigger_price=order_trigger,
            transaction_type="SELL",
            bo_takeprofit=takeprofit,
            bo_stoploss=stoploss,
        )

        return order
