import threading

import requests
from flask import Blueprint, jsonify, render_template, request

from app import Config, logger

from .services import BackTest

api = Blueprint("api", __name__)


@api.route("/")
def index():
    return render_template("index.html")


@api.route("/backtest/run/<stock>", methods=["GET"])
def backtest(stock):
    user_id = "abc"  # get from user service
    strategy_data = {"user_id": user_id, "symbol": stock}
    strategy_service_url = Config.STRATEGY_BASE
    print(f"{strategy_service_url}/strategy/launch")
    try:
        response = requests.post(
            f"{strategy_service_url}/strategy/launch",
            json=strategy_data,
        )
        response.raise_for_status()
        data = response.json()
        logger.info(f'Strategy container created with id: {data['data']['container_id']}')
    except requests.exceptions.RequestException as e:
        return jsonify({"message": "Failed to launch strategy", "error": str(e)}), 500

    file = f"{stock}_with_indicators_.csv"
    thread = threading.Thread(target=start_backtest, args=(file, stock))
    thread.start()

    return jsonify({"message": f"Backtesting Started "})

def start_backtest(file, stock):
    backtester = BackTest(file, stock)
    backtester.backtest()
