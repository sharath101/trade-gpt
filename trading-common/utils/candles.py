from datetime import datetime, time, timedelta

from talipp.ohlcv import OHLCV

from api import logger
from utils import redis_instance, redis_instance_backtest

from .indicators import IndicatorManager


class CandleManager:
    def __init__(
        self, interval_minutes: int, backtesting=False, indicators={"MACD": [12, 26, 9]}
    ):
        self.interval_minutes: int = interval_minutes
        self.indicators: IndicatorManager = IndicatorManager(indicators)
        self._market_open: time = time(9, 15, 0)
        self._market_close: time = time(15, 30, 0)
        if backtesting:
            self.redis_instance = redis_instance_backtest
        else:
            self.redis_instance = redis_instance

    def is_market_open(self, timestamp: datetime) -> bool:
        return self._market_open <= timestamp.time() <= self._market_close

    def process_tick(
        self, timestamp: datetime, price: float, volume: int, symbol: str
    ) -> None:
        try:

            last_timestamp = timestamp - timedelta(
                minutes=timestamp.minute % self.interval_minutes,
                seconds=timestamp.second,
                microseconds=timestamp.microsecond,
            )

            current_candle_key = f"candle_{symbol}_{self.interval_minutes}_current"
            ta_key = f"ta_{symbol}_{self.interval_minutes}"

            indicator = self.redis_instance.get(ta_key)
            if indicator:
                self.indicators = indicator

            current_candle = self.redis_instance.get(current_candle_key)
            if current_candle:
                if current_candle["time"] != last_timestamp:
                    self._close_candle(current_candle, symbol)
                    current_candle = self._open_candle(
                        last_timestamp, price, volume, symbol
                    )
            else:
                current_candle = self._open_candle(
                    last_timestamp, price, volume, symbol
                )

            if current_candle:
                current_candle = {
                    "time": last_timestamp,
                    "open": current_candle["open"],
                    "high": max(price, current_candle["high"]),
                    "low": min(price, current_candle["low"]),
                    "close": price,
                    "volume": current_candle["volume"] + volume,
                }
                olhcv_data = OHLCV(
                    current_candle["open"],
                    current_candle["high"],
                    current_candle["low"],
                    current_candle["close"],
                    current_candle["volume"],
                    current_candle["time"],
                )

                self.indicators.update(olhcv_data)
                indicators_dict = self.indicators.get_all()
                current_candle.update(indicators_dict)

                self.redis_instance.set(ta_key, self.indicators)
                self.redis_instance.set(current_candle_key, current_candle)
        except Exception as e:
            logger.error(f"Error processing tick: {e}")

    def _open_candle(
        self, timestamp: datetime, price: float, volume: int, symbol: str
    ) -> dict:
        try:
            if not self.is_market_open(timestamp):
                return None
            ta_key = f"ta_{symbol}_{self.interval_minutes}"
            indicator = self.redis_instance.get(ta_key)
            if indicator:
                self.indicators = indicator
            current_candle_data = {
                "time": timestamp,
                "open": price,
                "high": price,
                "low": price,
                "close": price,
                "volume": volume,
            }
            olhcv_data = OHLCV(
                current_candle_data["open"],
                current_candle_data["high"],
                current_candle_data["low"],
                current_candle_data["close"],
                current_candle_data["volume"],
                current_candle_data["time"],
            )

            self.indicators.add(olhcv_data)
            indicators_dict = self.indicators.get_all()
            current_candle_data.update(indicators_dict)

            current_candle_key = f"candle_{symbol}_{self.interval_minutes}_current"

            self.redis_instance.set(ta_key, self.indicators)
            self.redis_instance.set(current_candle_key, current_candle_data)
            return current_candle_data
        except Exception as e:
            logger.error(f"Error opening candle: {e}")

    def _close_candle(self, candle, symbol) -> None:
        try:
            candles_key = f"candle_{symbol}_{self.interval_minutes}"
            candles_data = self.redis_instance.get(candles_key)
            candles = candles_data if candles_data else []
            candles.append(candle)
            self.redis_instance.set(candles_key, candles)
        except Exception as e:
            logger.error(f"Error closing candle: {e}")

    def get_candles(self, symbol) -> list:
        try:
            candles_key = f"candle_{symbol}_{self.interval_minutes}"
            candles_data = self.redis_instance.get(candles_key)
            return candles_data if candles_data else []
        except Exception as e:
            logger.error(f"Error getting candles: {e}")
            return []

    def get_latest_candle(self, symbol) -> dict:
        try:
            current_candle_key = f"candle_{symbol}_{self.interval_minutes}_current"
            current_candle_data = self.redis_instance.get(current_candle_key)
            return current_candle_data if current_candle_data else None
        except Exception as e:
            logger.error(f"Error getting latest candle: {e}")
            return None
