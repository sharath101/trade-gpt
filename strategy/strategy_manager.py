from typing import List

from talipp.ohlcv import OHLCV

from api import logger
from order_manager.models import Order
from utils import redis_instance

from .strategy import Strategy


class StrategyManager:
    symbol: str
    candle_range: int
    backtesting: bool = False
    stategies: List[Strategy] = []

    def __init__(
        self,
        symbol: str,
        candle_range: int,
        strategies: List[Strategy],
        backtesing: bool,
    ):
        self.symbol = symbol
        self.candle_range = candle_range
        self.backtesting = backtesing
        self.strategies = strategies

    def add_strategy(self, strategy: Strategy) -> None:
        self.strategies.append(strategy)

    def remove_strategy(self, strategy: Strategy) -> None:
        self.strategies.remove(strategy)

    def fetch_current_candle(self, candle) -> OHLCV:
        try:
            candle_key = f"candle_{self.symbol}_{self.candle_range}_current"
            data = redis_instance.get(candle_key)
        except Exception as e:
            logger.error(f"Error fetching current candle: {e}")
            return None
        try:
            candle = OHLCV(
                data["open"],
                data["high"],
                data["low"],
                data["close"],
                data["volume"],
                data["time"],
            )
        except Exception as e:
            logger.error(f"Error creating OHLCV object: {e}")
            return None
        return candle

    def run_strategies(self, candle: OHLCV = None) -> Order:
        if not self.backtesting:
            candle = self.fetch_current_candle()
        if candle is None:
            logger.error("No candle data found to run strategies. Exiting.")
            return None
        current_order = None
        current_confidence = 0
        for strategy in self.strategies:
            order, confidence = strategy.analyse(candle)
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
                strategy.order_status = "PENDING"
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
