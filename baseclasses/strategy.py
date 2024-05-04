from abc import abstractmethod
from typing import List, Literal
from talipp.ohlcv import OHLCV

from dataclass import Order


class Strategy:
    current_position: Literal["LONG", "SHORT", "NONE"] = "NONE"
    order_status: Literal["PENDING", "TRADED", "CANCELLED", "CLOSED", "REJECTED"] = (
        "PENDING"
    )
    current_order: Order = None

    def __init__(self):
        self.candles: List[OHLCV] = []

    @abstractmethod
    def analyse(self, candle: OHLCV) -> tuple[Order | None, float]:
        pass

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
