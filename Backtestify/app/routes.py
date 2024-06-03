from flask import Blueprint, jsonify, render_template, request

from app import logger

# from .services import BackTest

api = Blueprint("api", __name__)


@api.route("/")
def index():
    return render_template("index.html")


@api.route("/backtest/run/<stock>", methods=["GET"])
def backtest(stock):
    file = f"{stock}_with_indicators_.csv"
    # backtester = BackTest(file, stock)
    # startegy_names = StrategyBook.get_all()
    # file_data = startegy_names[0].folder_loc
    # strat_dic = os.path.join(app.config["UPLOAD_FOLDER"], file_data)
    # session_id = str(uuid.uuid4())
    # volumes = {
    #     strat_dic: {
    #         "bind": "/app/user_strategies",
    #         "mode": "ro",
    #     }
    # }
    # environment = {"SYMBOL": stock, "BALANCE": 2000, "BACKTESTING": True}
    # conatiner = deploy_container(
    #     "strategy_runner:latest", session_id, volumes=volumes, environment=environment
    # )

    # if app.config["PYTHON_ENV"] == "PROD":
    #   new_process = Processor(backtester)
    #   new_process.start()
    # else:
    #   backtester.connect()

    # backtester.connect()

    return jsonify({"message": f"Backtesting Started "})
