import json
import os
from secrets import token_hex

from app import (
    Config,
    LaunchStrategyRequestBody,
    Strategy,
    StrategyBook,
    UploadStrategyRequestBody,
    logger,
)
from flask import Blueprint, request
from utils import deploy_container, handle_request
from werkzeug.utils import secure_filename

api = Blueprint("api", __name__)


@api.route("/strategy/launch", methods=["POST"])
@handle_request
def launch_strategy():
    strategy = LaunchStrategyRequestBody(**request.json)  # type: ignore
    stock = strategy.symbol
    logger.debug(stock)

    environment = {
        "SYMBOL": stock,
        "BALANCE": 2000,
        "SOCKET_URL": Config.SOCKET_URL,
        "CHANNEL": strategy.channel,
    }

    # Hardcoding strategy name to "abc"
    # TODO: Download the strategy files from object storage
    host_mount = Config.UPLOAD_FOLDER + "/abc"
    volumes = {
        host_mount: {
            "bind": "/StratRun/app/user_strategies",
            "mode": "ro",
        }
    }
    logger.debug(volumes)

    try:
        image = Config.STRATRUN["IMAGE"] + ":" + str(Config.STRATRUN["VERSION"])
        logger.debug(image)
        container = deploy_container(
            image,
            volumes=volumes,
            environment=environment,
        )
        logger.debug(container.id)
        return {"container_id": container.id}, 200
    except Exception as e:
        # Handle errors and return an appropriate response
        logger.error(f"Failed to launch container {str(e)}")
        return {"message": "Failed to launch container"}, 500


@api.route("/strategy/upload", methods=["POST"])
# @token_required
@handle_request
def upload_strategy():

    request_data = request.form["data"]
    json_data = json.loads(request_data)
    data = UploadStrategyRequestBody(**json_data)

    strategy_name = data.name
    indicators = data.indicators
    description = data.description
    user_id = data.user_id

    logger.info(
        f"Upload strategy request from user {user_id} for strategy {strategy_name}"
    )

    folder_loc = f"{token_hex(16)}"

    try:
        if "files" not in request.files:
            return "No files provided", 400

        files = request.files.getlist("files")

        folder_path = os.path.join(Config.UPLOAD_FOLDER, folder_loc)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        new_strategy = StrategyBook(
            user_id=user_id,
            strategy_name=strategy_name,
            indicators=[obj.model_dump_json() for obj in indicators],
            folder_loc=folder_loc,
            description=description,
        )

        new_strategy.save()

        logger.debug(f"Saved new strategy {strategy_name} to database.")

        # TODO: Upload the files to object storage
        file_data = {}
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(Config.UPLOAD_FOLDER, folder_loc, filename))
                with open(
                    os.path.join(Config.UPLOAD_FOLDER, folder_loc, filename), "r"
                ) as f:
                    file_data[filename] = f.read()

        return (
            "Strategy created successfully!",
            201,
        )

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return f"error: {str(e)}", 500


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
@handle_request
def get_strategies():
    try:
        all_strategies = StrategyBook.get_all()

        # Convert SQLAlchemy objects to dictionaries
        strategies_dict = [strategy.__dict__ for strategy in all_strategies]

        # Remove internal state objects
        for strategy in strategies_dict:
            strategy.pop("_sa_instance_state", None)

        return strategies_dict, 200

    except Exception as e:
        logger.error(f"Error in GET strategy: {e}")
        return "Error while getting all strategies", 400


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


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in Config.ALLOWED_EXTENSIONS
    )
