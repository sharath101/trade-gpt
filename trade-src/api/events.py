import time

from flask import request

from api import app, logger, socketio
from utils import redis_instance


@socketio.on("connect")
def handle_connect(data):
    """Handle authentication here, link SID with user.id and store in DB"""
    return True


@socketio.on("backtest")
def handle_backtest_all(data):
    window = 1000
    try:
        start = data["start"]
    except:
        start = -1
    try:
        end = data["end"]
    except:
        end = -1
    print("----------")
    print(f"start: {start}")
    print(f"end: {end}")
    redis_data: list = get_all_data()
    if redis_data and len(redis_data) > 0:
        start_index = binary_search(redis_data, start)
        end_index = binary_search(redis_data, end)
        print(len(redis_data))
        print(redis_data[-1])
        print(f"start_id: {start_index}")
        print(f"end_id: {end_index}")
        if start_index > len(redis_data):
            new_list = []
        elif start_index != -1 and end_index != -1:
            if end_index - start_index > window:
                new_list = redis_data[start_index : start_index + window]
            else:
                new_list = redis_data[start_index : end_index + 1]

        elif start_index and end_index == -1:
            new_list = redis_data[start_index:]
            if len(new_list) > window:
                new_list = redis_data[start_index : start_index + window]
            else:
                new_list = redis_data[start_index:]

        elif start_index == -1 and end_index:
            new_list = redis_data[:end_index]
            if len(new_list) > window:
                new_list = redis_data[end_index - window : end_index]
            else:
                new_list = redis_data[:end_index]

        elif start_index == -1 and end_index == -1:
            new_list = redis_data
            if len(new_list) > window:
                new_list = redis_data[-window:-1]
            else:
                new_list = redis_data
        print(f"Length of array returned: {len(new_list)}")
        socketio.emit("backtest", {"data": new_list})
    else:
        socketio.emit("backtest", None)


def get_all_data():
    # backup: list = redis_instance.get("backtest_backup")
    backtest: list = redis_instance.get("backtest")

    # if backup:
    #     pass
    # else:
    #     backup = []

    if backtest:
        pass
    else:
        backtest = []

    return backtest


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


@socketio.on_error_default
def handle_error_default(e):
    logger.error(f"Error in WebSocket IO: {e}")
