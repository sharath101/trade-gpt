import csv
import os
from datetime import datetime

from talipp.ohlcv import OHLCV

from strategy import EngulfingStrategy


class BackTester:
    def __init__(self, file):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_file_rel_path = f"historical_data/{file}"
        csv_file_abs_path = os.path.join(current_dir, csv_file_rel_path)
        self.csv_file_path = csv_file_abs_path
        self.strategy = EngulfingStrategy("HDFCBANK", 5, 20000, True)

    def backtest(self):
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
                self.strategy.analyse(data)
