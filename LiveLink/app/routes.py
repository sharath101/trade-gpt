import asyncio
from datetime import datetime, timedelta
from secrets import token_hex

import requests
from app import APIKey, Config, Symbol, logger
from flask import Blueprint, request
from utils import DHAN_INSTRUMENTS, Processor

from .services import BinanceMarketFeed, DhanMarketFeed, LiveTrade

api = Blueprint("api", __name__)


@api.route("/")
def index():
    return {"success": True}, 200


@api.route("/live/start/<symbol>", methods=["POST"])
async def start(symbol):
    channel: str = token_hex(10)
    user_id = "abc"

    strategy_data = {"user_id": user_id, "symbol": symbol, "channel": channel, "live": True}
    strategy_service_url = Config.STRATEGY_BASE
    print(f"{strategy_service_url}/strategy/launch/live")
    try:
        response = requests.post(
            f"{strategy_service_url}/strategy/launch",
            json=strategy_data,
        )
        response.raise_for_status()
        data = response.json()
        logger.info(f'Strategy container created with id: {data['data']['container_id']}')
    except requests.exceptions.RequestException as e:
        return {"message": "Failed to launch strategy", "error": str(e)}, 500

    # market_feed = DhanMarketFeed()
    market_feed = BinanceMarketFeed()
    symbols = [symbol]

    live_trade = LiveTrade(symbols, channel, market_feed, 5)

    await live_trade.connect()

    # marketFeedQuote = Processor(live_trade)
    # marketFeedQuote.start()
    return {"output": "Market data running"}


# @api.route("/live/stop", methods=["GET"])
# def stop():
#     marketFeedQuote.stop()
#     return {"output": "Market data stopped"}


@api.route("/live/api_key", methods=["POST"])
def add_api_key():
    try:
        key = request.json["key"]
        secret = request.json["secret"]
        platform = request.json["platform"]
        expiry = request.json["expiry"]
        if platform not in ["dhan"]:
            return {"message": "Invalid platform"}, 400
    except Exception as e:
        return {"message": "Invalid data provided"}, 400
    expiry = datetime.strptime(expiry, "%Y-%m-%d")
    api_key = APIKey(
        key=key, secret=secret, expiry=expiry, platform=platform, trading=True
    )
    api_key.save()
    return {"message": "API Key added successfully"}


@api.route("/live/api_key", methods=["GET"])
def get_api_key():
    api_keys = APIKey.get_all()
    api_keys = [{"key": key.key, "secret": key.secret} for key in api_keys]
    return {"success": "True", "data": api_keys}, 200


@api.route("/add_symbols", methods=["POST"])
def add_symbols():
    if request.method == "POST":
        try:
            symbol = request.json["symbol"]
            exchange = request.json["exchange"]
        except Exception as e:
            return {"message": "Invalid data provided"}, 400
        # Check if symbol already exists
        existing_symbol = Symbol.get_first(symbol=symbol, exchange=exchange)
        if existing_symbol:
            return {"message": "Symbol already exists"}, 400
        if symbol not in DHAN_INSTRUMENTS["symbol"]:
            return {"message": "Invalid symbol"}, 400
        symbol = Symbol(symbol=symbol, exchange=exchange)
        symbol.save()
        return {"message": "Symbol added successfully"}
    return {"message": "Method not allowed"}, 405


@api.route("/delete_symbols", methods=["DELETE"])
def delete_symbols():
    try:
        symbol = request.json["symbol"]
        exchange = request.json["exchange"]
    except Exception as e:
        return {"message": "Invalid data provided"}, 400
    # Check if symbol exists
    existing_symbol = Symbol.get_first(symbol=symbol, exchange=exchange)
    if not existing_symbol:
        return {"message": "Symbol does not exist"}, 400
    existing_symbol.delete()
    return {"message": "Symbol deleted successfully"}


@api.route("/get_symbols", methods=["GET"])
def get_symbols():
    symbols = Symbol.get_all()
    symbols = [
        {"symbol": symbol.symbol, "exchange": symbol.exchange} for symbol in symbols
    ]
    return symbols


# @api.route("/schedule", methods=["GET"])
# def schedule():
#     schedule_until_sunday()
#     return {"message": "Scheduled until upcoming Sunday"}
