from talipp.indicators import MACD
from talipp.ohlcv import OHLCV

from order_manager import Order
from strategy import Strategy
from utils import adjust_perc


class MACDStrategy(Strategy):
    def __init__(self):
        super().__init__()
        self.technical_indicators = MACD(12, 26, 9)
        pass

    def analyse(self, candle: OHLCV) -> tuple[Order | None, float]:
        self.candles.append(candle)

        self.technical_indicators.add(candle.close)
        order = None

        if self.technical_indicators[-1] is None:
            return None, 0
        if self.technical_indicators[-2] is None:
            return None, 0
        if self.technical_indicators[-3] is None:
            return None, 0
        if self.technical_indicators[-4] is None:
            return None, 0
        if self.technical_indicators[-1].macd is None:
            return None, 0
        if self.technical_indicators[-2].signal is None:
            return None, 0
        if (
            self.technical_indicators[-1].macd > 0
            and min(
                self.technical_indicators[-4].macd,
                self.technical_indicators[-3].macd,
                self.technical_indicators[-2].macd,
            )
            < 0
        ):

            if (
                self.technical_indicators[-1].macd
                > self.technical_indicators[-1].signal
            ):
                order = Order(
                    symbol="idk",
                    quantity=1,
                    price=candle.close,
                    transaction_type="BUY",
                    trigger_price=candle.close,
                    bo_takeprofit=adjust_perc(candle.close, 2),
                    bo_stoploss=adjust_perc(candle.close, -0.25),
                )

        elif (
            self.technical_indicators[-1].macd < 0
            and max(
                self.technical_indicators[-4].macd,
                self.technical_indicators[-3].macd,
                self.technical_indicators[-2].macd,
            )
            > 0
        ):
            if (
                self.technical_indicators[-1].macd
                < self.technical_indicators[-1].signal
            ):
                order = Order(
                    symbol="idk",
                    quantity=1,
                    price=candle.close,
                    transaction_type="SELL",
                    trigger_price=candle.close,
                    bo_takeprofit=adjust_perc(candle.close, -2),
                    bo_stoploss=adjust_perc(candle.close, 0.25),
                )
        if order:
            return order, 1
        return None, 0
