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
    start_index = data.get("start")
    end_index = data.get("end")
    redis_data: list = get_all_backtest_candles()

    if start_index == None and end_index == None:
        candle_list = redis_data[-window:]
        s_i = redis_data.index(candle_list[0])

    elif start_index == 0 and end_index:
        candle_list = redis_data[: min(end_index, len(redis_data))]
        s_i = 0

    elif start_index and end_index:
        if end_index - start_index > len(redis_data):
            logger.warning("UI is asking more data that we have")
            socketio.emit("backtest", None)
            return
        else:
            candle_list = redis_data[start_index:end_index]
            s_i = start_index
    else:
        socketio.emit("backtest", None)
        return

    for candle in candle_list:
        candle["index"] = s_i
        s_i += 1
    socketio.emit("backtest", {"data": candle_list})


def get_all_backtest_candles():
    backup: list = redis_instance.get("backtest_backup") or []
    backtest: list = redis_instance.get("backtest") or []
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


@socketio.on_error_default
def handle_error_default(e):
    logger.error(f"Error in WebSocket IO: {e}")
