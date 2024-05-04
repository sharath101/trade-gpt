from typing import List
from datetime import datetime
import logging as logger

from dataclass import Order
from utils import BacktestCandleManager, redis_instance, redis_instance_backtest
from baseclasses import Strategy


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

    def add_strategy(self, strategy: Strategy) -> None:
        self.strategies.append(strategy)

    def remove_strategy(self, strategy: Strategy) -> None:
        self.strategies.remove(strategy)

    def fetch_current_candle(self, candle_range: int) -> dict:
        try:
            candle_key = f"candle_{self.symbol}_{candle_range}_current"
            if not self.backtesting:
                data = redis_instance.get(candle_key)
            else:
                data = redis_instance_backtest.get(candle_key)
        except Exception as e:
            logger.error(f"Error fetching current candle: {e}")
            return {}
        return data

    def fetch_candles(self, candle_range: int) -> List[dict]:
        try:
            candles_key = f"candle_{self.symbol}_{candle_range}"
            if not self.backtesting:
                data = redis_instance.get(candles_key)
            else:
                data = redis_instance_backtest.get(candles_key)
        except Exception as e:
            logger.error(f"Error fetching candles: {e}")
            return []
        return data

    def run_strategies(
        self, symbol: str, current_price: float, timestamp: datetime, volume: int
    ) -> Order:
        if self.backtesting:
            self.candle_manager.process_tick(timestamp, current_price, volume, symbol)
        current_order = None
        current_confidence = 0
        for strategy in self.strategies:
            order, confidence = strategy.analyse(current_price)
            if order:
                order.symbol = self.symbol
                logger.info(
                    f"Strategy {strategy.__class__.__name__} generated order: {order}, with confidence: {confidence}"
                )
                if confidence >= current_confidence:
                    current_order = order
                    current_confidence = confidence
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
