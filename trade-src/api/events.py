from api import app, logger, socketio
from flask import request
from utils import redis_instance


@socketio.on("connect")
def handle_connect(data):
    """Handle authentication here, link SID with user.id and store in DB"""
    return True


@socketio.on("backtest_all")
def handle_backtest_all(data):
    redis_data: list = redis_instance.get("backtest")
    if redis_data:
        socketio.emit("backtest_all", {"all": redis_data[:-3]})
    else:
        socketio.emit("backtest_all", {"all": list([])})


@socketio.on("backtest_next")
def handle_backtest_next(data):
    last_timestamp = int(data["time"])
    if last_timestamp == 0:
        handle_backtest_all(data)
        return
    redis_data: list = redis_instance.get("backtest")
    if redis_data and len(redis_data):
        last_sent = binary_search(redis_data, last_timestamp)
        if redis_data[last_sent] != redis_data[-1]:
            socketio.emit("backtest_next", redis_data[last_sent + 1 :])
        else:
            socketio.emit("backtest_next", None)


def binary_search(arr, target):
    low = 0
    high = len(arr) - 1

    while low <= high:
        mid = (low + high) // 2
        if arr[mid]["time"] == target:
            return mid
        elif arr[mid]["time"] < target:
            low = mid + 1
        else:
            high = mid - 1

    return -1


@socketio.on_error_default
def handle_error_default(e):
    logger.error(f"Error in WebSocket IO: {e}")
