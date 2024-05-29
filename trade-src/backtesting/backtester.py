import asyncio
import csv
import os
import threading
import time
from datetime import datetime, timedelta

import pandas as pd
from api import logger
from order_manager import OrderManager
from talipp.ohlcv import OHLCV
from utils import redis_instance, round_to_nearest_multiple_of_5

from .socket_server import SocketServer


class BackTester:
    def __init__(self, file, stock):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_file_rel_path = f"historical_data/{file}"
        csv_file_abs_path = os.path.join(current_dir, csv_file_rel_path)
        self.csv_file_path = csv_file_abs_path
        self.stock = stock
        self.order_manager = OrderManager([self.stock], 20000, True)
        self.num_orders = 0
        self.user = "johndoe"
        self.server_ready_event = threading.Event()
        self.socket_server = SocketServer(
            self.order_manager.place_order, self.server_ready_event, self.backtest
        )

    def socket_server_run(self):
        asyncio.run(self.socket_server.run())

    def connect(self):
        # Spawn thread to run socket server for backtester
        thread = threading.Thread(target=self.socket_server_run)
        thread.start()

        self.server_ready_event.wait()

    def backtest(self):
        logger.info(f"Backtesting {self.stock}")
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
                ticker_data = self.generate_tickers(5, data)
                total_length = len(ticker_data)
                current_candle = OHLCV(
                    time=data.time,
                    open=data.open,
                    high=data.open,
                    low=data.open,
                    close=data.open,
                    volume=0,
                )
                for timestamp, row in ticker_data.iterrows():
                    timestamp = timestamp.to_pydatetime()  # type: ignore
                    current_price = float(row.iloc[0])
                    volume = data.volume / total_length  # type: ignore
                    current_candle.high = (
                        current_candle.high
                        if current_price < current_candle.high
                        else current_price
                    )
                    current_candle.low = (
                        current_candle.low
                        if current_price > current_candle.low
                        else current_price
                    )
                    current_candle.close = current_price
                    current_candle.volume += volume

                    self.order_manager.next(
                        self.stock,
                        current_candle,
                        timestamp,
                        self.socket_server.emitter,
                    )

    def generate_tickers(self, interval: int, candle: OHLCV):
        start_time = candle.time.replace(second=0, microsecond=0)
        end_time = start_time + timedelta(minutes=interval - 1, seconds=55)
        case = 0
        # Code for green candle with no wick
        if (
            candle.close > candle.open
            and candle.high == candle.close
            and candle.low == candle.open
        ):
            case = 1
            data = {"time": [start_time, end_time], "data": [candle.open, candle.close]}

        # Code for green candle with lower wick
        elif (
            candle.close > candle.open
            and candle.high == candle.close
            and candle.low != candle.open
        ):
            case = 2
            total_movement = 2 * (candle.high - candle.low) + candle.open - candle.close
            first_time_delta = round_to_nearest_multiple_of_5(
                300 * (candle.open - candle.low) / total_movement
            )
            first_time = start_time + timedelta(seconds=first_time_delta)
            data = {
                "time": [start_time, first_time, end_time],
                "data": [candle.open, candle.low, candle.close],
            }

        # Code for green candle with upper wick
        elif (
            candle.close > candle.open
            and candle.low == candle.open
            and candle.high != candle.close
        ):
            case = 3
            total_movement = 2 * (candle.high - candle.low) + candle.open - candle.close
            second_time_delta = round_to_nearest_multiple_of_5(
                300 * (candle.high - candle.open) / total_movement
            )
            second_time = start_time + timedelta(seconds=second_time_delta)
            data = {
                "time": [start_time, second_time, end_time],
                "data": [candle.open, candle.high, candle.close],
            }

        # Code for green candle with both wicks
        elif (
            candle.close > candle.open
            and candle.high != candle.close
            and candle.low != candle.open
        ):
            case = 4
            total_movement = 2 * (candle.high - candle.low) + candle.open - candle.close
            first_time_delta = round_to_nearest_multiple_of_5(
                300 * (candle.open - candle.low) / total_movement
            )
            second_time_delta = round_to_nearest_multiple_of_5(
                300 * (candle.high - candle.low) / total_movement
            )
            first_time = start_time + timedelta(seconds=first_time_delta)
            second_time = first_time + timedelta(seconds=second_time_delta)
            data = {
                "time": [start_time, first_time, second_time, end_time],
                "data": [candle.open, candle.low, candle.high, candle.close],
            }

        # Code for red candle with no wick
        elif (
            candle.open > candle.close
            and candle.high == candle.open
            and candle.low == candle.close
        ):
            case = 5
            data = {"time": [start_time, end_time], "data": [candle.open, candle.close]}

        # Code for red candle with lower wick
        elif (
            candle.open > candle.close
            and candle.high == candle.open
            and candle.low != candle.close
        ):
            case = 6
            total_movement = 2 * (candle.high - candle.low) + candle.close - candle.open
            second_time_delta = round_to_nearest_multiple_of_5(
                300 * (candle.open - candle.low) / total_movement
            )
            second_time = start_time + timedelta(seconds=second_time_delta)
            data = {
                "time": [start_time, second_time, end_time],
                "data": [candle.open, candle.low, candle.close],
            }

        # Code for red candle with upper wick
        elif (
            candle.open > candle.close
            and candle.low == candle.close
            and candle.high != candle.open
        ):
            case = 7
            total_movement = 2 * (candle.high - candle.low) + candle.close - candle.open
            first_time_delta = round_to_nearest_multiple_of_5(
                300 * (candle.high - candle.open) / total_movement
            )
            first_time = start_time + timedelta(seconds=first_time_delta)
            data = {
                "time": [start_time, first_time, end_time],
                "data": [candle.open, candle.high, candle.close],
            }

        # Code for red candle with both wicks
        elif (
            candle.open > candle.close
            and candle.high != candle.open
            and candle.low != candle.close
        ):
            case = 8
            total_movement = 2 * (candle.high - candle.low) + candle.close - candle.open
            first_time_delta = round_to_nearest_multiple_of_5(
                300 * (candle.high - candle.open) / total_movement
            )
            second_time_delta = round_to_nearest_multiple_of_5(
                300 * (candle.open - candle.low) / total_movement
            )
            first_time = start_time + timedelta(seconds=first_time_delta)
            second_time = first_time + timedelta(seconds=second_time_delta)
            data = {
                "time": [start_time, first_time, second_time, end_time],
                "data": [candle.open, candle.low, candle.high, candle.close],
            }

        # Code for zero candle with both wicks
        elif (
            candle.open == candle.close
            and candle.high != candle.low
            and candle.high != candle.open
            and candle.low != candle.close
        ):
            case = 9
            total_movement = 2 * (candle.high - candle.low)
            first_time_delta = round_to_nearest_multiple_of_5(
                300 * (candle.open - candle.low) / total_movement
            )
            second_time_delta = round_to_nearest_multiple_of_5(
                300 * (candle.high - candle.low) / total_movement
            )
            first_time = start_time + timedelta(seconds=first_time_delta)
            second_time = first_time + timedelta(seconds=second_time_delta)
            data = {
                "time": [start_time, first_time, second_time, end_time],
                "data": [candle.open, candle.low, candle.high, candle.close],
            }

        # Code for only high different
        elif candle.open == candle.close and candle.open == candle.low:
            case = 10
            first_time = start_time + timedelta(seconds=150)
            data = {
                "time": [start_time, first_time, end_time],
                "data": [candle.open, candle.high, candle.close],
            }

        # Code for only low different
        elif candle.open == candle.close and candle.open == candle.high:
            case = 11
            first_time = start_time + timedelta(seconds=150)
            data = {
                "time": [start_time, first_time, end_time],
                "data": [candle.open, candle.low, candle.close],
            }

        # Code for no price movement
        else:
            case = 12
            data = {"time": [start_time, end_time], "data": [candle.open, candle.open]}

        if data["time"][-2] == end_time:
            data["time"][-2] = end_time - timedelta(seconds=5)
        if data["time"][1] == start_time:
            data["time"][1] = start_time + timedelta(seconds=5)

        try:
            df = pd.DataFrame(data)
            df.set_index("time", inplace=True)
            interpolated_df = df.resample("5s").interpolate(method="linear")
            final_series = interpolated_df["data"].round(2)
            final_df = pd.DataFrame(final_series)
        except Exception as e:
            logger.info(f"Case {case} failed while generating tickers: {e}")

        return final_df
