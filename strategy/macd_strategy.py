from dataclass import Order
from baseclasses import Strategy
from utils import adjust_perc


class MACDStrategy(Strategy):
    def __init__(self):
        super().__init__()
        pass

    def analyse(self, current_price: float) -> tuple[Order | None, float]:

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
                    price=current_price,
                    transaction_type="BUY",
                    trigger_price=current_price,
                    bo_takeprofit=adjust_perc(current_price, 2),
                    bo_stoploss=adjust_perc(current_price, -0.25),
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
                    price=current_price,
                    transaction_type="SELL",
                    trigger_price=current_price,
                    bo_takeprofit=adjust_perc(current_price, -2),
                    bo_stoploss=adjust_perc(current_price, 0.25),
                )
        if order:
            return order, 1
        return None, 0
