from talipp.ohlcv import OHLCV
from talipp.indicators import MACD
from strategy import Strategy
from utils import adjust_perc
from order_manager import Order


class MACDStrategy(Strategy):
    def __init__(self, symbol, candle_interval, balance, backtesting=False):
        super(MACDStrategy, self).__init__(
            symbol, candle_interval, balance, backtesting
        )
        self.technical_indicators = MACD(12, 26, 9)
        pass

    def analyse(self, candle: OHLCV):
        if self.backtesting:
            self.candles.append(candle)
        else:
            self.fetchData()

        self.technical_indicators.add(candle.close)

        if self.technical_indicators[-1] is None:
            return
        if self.technical_indicators[-2] is None:
            return
        if self.technical_indicators[-3] is None:
            return
        if self.technical_indicators[-4] is None:
            return
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
                    symbol=self.symbol,
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
                    symbol=self.symbol,
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
