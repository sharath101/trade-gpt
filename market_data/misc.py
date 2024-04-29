from datetime import datetime, timedelta
import os

from api import app
from .candles import CandleManager
from .models import MarketQuoteData
from utils import redis_instance
from database import Symbol
import pickle


async def analyser(data: MarketQuoteData) -> None:
    candle1m = CandleManager(1)
    candle1m.process_tick(data.timestamp, data.price, data.quantity, data.symbol)


def backup_current_day() -> None:
    if not os.path.isdir(
        os.path.join(
            app.config["DATA"], f"backup_{datetime.now().strftime('%Y-%m-%d')}"
        )
    ):
        os.mkdir(
            os.path.join(
                app.config["DATA"], f"backup_{datetime.now().strftime('%Y-%m-%d')}"
            )
        )
    all_symbols = Symbol.get_all()
    all_keys = {}
    for symbol in all_symbols:
        all_keys[symbol.symbol] = []
        key1m = f"candle_{symbol.symbol}_1"
        all_keys[symbol.symbol].append(key1m)
        key2m = f"candle_{symbol.symbol}_2"
        all_keys[symbol.symbol].append(key2m)
        key3m = f"candle_{symbol.symbol}_3"
        all_keys[symbol.symbol].append(key3m)
        key5m = f"candle_{symbol.symbol}_5"
        all_keys[symbol.symbol].append(key5m)
        key10m = f"candle_{symbol.symbol}_10"
        all_keys[symbol.symbol].append(key10m)
        key15m = f"candle_{symbol.symbol}_15"
        all_keys[symbol.symbol].append(key15m)
        key30m = f"candle_{symbol.symbol}_30"
        all_keys[symbol.symbol].append(key30m)

    for symbol in all_symbols:
        backup_data = {}
        for key in all_keys[symbol]:
            backup_data[key] = []
            candle_data: list = redis_instance.get(key)
            if not candle_data:
                continue
            for candle in candle_data:
                if candle["time"] > datetime.now() - timedelta(days=1):
                    backup_data[key].append(candle)

        new_path = os.path.join(
            app.config["DATA"], f"backup_{datetime.now().strftime('%Y-%m-%d')}"
        )
        with open(f"{new_path}/backup_{symbol}.pkl", "wb") as f:
            pickle.dump(backup_data, f)


def delete_old_data() -> None:
    try:
        all_symbols = Symbol.get_all()
        all_keys = []
        for symbol in all_symbols:
            key1m = f"candle_{symbol.symbol}_1"
            all_keys.append(key1m)
            key2m = f"candle_{symbol.symbol}_2"
            all_keys.append(key2m)
            key3m = f"candle_{symbol.symbol}_3"
            all_keys.append(key3m)
            key5m = f"candle_{symbol.symbol}_5"
            all_keys.append(key5m)
            key10m = f"candle_{symbol.symbol}_10"
            all_keys.append(key10m)
            key15m = f"candle_{symbol.symbol}_15"
            all_keys.append(key15m)
            key30m = f"candle_{symbol.symbol}_30"
            all_keys.append(key30m)

        for key in all_keys:
            candle_data: list = redis_instance.get(key)
            if candle_data:
                for candle in candle_data:
                    if candle["time"] <= datetime.now() - timedelta(days=7):
                        candle_data.remove(candle)
                redis_instance.set(key, candle_data)
    except Exception as e:
        print(f"Error deleting old data: {e}")
