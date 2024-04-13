from flask import jsonify, request
from market_data import app, db
from market_data.models import APIKey, Symbol
from datetime import datetime
from market_data.misc import get_access_token
from market_data import (
    marketDataTicker,
    marketFeedTicker,
    marketDataQuote,
    marketFeedQuote,
)
from .misc import analyser


# Need to add security to the API
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


# This is probably not required
@app.route("/get_api_key", methods=["GET"])
def get_api_key():
    if request.method == "GET":
        api_keys = APIKey.query.all()
        api_keys = [{"key": key.key, "secret": key.secret} for key in api_keys]
        return jsonify(api_keys)
    return jsonify({"message": "Method not allowed"}), 405


# The button to start the live-data-processing
# Need to add security to the API
@app.route("/start")
def start():
    platform = "dhan"
    access_token = get_access_token(platform)
    if access_token is False:
        return jsonify({"message": "API Key expired"})

    marketDataTicker.set_api_key(access_token["key"], access_token["secret"])
    marketDataQuote.set_api_key(access_token["key"], access_token["secret"])
    marketDataTicker.analyser = analyser
    marketDataQuote.analyser = analyser

    instruments = Symbol.query.all()
    ins_list = []
    for ins in instruments:
        ins_list.append(ins.symbol)
    marketDataTicker.instruments = ins_list
    marketDataQuote.instruments = ins_list

    # marketFeedTicker.start()
    marketFeedQuote.start()

    return jsonify({"output": "Market data running"})


# The button to stop the live-data-processing
# Need to add security to the API
@app.route("/stop", methods=["GET"])
def stop():
    marketFeedTicker.stop()
    marketFeedQuote.stop()
    return jsonify({"output": "Market data stopped"})


# Need to add security to the API
@app.route("/add_symbols", methods=["POST"])
def add_symbols():
    if request.method == "POST":
        symbol = request.json["symbol"]
        exchange = request.json["exchange"]
        symbol = Symbol(symbol=symbol, exchange=exchange)
        db.session.add(symbol)
        db.session.commit()
        return jsonify({"message": "Symbol added successfully"})
    return jsonify({"message": "Method not allowed"}), 405
