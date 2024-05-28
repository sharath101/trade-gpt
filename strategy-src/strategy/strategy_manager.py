from typing import Dict, List, Literal, Optional

from talipp.ohlcv import OHLCV

from .order import Order
from .strategy_obj import Strategy
from .type_dict import MarketData, MarketDataList


class StrategyManager:
    """Data structure for candles stored in strategy manager:
    data = {"symbol": {"interval": []}}
    """

    def __init__(self, symbols: List[str], balance: float, strategies: List[Strategy]):
        self.symbols: List[str] = symbols
        self.strategies: List[Strategy] = strategies
        self.balance: float = balance
        self.candles: Dict[str, Dict[int, MarketDataList]] = {}

        for symbol in self.symbols:
            """Initializing a dictionary of candles for each symbol subscribed
            The dict must be of following type:
            {interval: [OHLCV, OHLCV, OHLCV, .....]}"""
            self.candles[symbol] = {}

    def add_strategy(self, strategy: Strategy) -> None:
        self.strategies.append(strategy)

    def remove_strategy(self, strategy: Strategy) -> None:
        self.strategies.remove(strategy)

    def add_candle(self, symbol: str, interval: int, market_data: MarketData) -> None:
        if len(self.candles[symbol][interval]["candle"]):
            last_candle = self.candles[symbol][interval]["candle"][-1]
            if last_candle.time == market_data["candle"].time:
                for key in market_data:
                    self.candles[symbol][interval][key][-1] = market_data[key]

            else:
                for key in market_data:
                    self.candles[symbol][interval][key].append(market_data[key])
                    if len(self.candles[symbol][interval][key]) > 100:
                        self.candles[symbol][interval][key].remove(
                            self.candles[symbol][interval][key][0]
                        )
        else:
            for key in market_data:
                self.candles[symbol][interval][key] = [market_data[key]]

    def run_strategies(
        self, symbol: str, data: Dict[int, MarketData]
    ) -> Optional[Order]:

        for interval in data:
            self.add_candle(
                symbol=symbol, interval=interval, market_data=data[interval]
            )

        current_order: Optional[Order] = None
        for strategy in self.strategies:
            current_order, confidence = strategy.analyse(data[5]["candle"])
            if current_order:
                current_order.timestamp = data[5]["candle"].time
            for strategy in self.strategies:
                strategy.order_status = "TRANSIT"
                strategy.current_order = current_order

            return current_order
        return None
