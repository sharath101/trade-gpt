from flask import jsonify, request
from market_data import app, db
from market_data.models import APIKey
from datetime import datetime
from market_data.app_scheduler import MarketScheduler


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


@app.route("/market_sch", methods=["POST"])
def market_sch():
    if request.method == "POST":
        platform = request.json["platform"]
        date = datetime.strptime(request.json["date"], "%Y-%m-%d")
        market_scheduler = MarketScheduler()
        output = market_scheduler.scheduler_market_data(platform, date)
        return jsonify(output)
    return jsonify({"message": "Method not allowed"}), 405
