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
        start = 0
    try:
        end = data["end"]
    except:
        end = 0

    redis_data: list = get_all_data()

    if redis_data and len(redis_data) > 0:
        start_index = binary_search(redis_data, start)
        end_index = binary_search(redis_data, end)
        if start_index > end_index:
            socketio.emit("backtest", None)
            return

        if start_index == 0 and end_index == 0:
            new_list = redis_data
            if len(new_list) > window:
                new_list = redis_data[-1000:-1]
            else:
                new_list = redis_data

        elif start_index and end_index:
            new_list = redis_data[start_index : end_index + 1]

        elif start_index and not end_index:
            new_list = redis_data[start_index:]
            if len(new_list) > window:
                new_list = redis_data[start_index : start_index + window]
            else:
                new_list = redis_data[start_index:]

        elif not start_index and end_index:
            new_list = redis_data[:end_index]
            if len(new_list) > window:
                new_list = redis_data[end_index - window : end_index]
            else:
                new_list = redis_data[:end_index]
        socketio.emit("backtest", {"data": new_list})
    else:
        socketio.emit("backtest", None)


@socketio.on("backtest_next")
def handle_backtest_next(data):
    try:
        last_timestamp = data["last"]
    except:
        return
    try:
        quantity = data["num"]
    except:
        quantity = 1
    if last_timestamp:
        redis_data: list = get_all_data()
        start_index = binary_search(redis_data, last_timestamp)
        if start_index == len(redis_data):
            socketio.emit("backtest", None)
        elif start_index < len(redis_data) and len(redis_data) - start_index > quantity:
            new_list = redis_data[start_index : start_index + quantity]
            socketio.emit("backtest", {"data": new_list})
        else:
            socketio.emit("backtest", None)


def get_all_data():
    backup: list = redis_instance.get("backtest_backup")
    backtest: list = redis_instance.get("backtest")

    if backup:
        pass
    else:
        backup = []

    if backtest:
        pass
    else:
        backtest = []

    return backup + backtest


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


# @socketio.on_error_default
# def handle_error_default(e):
#     logger.error(f"Error in WebSocket IO: {e}")
