import os
from datetime import datetime

from flask import jsonify, request

from api import app
from backtesting.backtester import BackTester
from market_data import marketDataQuote, marketFeedQuote
from market_data.schedule import schedule_until_sunday
from database import db
from database import APIKey, Symbol

from .misc import get_access_token


def secure_route(route):
    def secure_route_decorator(*args, **kwargs):
        if request.headers.get("Authorization") is None:
            return jsonify({"message": "Unauthorized"}), 401
        if request.headers.get("Authorization") == "Bearer 1234":
            a = route(*args, **kwargs)
            return a
        return jsonify({"message": "Unauthorized"}), 401

    return secure_route_decorator


@app.route("/add_api_key", methods=["POST"])
def add_api_key():
    if request.method == "POST":
        key = request.json["key"]
        secret = request.json["secret"]
        expiry = datetime.strptime(request.json["expiry"], "%Y-%m-%d")
        platform = request.json["platform"]
        api_key = APIKey(key=key, secret=secret, expiry=expiry, platform=platform)
        db.session.add(api_key)
        db.session.commit()
        return jsonify({"message": "API Key added successfully"})
    return jsonify({"message": "Method not allowed"}), 405


@app.route("/get_api_key", methods=["GET"])
def get_api_key():
    if request.method == "GET":
        api_keys = APIKey.query.all()
        api_keys = [{"key": key.key, "secret": key.secret} for key in api_keys]
        return jsonify(api_keys)
    return jsonify({"message": "Method not allowed"}), 405


@app.route("/start")
def start():
    platform = "dhan"
    access_token = get_access_token(platform)
    if access_token is False:
        return jsonify({"message": "API Key expired"})

    marketDataQuote.set_api_key(access_token["key"], access_token["secret"])

    instruments = Symbol.query.all()
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
        symbol = request.json["symbol"]
        exchange = request.json["exchange"]

        # Check if symbol already exists
        existing_symbol = Symbol.query.filter_by(
            symbol=symbol, exchange=exchange
        ).first()
        if existing_symbol:
            return jsonify({"message": "Symbol already exists"}), 400

        symbol = Symbol(symbol=symbol, exchange=exchange)
        db.session.add(symbol)
        db.session.commit()
        return jsonify({"message": "Symbol added successfully"})
    return jsonify({"message": "Method not allowed"}), 405


@app.route("/delete_symbols", methods=["DELETE"])
def delete_symbols():
    if request.method == "DELETE":
        symbol = request.json["symbol"]
        exchange = request.json["exchange"]

        # Check if symbol exists
        existing_symbol = Symbol.query.filter_by(symbol=symbol, exchange=exchange).all()
        if not existing_symbol:
            return jsonify({"message": "Symbol does not exist"}), 400

        for db_symbol in existing_symbol:
            db.session.delete(db_symbol)
        db.session.commit()
        return jsonify({"message": "Symbol deleted successfully"})
    return jsonify({"message": "Method not allowed"}), 405


@app.route("/schedule", methods=["GET"])
def schedule():
    schedule_until_sunday()
    return jsonify({"message": "Scheduled until upcoming Sunday"})


@app.route("/backtest", methods=["GET"])
def backtest():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file_rel_path = "historical_data/HDFC_with_indicators_.csv"
    csv_file_abs_path = os.path.join(current_dir, csv_file_rel_path)

    backtester = BackTester(csv_file_abs_path)
    backtester.backtest()
    return jsonify({"message": "Started Backtesting"})
