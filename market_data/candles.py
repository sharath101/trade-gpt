from datetime import datetime, timedelta
from talipp.ohlcv import OHLCV
from .indicators import IndicatorManager
from utils import redis_instance


class CandleManager:
    def __init__(self, interval_minutes: int):
        self.interval_minutes = interval_minutes
        self.indicators = IndicatorManager()

    def process_tick(self, timestamp: datetime, price: float, volume: int, symbol: str):
        current_time = timestamp

        last_timestamp = current_time - timedelta(
            minutes=current_time.minute % self.interval_minutes,
            seconds=current_time.second,
        )

        current_candle_key = f"candle_{symbol}_{self.interval_minutes}_current"
        ta_key = f"ta_{symbol}_{self.interval_minutes}"

        indicator = redis_instance.get(ta_key)
        if indicator:
            self.indicators = indicator

        current_candle_data = redis_instance.get(current_candle_key)
        if current_candle_data:
            current_candle = current_candle_data
            if current_candle["time"] != last_timestamp.strftime("%Y-%m-%d %H:%M:%S"):
                self._close_candle(current_candle, symbol)
                current_candle = self._open_candle(
                    last_timestamp, price, volume, symbol
                )
        else:
            current_candle = self._open_candle(last_timestamp, price, volume, symbol)

        current_candle_data = {
            "time": last_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "open": current_candle["open"] if current_candle_data else price,
            "high": (
                max(price, current_candle["high"]) if current_candle_data else price
            ),
            "low": min(price, current_candle["low"]) if current_candle_data else price,
            "close": price,
            "volume": (
                current_candle["volume"] + volume if current_candle_data else volume
            ),
        }
        olhcv_data = OHLCV(
            current_candle_data["open"],
            current_candle_data["high"],
            current_candle_data["low"],
            current_candle_data["close"],
            current_candle_data["volume"],
            current_candle_data["time"],
        )

        self.indicators.update(olhcv_data)
        indicators_dict = self.indicators.get_all()
        current_candle_data.update(indicators_dict)

        redis_instance.set(ta_key, self.indicators)
        redis_instance.set(current_candle_key, current_candle_data)

    def _open_candle(self, timestamp, price, volume, symbol):
        ta_key = f"ta_{symbol}_{self.interval_minutes}"
        indicator = redis_instance.get(ta_key)
        if indicator:
            self.indicators = indicator
        current_candle_data = {
            "time": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
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
