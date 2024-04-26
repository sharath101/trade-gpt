import os

from backtester import BackTester

current_dir = os.path.dirname(os.path.abspath(__file__))
csv_file_rel_path = "historical_data/HDFC_with_indicators_.csv"
csv_file_abs_path = os.path.join(current_dir, csv_file_rel_path)

backtester = BackTester(csv_file_abs_path)
backtester.backtest()
