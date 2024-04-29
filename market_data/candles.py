from datetime import datetime, timedelta
from talipp.ohlcv import OHLCV
from .indicators import IndicatorManager
from utils import redis_instance


class CandleManager:
    def __init__(self, interval_minutes: int):
        self.interval_minutes: int = interval_minutes
        self.indicators: IndicatorManager = IndicatorManager()
        self._market_open: datetime = datetime.now().replace(
            hour=9, minute=15, second=0, microsecond=0
        )
        self._market_close: datetime = datetime.now().replace(
            hour=15, minute=30, second=0, microsecond=0
        )

    def is_market_open(self, timestamp: datetime):
        self._market_open: datetime = datetime.now().replace(
            hour=9, minute=15, second=0, microsecond=0
        )
        self._market_close: datetime = datetime.now().replace(
            hour=15, minute=30, second=0, microsecond=0
        )
        return self._market_open <= timestamp <= self._market_close

    def process_tick(self, timestamp: datetime, price: float, volume: int, symbol: str):

        last_timestamp = timestamp - timedelta(
            minutes=timestamp.minute % self.interval_minutes,
            seconds=timestamp.second,
            microseconds=timestamp.microsecond,
        )

        current_candle_key = f"candle_{symbol}_{self.interval_minutes}_current"
        ta_key = f"ta_{symbol}_{self.interval_minutes}"

        indicator = redis_instance.get(ta_key)
        if indicator:
            self.indicators = indicator

        current_candle = redis_instance.get(current_candle_key)
        if current_candle:
            if current_candle["time"] != last_timestamp:
                self._close_candle(current_candle, symbol)
                current_candle = self._open_candle(
                    last_timestamp, price, volume, symbol
                )
        else:
            current_candle = self._open_candle(last_timestamp, price, volume, symbol)

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

            redis_instance.set(ta_key, self.indicators)
            redis_instance.set(current_candle_key, current_candle)

    def _open_candle(self, timestamp: datetime, price: float, volume: int, symbol: str):
        if not self.is_market_open(timestamp):
            return None
        ta_key = f"ta_{symbol}_{self.interval_minutes}"
        indicator = redis_instance.get(ta_key)
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

        redis_instance.set(ta_key, self.indicators)
        redis_instance.set(current_candle_key, current_candle_data)
        return current_candle_data

    def _close_candle(self, candle, symbol):
        candles_key = f"candle_{symbol}_{self.interval_minutes}"
        candles_data = redis_instance.get(candles_key)
        candles = candles_data if candles_data else []
        candles.append(candle)
        redis_instance.set(candles_key, candles)

    def get_candles(self, symbol):
        candles_key = f"candle_{symbol}_{self.interval_minutes}"
        candles_data = redis_instance.get(candles_key)
        return candles_data if candles_data else []

    def get_latest_candle(self, symbol):
        current_candle_key = f"candle_{symbol}_{self.interval_minutes}_current"
        current_candle_data = redis_instance.get(current_candle_key)
        return current_candle_data if current_candle_data else None
