import logging
import os
from secrets import token_hex

import app
from app import Config, StrategyBook
from app.models import Strategy
from flask import Blueprint, request
from utils import deploy_container, handle_request, handle_response

logger = logging.getLogger(__name__)

api = Blueprint("api", __name__)


@api.route("/strategy/launch", methods=["POST"])
# @handle_request
def launch_strategy():
    startegy = Strategy(**request.json)
    stock = startegy.symbol
    environment = {"SYMBOL": stock, "BALANCE": 2000, "BACKTESTING": True}
    volumes = {
        # TODO:Host mount point??
        # strat_dic: {
        #     "bind": "/app/user_strategies",
        #     "mode": "ro",
        # }
    }

    try:
        container_id = deploy_container(
            Config.STRATRUN["IMAGE"] + ":" + str(Config.STRATRUN["VERSION"]),
            volumes=volumes,
            environment=environment,
        )
        return {"container_id": container_id}, 200
    except Exception as e:
        # Handle errors and return an appropriate response
        logger.error(f"Failed to launch container {str(e)}")
        return handle_response({"message": "Failed to launch container"}, 500)


# @app.route("/strategy/upload", methods=["POST"])
# # @token_required
# @handle_request
# def add_strategy(data):
#     try:
#         strategy_name = data.get("strategy_name")
#         indicators = data.get("indicators")
#         description = data.get("description")
#         folder_loc = f"{token_hex(16)}"

#         if not all([strategy_name, indicators]):
#             return handle_response({"message": "Missing required parameters"}), 400

#         folder_path = os.path.join(app.config["UPLOAD_FOLDER"], folder_loc)
#         if not os.path.exists(folder_path):
#             os.makedirs(folder_path)

#         files = request.files.getlist("files")
#         if not files:
#             return handle_response({"message": "No files provided"}), 400

#         new_strategy = StrategyBook(
#             user_id=user.id,
#             strategy_name=strategy_name,
#             indicators=indicators,
#             folder_loc=folder_loc,
#             description=description,
#         )

#         new_strategy.save()

#         file_data = {}
#         for file in files:
#             if file and allowed_file(file.filename):
#                 filename = secure_filename(file.filename)
#                 file.save(
#                     os.path.join(app.config["UPLOAD_FOLDER"], folder_loc, filename)
#                 )
#                 with open(
#                     os.path.join(app.config["UPLOAD_FOLDER"], folder_loc, filename), "r"
#                 ) as f:
#                     file_data[filename] = f.read()

#         return (
#             jsonify({"status": "success", "message": "Strategy created successfully!"}),
#             201,
#         )

#     except KeyError as e:
#         return (
#             jsonify({"status": "failure", "error": f"Missing required parameter: {e}"}),
#             400,
#         )

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


# @app.route("/update_strategy/<int:strategy_id>", methods=["POST"])
# # @token_required
# def update_strategy(strategy_id, user):
#     try:
#         strategy_name = request.form.get("strategy_name")
#         indicators = request.form.get("indicators")
#         description = request.form.get("description")
#         if not all([strategy_name, indicators]):
#             return (
#                 jsonify({"status": "failure", "error": "Missing required parameters"}),
#                 400,
#             )

#         strategy = StrategyBook.get_first(id=strategy_id, user_id=user.id)
#         if not strategy:
#             return jsonify({"status": "failure", "error": "Strategy not found"}), 404

#         old_folder_path = os.path.join(app.config["UPLOAD_FOLDER"], strategy.folder_loc)
#         if os.path.exists(old_folder_path):
#             shutil.rmtree(f"{old_folder_path}")

#         files = request.files.getlist("files")
#         if not files:
#             return jsonify({"status": "failure", "error": "No files provided"}), 400

#         new_folder_path = os.path.join(app.config["UPLOAD_FOLDER"], strategy.folder_loc)
#         if not os.path.exists(new_folder_path):
#             os.makedirs(new_folder_path)

#         strategy.strategy_name = strategy_name
#         strategy.indicators = indicators
#         strategy.description = description
#     strategy.save()

#     for file in files:
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             file.save(os.path.join(new_folder_path, filename))

#     return (
#         jsonify({"status": "success", "message": "Strategy updated successfully!"}),
#         200,
#     )

# except KeyError as e:
#     return (
#         jsonify({"status": "failure", "error": f"Missing required parameter: {e}"}),
#         400,
#     )

# except Exception as e:
#     return jsonify({"status": "failure", "error": str(e)}), 500


@api.route("/strategy", methods=["GET"])
# @token_required
# @handle_request
def get_strategies():
    try:
        all_strategies = StrategyBook.get_all()
        return {"status": "success", "data": all_strategies}, 201
    except Exception as e:
        logger.error(f"Error in /get_strategies: {e}")
        response_data = {"status": "failure", "message": e}
        response = response_data, 200

        return response


# @app.route("/delete_strategy/<int:strategy_id>", methods=["DELETE"])
# # @token_required
# def delete_strategy(strategy_id, user):
#     try:
#         strategy: StrategyBook = StrategyBook.get_first(id=strategy_id)
#         if not strategy:
#             return jsonify({"error": "Strategy not found"}), 404

#         folder_path = os.path.join(app.config["UPLOAD_FOLDER"], strategy.folder_loc)
#         if os.path.exists(folder_path):
#             shutil.rmtree(folder_path)

#         strategy.delete()

#         return (
#             {"status": "success", "message": "Strategy deleted successfully!"},
#             200,
#         )

#     except Exception as e:
#         response_data = {"status": "failure", "message": e}
#         response = response_data, 200
#         return response


# @app.route("/get_strategy/<int:strategy_id>", methods=["GET"])
# # @token_required
# def get_strategy(strategy_id, user):
#     strategy: StrategyBook = StrategyBook.get_first(id=strategy_id)
#     if not strategy:
#         return jsonify({"error": "Strategy not found"}), 404

#     strategy_details = {
#         "strategy_name": strategy.strategy_name,
#         "indicators": strategy.indicators,
#         "description": strategy.description,
#         "files": [],
#     }

#     folder_loc = strategy.folder_loc
#     strategy_folder = os.path.join(app.config["UPLOAD_FOLDER"], folder_loc)
#     if os.path.isdir(strategy_folder):
#         for filename in os.listdir(strategy_folder):
#             file_path = os.path.join(strategy_folder, filename)
#             if os.path.isfile(file_path):
#                 with open(file_path, "r") as file:
#                     strategy_details["files"].append(
#                         {"filename": filename, "code": file.read()}
#                     )

#     return {"status": "success", "data": strategy_details}
