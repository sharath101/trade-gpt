from dataclass import Order
from baseclasses import Strategy
from utils import adjust_perc, redis_instance, redis_instance_backtest
from api import logger


class MACDStrategy(Strategy):
    def __init__(self):
        super().__init__()
        pass

    def analyse(self, current_price: float) -> tuple[Order | None, float]:

        all_candles = self.all_candles(5)

        order = None
        if len(all_candles) < 5:
            return None, 0
        if all_candles[-1]["MACD"] is None:
            return None, 0
        if all_candles[-2]["MACD"] is None:
            return None, 0
        if all_candles[-3]["MACD"] is None:
            return None, 0
        if all_candles[-4]["MACD"] is None:
            return None, 0
        if all_candles[-1]["MACD"].macd is None:
            return None, 0
        if all_candles[-1]["MACD"].signal is None:
            return None, 0
        if (
            all_candles[-1]["MACD"].macd > 0
            and min(
                all_candles[-4]["MACD"].macd,
                all_candles[-3]["MACD"].macd,
                all_candles[-2]["MACD"].macd,
            )
            < 0
        ):

            if all_candles[-1]["MACD"].macd > all_candles[-1]["MACD"].signal:
                order = Order(
                    symbol="idk",
                    quantity=1,
                    price=current_price,
                    transaction_type="BUY",
                    trigger_price=current_price,
                    bo_takeprofit=adjust_perc(current_price, 2),
                    bo_stoploss=adjust_perc(current_price, -0.25),
                )

        elif (
            all_candles[-1]["MACD"].macd < 0
            and max(
                all_candles[-4]["MACD"].macd,
                all_candles[-3]["MACD"].macd,
                all_candles[-2]["MACD"].macd,
            )
            > 0
        ):
            if all_candles[-1]["MACD"].macd < all_candles[-1]["MACD"].signal:
                order = Order(
                    symbol="idk",
                    quantity=1,
                    price=current_price,
                    transaction_type="SELL",
                    trigger_price=current_price,
                    bo_takeprofit=adjust_perc(current_price, -2),
                    bo_stoploss=adjust_perc(current_price, 0.25),
                )
        if order:
            return order, 1
        return None, 0
