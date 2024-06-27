import csv
import os
import pickle
from datetime import datetime
from typing import List

from app import socketio, strategy_events
from config import Config
from dataclass import Order
from order_manager import OrderManager
from talipp.ohlcv import OHLCV
from utils.common import generate_tickers


class BackTest:
    def __init__(self, file, stock):
        self.socketio = socketio
        app_dir = Config.Backtestify.APP_DIR
        csv_file_rel_path = f"historical_data/{file}"
        self.csv_file_path = os.path.join(app_dir, csv_file_rel_path)
        self.stock = stock
        self.order_manager = OrderManager(self.stock, [5], True)
        self.candle_data: List[OHLCV] = []
        self.len_candle_data: int = len(self.candle_data)
        self.candle_data_pointer: int = 0
        self.ticker_data: List[tuple] = []
        self.len_ticker_data: int = len(self.ticker_data)
        self.ticker_data_pointer: int = 0
        self.current_candle: OHLCV = OHLCV(None, None, None, None, None, None)

        with open(self.csv_file_path, mode="r", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                data = OHLCV(
                    time=datetime.strptime(row["date"], "%Y-%m-%d %H:%M:%S%z"),
                    open=float(row["open"]),
                    high=float(row["high"]),
                    low=float(row["low"]),
                    close=float(row["close"]),
                    volume=float(row["volume"]),
                )
                self.candle_data.append(data)
        self.len_candle_data = len(self.candle_data)

    def backtest(self, channel):
        if self.ticker_data_pointer == 0:
            data = generate_tickers(5, self.candle_data[self.candle_data_pointer])
            self.ticker_data = []
            for timestamp, row in data.iterrows():
                self.ticker_data.append((timestamp.to_pydatetime(), float(row.iloc[0])))  # type: ignore
            self.len_ticker_data = len(self.ticker_data)
            self.candle_data_pointer += 1

        timestamp, current_price = self.ticker_data[self.ticker_data_pointer]
        volume = (
            self.candle_data[self.candle_data_pointer - 1].volume / self.len_ticker_data  # type: ignore
        )
        self.order_manager.next(
            self.stock,
            current_price,
            timestamp,
            volume,
            strategy_events.emit,
            channel,
        )
        self.ticker_data_pointer += 1
        self.ticker_data_pointer = self.ticker_data_pointer % self.len_ticker_data

    def register_channel(self, channel: str):

        @self.socketio.on(channel)
        def handle_order(data):
            order: Order = pickle.loads(data)["order"]
            if order:
                self.order_manager.place_order(ordered=order)
            self.backtest(channel)
