import asyncio
import logging
import os
import shutil
import subprocess
import threading
import uuid
from datetime import datetime, timedelta

from api import app, logger
from backtesting import BackTester
from database import APIKey, DhanOrderBook, StrategyBook, Symbol
from flask import jsonify, make_response, render_template, request
from market_data import (
    DHAN_INSTRUMENTS,
    marketDataQuote,
    marketFeedQuote,
    schedule_until_sunday,
)
from strategy import StrategyImporter
from utils import deploy_container
from werkzeug.utils import secure_filename

from .misc import get_access_token


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
    startegy_names = StrategyBook.get_all()
    file_data = startegy_names[0].folder_loc
    strat_dic = os.path.join(app.config["UPLOAD_FOLDER"], file_data)
    session_id = str(uuid.uuid4())
    volumes = {
        strat_dic: {
            "bind": "/app/user_strategies",
            "mode": "ro",
        }
    }
    conatiner = deploy_container("test:1", session_id, volumes=volumes)

    # if app.config["PYTHON_ENV"] == "PROD":
    #   new_process = Processor(backtester)
    #   new_process.start()
    # else:
    #   backtester.connect()

    backtester.connect()

    return jsonify({"message": f"Backtesting Started {conatiner.id}"})


def connect_backtester(backtester):
    asyncio.run(backtester.connect())


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


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    files = data.get("files", {})

    if "main.py" not in files:
        return jsonify(
            {
                "error": "At least one file must be named main.py",
                "errors": {},
                "suspicious": {},
            }
        )

    errors = {}
    suspicious = {}
    strategy_importer = StrategyImporter()

    for filename, code in files.items():
        file_errors, file_suspicious = strategy_importer.parse(code, files.keys())
        errors[filename] = file_errors
        suspicious[filename] = file_suspicious
    return jsonify({"errors": errors, "suspicious": suspicious})


@app.route("/run", methods=["POST"])
def run_code():
    data = request.get_json()
    files = data.get("files", {})

    errors = {}
    suspicious = {}

    strategy_importer = StrategyImporter()

    if "main.py" not in files:
        return jsonify(
            {
                "error": "At least one file must be named main.py",
                "errors": {},
                "suspicious": {},
            }
        )

    # Analyze each file first
    for filename, code in files.items():
        file_errors, file_suspicious = strategy_importer.parse(code, files.keys())
        errors[filename] = file_errors
        suspicious[filename] = file_suspicious

    # If there are errors, do not run the code
    if any(errors.values()) or any(suspicious.values()):
        return jsonify(
            {
                "errors": errors,
                "suspicious": suspicious,
                "output": "",
                "error": "Code contains errors. Fix them before running.",
            }
        )

    # Create a unique directory for the user session
    session_id = str(uuid.uuid4())
    session_dir = os.path.join(app.config["DATA"], session_id)
    os.makedirs(session_dir)

    # Save each file
    for filename, code in files.items():
        with open(os.path.join(session_dir, filename), "w") as f:
            f.write(code)

    try:
        # Run the main file inside a Docker container or a subprocess
        result = subprocess.run(
            ["python", os.path.join(session_dir, "main.py")],
            capture_output=True,
            text=True,
            cwd=session_dir,
            timeout=10,
        )
        output = result.stdout
        error = result.stderr
    except subprocess.TimeoutExpired:
        output = ""
        error = "Error: Code execution timed out"
    finally:
        # Clean up the user's files
        shutil.rmtree(session_dir)

    return jsonify(
        {"errors": errors, "suspicious": suspicious, "output": output, "error": error}
    )


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
    )


@app.route("/upload_strategy", methods=["POST"])
def add_strategy():
    try:
        strategy_name = request.form.get("strategy_name")
        indicators = request.form.getlist("indicators")
        description = request.form.get("description")
        folder_loc = f"{strategy_name}"

        if not all([strategy_name, indicators]):
            return jsonify({"error": "Missing required parameters"}), 400

        folder_path = os.path.join(app.config["UPLOAD_FOLDER"], folder_loc)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        files = request.files.getlist("files")
        if not files:
            return jsonify({"error": "No files provided"}), 400

        new_strategy = StrategyBook(
            strategy_name=strategy_name,
            indicators=indicators,
            folder_loc=folder_loc,
            description=description,
        )

        new_strategy.save()

        file_data = {}
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(
                    os.path.join(app.config["UPLOAD_FOLDER"], folder_loc, filename)
                )
                with open(
                    os.path.join(app.config["UPLOAD_FOLDER"], folder_loc, filename), "r"
                ) as f:
                    file_data[filename] = f.read()

        return jsonify({"message": "Strategy created successfully!"}), 201

    except KeyError as e:
        return jsonify({"error": f"Missing required parameter: {e}"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/update_strategy/<int:strategy_id>", methods=["POST"])
def update_strategy(strategy_id):
    try:
        strategy_name = request.form.get("strategy_name")
        indicators = request.form.getlist("indicators")
        description = request.form.get("description")
        folder_loc = f"{strategy_name}"

        if not all([strategy_name, indicators]):
            return jsonify({"error": "Missing required parameters"}), 400

        strategy: StrategyBook = StrategyBook.get_first(id=strategy_id)
        if not strategy:
            return jsonify({"error": "Strategy not found"}), 404

        folder_path = os.path.join(app.config["UPLOAD_FOLDER"], strategy.folder_loc)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)

        folder_path = os.path.join(app.config["UPLOAD_FOLDER"], folder_loc)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        files = request.files.getlist("files")
        if not files:
            return jsonify({"error": "No files provided"}), 400

        strategy.delete()
        new_strategy = StrategyBook(
            id=strategy_id,
            strategy_name=strategy_name,
            indicators=indicators,
            folder_loc=folder_loc,
            description=description,
        )
        new_strategy.save()

        file_data = {}
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(
                    os.path.join(app.config["UPLOAD_FOLDER"], folder_loc, filename)
                )
                with open(
                    os.path.join(app.config["UPLOAD_FOLDER"], folder_loc, filename), "r"
                ) as f:
                    file_data[filename] = f.read()

        return jsonify({"message": "Strategy created successfully!"}), 201

    except KeyError as e:
        return jsonify({"error": f"Missing required parameter: {e}"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/get_strategies", methods=["GET"])
def get_strategies():
    try:
        all_strategies = StrategyBook.get_all_dict()
        return jsonify({"status": "success", "data": all_strategies}), 201
    except Exception as e:
        logger.error(f"Error in /get_strategies: {e}")
        response_data = {"status": "failure", "message": e}
        response = make_response(jsonify(response_data), 200)

        return response


@app.route("/delete_strategy/<int:strategy_id>", methods=["DELETE"])
def delete_strategy(strategy_id):
    try:
        strategy: StrategyBook = StrategyBook.get_first(id=strategy_id)
        if not strategy:
            return jsonify({"error": "Strategy not found"}), 404

        folder_path = os.path.join(app.config["UPLOAD_FOLDER"], strategy.folder_loc)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)

        strategy.delete()

        return (
            jsonify({"status": "success", "message": "Strategy deleted successfully!"}),
            200,
        )

    except Exception as e:
        response_data = {"status": "failure", "message": e}
        response = make_response(jsonify(response_data), 200)
        return response


@app.route("/get_strategy/<int:strategy_id>", methods=["GET"])
def get_strategy(strategy_id):
    strategy: StrategyBook = StrategyBook.get_first(id=strategy_id)
    if not strategy:
        return jsonify({"error": "Strategy not found"}), 404

    strategy_details = {
        "strategy_name": strategy.strategy_name,
        "indicators": strategy.indicators,
        "description": strategy.description,
        "files": [],
    }

    folder_loc = strategy.folder_loc
    strategy_folder = os.path.join(app.config["UPLOAD_FOLDER"], folder_loc)
    if os.path.isdir(strategy_folder):
        for filename in os.listdir(strategy_folder):
            file_path = os.path.join(strategy_folder, filename)
            if os.path.isfile(file_path):
                with open(file_path, "r") as file:
                    strategy_details["files"].append(
                        {"filename": filename, "code": file.read()}
                    )

    return jsonify({"status": "success", "data": strategy_details})
