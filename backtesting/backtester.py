import csv

from strategy import EngulfingStrategy


class BackTester:
    def __init__(self, csv_file_path):
        self.csv_file_path = csv_file_path
        self.strategy = EngulfingStrategy(True)

    def backtest(self):
        with open(self.csv_file_path, mode="r", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                data = {
                    "time": row["date"],
                    "open": row["open"],
                    "high": row["high"],
                    "low": row["low"],
                    "close": row["close"],
                    "volume": row["volume"],
                }
                self.strategy.analyse(data)
