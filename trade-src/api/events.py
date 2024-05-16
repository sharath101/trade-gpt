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
        start_index = data["start"]
    except:
        start_index = None
    try:
        end_index = data["end"]
    except:
        end_index = None
    if start_index == None and end_index == None:
        redis_data: list = get_all_data()
        new_list = redis_data[-window:]
        s_i = redis_data.index(new_list[0])
        for candle in new_list:
            candle["index"] = s_i
            s_i += 1
        socketio.emit("backtest", {"data": new_list})
        return

    elif start_index == 0 and end_index:

        redis_data: list = get_all_data()
        if len(redis_data) >= end_index:
            new_list = redis_data[:end_index]
            s_i = 0
            for candle in new_list:
                candle["index"] = s_i
                s_i += 1

            socketio.emit("backtest", {"data": new_list})
            return
        else:
            new_list = redis_data
            s_i = 0
            for candle in new_list:
                candle["index"] = s_i
                s_i += 1
            socketio.emit("backtest", {"data": new_list})

    elif start_index and end_index:
        redis_data: list = get_all_data()
        if end_index - start_index > len(redis_data):
            logger.warning("UI is asking more data that we have")
            socketio.emit("backtest", None)
            return
        else:
            new_list = redis_data[start_index:end_index]
            s_i = start_index
            for candle in new_list:
                candle["index"] = s_i
                s_i += 1
            socketio.emit("backtest", {"data": new_list})


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


@socketio.on_error_default
def handle_error_default(e):
    logger.error(f"Error in WebSocket IO: {e}")
