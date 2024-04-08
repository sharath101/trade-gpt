import time
from datetime import datetime, timedelta

import pandas as pd

from redis_manager import redis_instance


class CandleManager:
    def __init__(self, interval_minutes):
        self.interval_minutes = interval_minutes
        self.symbols = {}
        self.sum = 0
        self.total_ticks = 0

    def create_symbol(self, symbol):
        self.symbols[symbol] = {
            "candles": [],
            "current_candle": None,
            "last_timestamp": None,
        }

    def process_tick(self, timestamp, price, symbol, save_redis=1):
        self.total_ticks += 1
        if symbol not in self.symbols:
            self.create_symbol(symbol)
        symb = self.symbols[symbol]
        current_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        if symb["last_timestamp"] is None:
            symb["last_timestamp"] = current_time - timedelta(
                minutes=current_time.minute % self.interval_minutes,
                seconds=current_time.second,
            )
        if symb["current_candle"] is None:
            self._open_candle(symb["last_timestamp"], price, symbol)

        while (
            symb["last_timestamp"] + timedelta(minutes=self.interval_minutes)
            <= current_time
        ):
            self._close_candle(symbol)
            symb["last_timestamp"] += timedelta(minutes=self.interval_minutes)
            self._open_candle(symb["last_timestamp"], price, symbol)
        symb["current_candle"]["high"] = max(symb["current_candle"]["high"], price)
        symb["current_candle"]["low"] = min(symb["current_candle"]["low"], price)
        symb["current_candle"]["close"] = price
        if save_redis:
            redis_instance.set(
                f"candle_{symbol}_{self.interval_minutes}", symb["candles"]
            )

    def _open_candle(self, timestamp, price, symbol):
        symb = self.symbols[symbol]
        symb["current_candle"] = {
            "timestamp": timestamp,
            "open": price,
            "high": price,
            "low": price,
            "close": price,
        }

    def _close_candle(self, symbol):
        symb = self.symbols[symbol]
        symb["candles"].append(
            {
                "timestamp": symb["current_candle"]["timestamp"],
                "open": symb["current_candle"]["open"],
                "high": symb["current_candle"]["high"],
                "low": symb["current_candle"]["low"],
                "close": symb["current_candle"]["close"],
            }
        )

    def get_candles(self, symbol):
        return self.symbols[symbol]["candles"]

    def get_latest_candle(self, symbol):
        return self.symbols[symbol]["current_candle"]


candle_1m = CandleManager(1)
candle_5m = CandleManager(5)
candle_10m = CandleManager(10)
candle_15m = CandleManager(15)
candle_30m = CandleManager(30)
candle_1h = CandleManager(60)
candle_2h = CandleManager(120)
candle_5h = CandleManager(300)
candle_10h = CandleManager(600)
candle_1d = CandleManager(1440)
