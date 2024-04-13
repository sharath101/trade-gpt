from datetime import datetime, timedelta
from market_data import redis_instance
from talipp.indicators import SMA


def convert_dict(input_dict):
    for key, value in input_dict.items():
        # Convert integer or float represented as string to actual int or float
        if isinstance(value, str) and value.isdigit():
            input_dict[key] = int(value)
        elif isinstance(value, str) and value.replace(".", "", 1).isdigit():
            input_dict[key] = float(value)
        # Recursively convert nested dictionaries
        elif isinstance(value, dict):
            input_dict[key] = convert_dict(value)
        # Convert string representation of list to actual list
        elif isinstance(value, str) and value.startswith("[") and value.endswith("]"):
            input_dict[key] = eval(value)
    return input_dict


class CandleManager:
    def __init__(self, interval_minutes: int):
        self.interval_minutes = interval_minutes
        self.sma = SMA(5)

    def process_tick(self, timestamp: datetime, price: float, volume: int, symbol: str):
        current_time = timestamp

        last_timestamp = current_time - timedelta(
            minutes=current_time.minute % self.interval_minutes,
            seconds=current_time.second,
        )

        current_candle_key = f"candle_{symbol}_{self.interval_minutes}_current"
        last_candle_key = f"candle_{symbol}_{self.interval_minutes}_last"

        last_candle_data = redis_instance.get(last_candle_key)
        if last_candle_data:
            last_candle = eval(last_candle_data)
            last_candle = convert_dict(last_candle)
            last_candle_timestamp = last_candle["timestamp"]
            if last_candle_timestamp < last_timestamp:
                self._close_candle(last_candle, symbol)

        current_candle_data = redis_instance.get(current_candle_key)
        if current_candle_data:
            current_candle = eval(current_candle_data)
            current_candle = convert_dict(current_candle)
            if current_candle["timestamp"] != last_timestamp.strftime(
                "%Y-%m-%d %H:%M:%S"
            ):
                self._close_candle(current_candle, symbol)
                self._open_candle(last_timestamp, price, volume, symbol)
        else:
            self._open_candle(last_timestamp, price, volume, symbol)

        current_candle_data = {
            "timestamp": last_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "open": price,
            "high": (
                max(price, current_candle["high"]) if current_candle_data else price
            ),
            "low": min(price, current_candle["low"]) if current_candle_data else price,
            "close": price,
            "volume": (
                current_candle["volume"] + volume if current_candle_data else volume
            ),
        }

        redis_instance.set(current_candle_key, str(current_candle_data))

    def _open_candle(self, timestamp, price, volume, symbol):
        current_candle_data = {
            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "open": price,
            "high": price,
            "low": price,
            "close": price,
            "volume": volume,
        }
        current_candle_key = f"candle_{symbol}_{self.interval_minutes}_current"
        redis_instance.set(current_candle_key, str(current_candle_data))

    def _close_candle(self, candle, symbol):
        candles_key = f"candle_{symbol}_{self.interval_minutes}"
        candles_data = redis_instance.get(candles_key)
        candles = eval(candles_data) if candles_data else []
        candles.append(candle)
        redis_instance.set(candles_key, str(candles))

    def get_candles(self, symbol):
        candles_key = f"candle_{symbol}_{self.interval_minutes}"
        candles_data = redis_instance.get(candles_key)
        return eval(candles_data) if candles_data else []

    def get_latest_candle(self, symbol):
        current_candle_key = f"candle_{symbol}_{self.interval_minutes}_current"
        current_candle_data = redis_instance.get(current_candle_key)
        return eval(current_candle_data) if current_candle_data else None
