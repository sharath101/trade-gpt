import logging
import os
import subprocess
import uuid
import shutil
from datetime import datetime, timedelta

from flask import jsonify, request, render_template


from api import app, logger
from backtesting import BackTester
from database import APIKey, DhanOrderBook, Symbol
from market_data import (
    DHAN_INSTRUMENTS,
    marketDataQuote,
    marketFeedQuote,
    schedule_until_sunday,
)
from utils import Processor
from strategy import StrategyImporter
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

@app.route("/")
def index():
    return render_template("index.html")


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
async def start(platform) -> jsonify:
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


@app.route("/backtest/<stock>", methods=["GET"])
def backtest(stock):
    file = f"{stock}_with_indicators_.csv"
    backtester = BackTester(file, stock)
    if app.config["PYTHON_ENV"] == "PROD":
        new_process = Processor(backtester)
        new_process.start()
    else:
        backtester.backtest()
    return jsonify({"message": "Backtesting Started"})


@app.route("/postback/dhan", methods=["POST"])
def postback():
    data = request.json
    if data["dhanClientId"] and data["orderId"]:
        order = DhanOrderBook.get_first(
            client_id=data["dhanClientId"], order_id=data["orderId"]
        )
        if order:
            order.order_status = data["status"]
            order.save()
            return jsonify({"message": "Postback received"})
    return jsonify({"message": "Postback received"})


@app.route("/add_startegy", methods=["POST"])
def add_strategy():
    from strategy.strategy_builder import StrategyImporter
    data = request.json
    si = StrategyImporter()
    si.importclass(data["strategy"])
    return "OK"


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    files = data.get('files', {})

    if 'main.py' not in files:
        return jsonify({'error': 'At least one file must be named main.py', 'errors': {}, 'suspicious': {}})

    errors = {}
    suspicious = {}
    strategy_importer = StrategyImporter()

    for filename, code in files.items():
        file_errors, file_suspicious = strategy_importer.parse(code, files.keys())
        errors[filename] = file_errors
        suspicious[filename] = file_suspicious
    return jsonify({'errors': errors, 'suspicious': suspicious})


@app.route('/run', methods=['POST'])
def run_code():
    data = request.get_json()
    files = data.get('files', {})

    errors = {}
    suspicious = {}

    strategy_importer = StrategyImporter()

    if 'main.py' not in files:
        return jsonify({'error': 'At least one file must be named main.py', 'errors': {}, 'suspicious': {}})

    # Analyze each file first
    for filename, code in files.items():
        file_errors, file_suspicious = strategy_importer.parse(code, files.keys())
        errors[filename] = file_errors
        suspicious[filename] = file_suspicious

    # If there are errors, do not run the code
    if any(errors.values()) or any(suspicious.values()):
        return jsonify({'errors': errors, 'suspicious': suspicious, 'output': '', 'error': 'Code contains errors. Fix them before running.'})

    # Create a unique directory for the user session
    session_id = str(uuid.uuid4())
    session_dir = os.path.join(app.config['DATA'], session_id)
    os.makedirs(session_dir)

    # Save each file
    for filename, code in files.items():
        with open(os.path.join(session_dir, filename), 'w') as f:
            f.write(code)

    try:
        # Run the main file inside a Docker container or a subprocess
        result = subprocess.run(
            ['python', os.path.join(session_dir, 'main.py')],
            capture_output=True,
            text=True,
            cwd=session_dir,
            timeout=10
        )
        output = result.stdout
        error = result.stderr
    except subprocess.TimeoutExpired:
        output = ""
        error = "Error: Code execution timed out"
    finally:
        # Clean up the user's files
        shutil.rmtree(session_dir)
    
    return jsonify({'errors': errors, 'suspicious': suspicious, 'output': output, 'error': error})
