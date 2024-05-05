from typing import List
from datetime import datetime

from dataclass import Order
from utils import BacktestCandleManager
from baseclasses import Strategy
from api import logger


class StrategyManager:
    symbol: str
    backtesting: bool = False
    stategies: List[Strategy] = []
    candle_manager = BacktestCandleManager(5)

    def __init__(
        self,
        symbol: str,
        balance: float,
        strategies: List[Strategy],
        backtesing: bool,
    ):
        self.symbol = symbol
        self.backtesting = backtesing
        self.strategies = strategies
        self.balance = balance
        if self.backtesting:
            for strategy in self.strategies:
                strategy.backtesting = True
                strategy.symbol = symbol

    def add_strategy(self, strategy: Strategy) -> None:
        self.strategies.append(strategy)

    def remove_strategy(self, strategy: Strategy) -> None:
        self.strategies.remove(strategy)

    def run_strategies(
        self, symbol: str, current_price: float, timestamp: datetime, volume: int
    ) -> Order:
        if self.backtesting:
            self.candle_manager.process_tick(timestamp, current_price, volume, symbol)
        current_order = None
        current_confidence = 0
        for strategy in self.strategies:
            try:
                order, confidence = strategy.analyse(current_price)
                if order:
                    order.symbol = self.symbol
                    # logger.info(
                    #     f"Strategy {strategy.__class__.__name__} generated order: {order}, with confidence: {confidence}"
                    # )
                    if confidence >= current_confidence:
                        current_order = order
                        current_confidence = confidence

            except Exception as e:
                logger.error(
                    f"Error running strategy {strategy.__class__.__name__}: {e}"
                )
        if current_confidence > 0.1:
            for strategy in self.strategies:
                strategy.order_status = "TRANSIT"
                strategy.current_order = current_order
            return current_order
        return None

    def traded(self) -> None:
        for strategy in self.strategies:
            strategy.order_status = "TRADED"

    def cancelled(self) -> None:
        for strategy in self.strategies:
            strategy.order_status = "CANCELLED"

    def closed(self) -> None:
        for strategy in self.strategies:
            strategy.order_status = "CLOSED"

    def rejected(self) -> None:
        for strategy in self.strategies:
            strategy.order_status = "REJECTED"

    def closing(self) -> None:
        for strategy in self.strategies:
            strategy.order_status = "CLOSING"

    def opening(self) -> None:
        for strategy in self.strategies:
            strategy.order_status = "OPENING"

    def open(self) -> None:
        for strategy in self.strategies:
            strategy.order_status = "OPEN"
