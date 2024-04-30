from talipp.ohlcv import OHLCV

from strategy import Strategy
from utils import adjust_perc


class EngulfingStrategy(Strategy):
    def __init__(self, symbol, candle_interval, balance, backtesting=False):
        super(EngulfingStrategy, self).__init__(
            symbol, candle_interval, balance, backtesting
        )
        pass

    def analyse(self, candle: OHLCV):
        self.order_manager.analyse(candle)
        if self.backtesting:
            self.candles.append(candle)
        else:
            self.fetchData()
        candles = self.candles

        if len(candles) <= 1:
            return

        curr_price = float(candles[-1].close)
        if (
            candles[-2].close > candles[-2].open
            and candles[-1].close < candles[-2].open
        ):
            self.shortOrder(
                curr_price,
                1,
                adjust_perc(curr_price, -1.0),
                adjust_perc(curr_price, 1.0),
            )
        elif (
            candles[-2].open > candles[-2].close
            and candles[-1].close > candles[-2].open
        ):
            self.longOrder(
                curr_price,
                1,
                adjust_perc(curr_price, 1.0),
                adjust_perc(curr_price, -1.0),
            )
