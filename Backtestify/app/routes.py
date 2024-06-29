from secrets import token_hex

import requests
from app import logger
from config import Config
from database import Users
from flask import Blueprint, jsonify, render_template
from utils import handle_request

from .backtest import BackTest

api = Blueprint("api", __name__)


@api.route("/")
def index():
    return render_template("index.html")


@api.route("/backtest/run/<stock>", methods=["GET"])
@handle_request
def backtest(stock, user: Users):
    user_id = user.id
    channel: str = token_hex(10)
    strategy_data = {"user_id": user_id, "symbol": stock, "channel": channel}
    strategy_service_url = Config.StrategEase.HOST
    file = f"{stock}_with_indicators_.csv"
    start_backtest(file, stock, channel)
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

    return jsonify({"message": f"Backtesting Started "})

def start_backtest(file, stock, channel):
    backtester = BackTest(file, stock)
    backtester.register_channel(channel)
