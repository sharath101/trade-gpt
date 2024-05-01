from talipp.ohlcv import OHLCV

from order_manager.models import Order
from strategy import Strategy
from utils import adjust_perc


class EngulfingStrategy(Strategy):
    def __init__(self):
        super().__init__()

    def analyse(self, candle: OHLCV) -> tuple[Order | None, float]:
        self.candles.append(candle)
        candles = self.candles

        if len(candles) <= 1:
            return None, 0

        curr_price = float(candles[-1].close)
        order: Order = None
        if (
            candles[-2].close > candles[-2].open
            and candles[-1].close < candles[-2].open
        ):
            order = self.shortOrder(
                curr_price,
                1,
                adjust_perc(curr_price, -1),
                adjust_perc(curr_price, 1),
            )
        elif (
            candles[-2].open > candles[-2].close
            and candles[-1].close > candles[-2].open
        ):
            order = self.longOrder(
                curr_price,
                1,
                adjust_perc(curr_price, 1),
                adjust_perc(curr_price, -1),
            )

        if order:
            return order, 1
        return None, 0
