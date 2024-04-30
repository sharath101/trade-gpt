import logging
from datetime import datetime, timedelta

from flask import jsonify, request

from api import app, logger
from backtesting import BackTester
from database import APIKey, Symbol, db
from market_data import marketDataQuote, marketFeedQuote
from market_data.constants import DHAN_INSTRUMENTS
from market_data.misc import backup_current_day, delete_old_data
from market_data.schedule import schedule_until_sunday

from .misc import get_access_token
from utils import scheduler


def secure_route(route):
    def secure_route_decorator(*args, **kwargs):
        if request.headers.get("Authorization") is None:
            return jsonify({"message": "Unauthorized"}), 401
        if request.headers.get("Authorization") == "Bearer 1234":
            a = route(*args, **kwargs)
            return a
        return jsonify({"message": "Unauthorized"}), 401

    return secure_route_decorator


@app.before_request
def set_log_level():
    log_level_param = request.args.get("log_level")
    if log_level_param == "error":
        log_level = logging.ERROR
    elif log_level_param == "warning":
        log_level = logging.WARNING
    elif log_level_param == "info":
        log_level = logging.INFO
    else:
        log_level = logging.DEBUG
    logger.setLevel(log_level)


@app.route("/add_api_key", methods=["POST"])
def add_api_key() -> jsonify:
    if request.method == "POST":
        try:
            key = request.json["key"]
            secret = request.json["secret"]
            platform = request.json["platform"]
            if platform not in ["dhan"]:
                return jsonify({"message": "Invalid platform"}), 400
        except Exception as e:
            return jsonify({"message": "Invalid data provided"}), 400

        try:
            expiry = datetime.strptime(request.json["expiry"], "%Y-%m-%d") + timedelta(
                hours=23
            )
        except Exception as e:
            return jsonify({"message": "Invalid expiry date"}), 400

        api_key = APIKey(key=key, secret=secret, expiry=expiry, platform=platform)

        if "trading" in request.json:
            if request.json["trading"] == "False":
                api_key.trading = False

        api_key.save()
        return jsonify({"message": "API Key added successfully"})
    return jsonify({"message": "Method not allowed"}), 405


@app.route("/get_api_key", methods=["GET"])
def get_api_key() -> jsonify:
    if request.method == "GET":
        api_keys = APIKey.get_all()
        api_keys = [{"key": key.key, "secret": key.secret} for key in api_keys]
        return jsonify(api_keys)
    return jsonify({"message": "Method not allowed"}), 405


@app.route("/start/<platform>")
def start(platform) -> jsonify:
    if platform not in ["dhan"]:
        return jsonify({"message": "Invalid platform"}), 400
    access_token = get_access_token(platform)
    if access_token is False:
        return jsonify({"message": "API Key expired"}), 400

    marketDataQuote.set_api_key(access_token["key"], access_token["secret"])

    instruments = Symbol.get_all()
    ins_list = []
    for ins in instruments:
        ins_list.append(ins.symbol)
    marketDataQuote.instruments = ins_list

    marketFeedQuote.start()

    return jsonify({"output": "Market data running"})


@app.route("/stop", methods=["GET"])
def stop():
    marketFeedQuote.stop()
    return jsonify({"output": "Market data stopped"})


@app.route("/add_symbols", methods=["POST"])
def add_symbols():
    if request.method == "POST":
        try:
            symbol = request.json["symbol"]
            exchange = request.json["exchange"]
        except Exception as e:
            return jsonify({"message": "Invalid data provided"}), 400

        # Check if symbol already exists
        existing_symbol = Symbol.get_first(symbol=symbol, exchange=exchange)
        if existing_symbol:
            return jsonify({"message": "Symbol already exists"}), 400

        if symbol not in DHAN_INSTRUMENTS["symbol"]:
            return jsonify({"message": "Invalid symbol"}), 400

        symbol = Symbol(symbol=symbol, exchange=exchange)
        symbol.save()
        return jsonify({"message": "Symbol added successfully"})
    return jsonify({"message": "Method not allowed"}), 405


@app.route("/delete_symbols", methods=["DELETE"])
def delete_symbols():
    if request.method == "DELETE":
        try:
            symbol = request.json["symbol"]
            exchange = request.json["exchange"]
        except Exception as e:
            return jsonify({"message": "Invalid data provided"}), 400

        # Check if symbol exists
        existing_symbol = Symbol.get_first(symbol=symbol, exchange=exchange)
        if not existing_symbol:
            return jsonify({"message": "Symbol does not exist"}), 400

        existing_symbol.delete()
        return jsonify({"message": "Symbol deleted successfully"})
    return jsonify({"message": "Method not allowed"}), 405


@app.route("/get_symbols", methods=["GET"])
def get_symbols():
    if request.method == "GET":
        symbols = Symbol.get_all()
        symbols = [
            {"symbol": symbol.symbol, "exchange": symbol.exchange} for symbol in symbols
        ]
        return jsonify(symbols)
    return jsonify({"message": "Method not allowed"}), 405


@app.route("/schedule", methods=["GET"])
def schedule():
    schedule_until_sunday()
    return jsonify({"message": "Scheduled until upcoming Sunday"})


@app.route("/backtest", methods=["GET"])
def backtest():
    file = "HDFC_with_indicators_.csv"
    backtester = BackTester(file)
    backtester.backtest()
    return jsonify({"message": "Backtesting Started"})
