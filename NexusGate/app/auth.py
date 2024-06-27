import os
from functools import wraps

from config import Config
from database.users import Users
from flask import jsonify, make_response, redirect, request

from . import app, bcrypt, client, logger
from .oauth_google import get_google_provider_cfg

HOST = Config.NexusGate.HOST


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        data = request.headers.get("Authorization")
        token = str.replace(str(data), "Bearer ", "")
        if not token:
            return jsonify({"status": "failure", "message": "Token is missing"}), 200
        user = Users.decode_auth_token(token)
        if not user:
            return jsonify({"status": "failure", "message": "User not found"}), 200

        response = f(*args, user=user, **kwargs)

        if not isinstance(response, tuple):
            response = jsonify(response), 200

        auth_token = user.encode_auth_token(user.id)
        if auth_token:
            server_response = make_response(*response)
            server_response.headers["Authorization"] = auth_token
        server_response.headers["Access-Control-Expose-Headers"] = "Authorization"

        return server_response

    return decorated


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":

        google_provider_cfg = get_google_provider_cfg()
        authorization_endpoint = google_provider_cfg["authorization_endpoint"]

        request_uri = client.prepare_request_uri(
            authorization_endpoint,
            redirect_uri=f"{HOST}/login/callback",
            scope=["openid", "email", "profile"],
        )
        return redirect(request_uri)

    elif request.method == "POST":
        try:
            if (
                not request.headers.get("Content-Type")
                or request.headers.get("Content-Type") != "application/json"
            ):
                response_data = {
                    "status": "failure",
                    "message": "Content-Type not allowed",
                }
                response = make_response(jsonify(response_data), 200)

                return response

            data = request.get_json()
            email = data.get("email")
            password = data.get("password")

            user = Users.get_first(email=email)
            if user and bcrypt.check_password_hash(user.password, password):
                auth_token = user.encode_auth_token(user.id)
                if auth_token:
                    response_data = {"status": "success"}
                    response = make_response(jsonify(response_data), 200)
                    response.headers["Authorization"] = auth_token
                    response.headers["Access-Control-Expose-Headers"] = "Authorization"
                else:
                    response_data = {"status": "failure"}
                    response = make_response(jsonify(response_data), 200)

            else:
                response_data = {
                    "status": "failure",
                    "message": "Incorrect username or password!",
                }
                response = make_response(jsonify(response_data), 200)

            return response

        except Exception as e:
            logger.exception(f"Error in /login: {e}")
            response_data = {"status": "failure", "message": "Content-Type not allowed"}
            response = make_response(jsonify(response_data), 200)

            return response

    else:
        response_data = {"status": "failure", "message": "Method not allowed"}
        response = make_response(jsonify(response_data), 400)
        return response


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "GET":

        google_provider_cfg = get_google_provider_cfg()
        authorization_endpoint = google_provider_cfg["authorization_endpoint"]

        request_uri = client.prepare_request_uri(
            authorization_endpoint,
            redirect_uri=f"{HOST}/login/callback",
            scope=["openid", "email", "profile"],
        )
        return redirect(request_uri)

    elif request.method == "POST":
        try:
            if (
                not request.headers.get("Content-Type")
                or request.headers.get("Content-Type") != "application/json"
            ):
                response_data = {
                    "status": "failure",
                    "message": "Content-Type not allowed",
                }
                response = make_response(jsonify(response_data), 200)

                return response

            data = request.json
            if not data:
                response_data = {
                    "status": "failure",
                    "message": "No data received!",
                }
                response = make_response(jsonify(response_data), 200)
                return response

            email = data.get("email")
            password = data.get("password")
            name = data.get("name")
            existing_user = Users.get_first(email=email)
            if existing_user:
                response_data = {
                    "status": "failure",
                    "message": "Email already registered. Sign In instead!",
                }

                response = make_response(jsonify(response_data), 200)
                return response

            password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
            user = Users(email=email, password=password_hash, name=name)

            user.save()

            response_data = {
                "status": "success",
                "message": "Account created successfully!",
            }

            response = make_response(jsonify(response_data), 200)

            return response
        except Exception as e:
            logger.error(f"Error in /register: {e}")
            response_data = {"status": "failure", "message": "Email already registered"}
            response = make_response(jsonify(response_data), 200)

            return response

    else:
        response_data = {"status": "failure", "message": "Method not allowed"}
        response = make_response(jsonify(response_data), 400)
        return response


@app.route("/check_login")
@token_required
def check_login(user):
    return {"status": "success"}
