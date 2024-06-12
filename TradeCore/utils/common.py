from datetime import timedelta

import pandas as pd
from talipp.ohlcv import OHLCV


def adjust_perc(value: float, percent: float) -> float:
    return value * (1 + percent / 100)


def round_to_nearest_multiple_of_5(x):
    val = round(x / 5) * 5
    if val == 0:
        return 5
    if val == 295:
        return 290
    return val


def binary_search(arr, target):
    low = 0
    high = len(arr)

    while low < high:
        mid = (low + high) // 2
        if arr[mid]["time"] < target:
            low = mid + 1
        else:
            high = mid

    return low


def generate_tickers(interval: int, candle: OHLCV):
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
        raise ValueError(f"Case {case} failed while generating tickers: {e}")

    return final_df
