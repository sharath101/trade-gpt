from functools import wraps

import requests
from database.users import Users
from flask import json, jsonify, make_response, redirect, request

from . import (
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    GOOGLE_DISCOVERY_URL,
    app,
    bcrypt,
    client,
    logger,
)


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


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
        server_response = make_response(*response)
        server_response.headers["Authorization"] = auth_token
        server_response.headers["Access-Control-Expose-Headers"] = "Authorization"

        return server_response

    return decorated


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return redirect("/log")
    else:
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
                response_data = {"status": "success"}
                response = make_response(jsonify(response_data), 200)
                response.headers["Authorization"] = auth_token
                response.headers["Access-Control-Expose-Headers"] = "Authorization"

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


@app.route("/register", methods=["POST"])
def register():
    try:
        if (
            not request.headers.get("Content-Type")
            or request.headers.get("Content-Type") != "application/json"
        ):
            response_data = {"status": "failure", "message": "Content-Type not allowed"}
            response = make_response(jsonify(response_data), 200)

            return response

        data = request.json
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


@app.route("/user_info")
@token_required
def user_info(user: Users):
    return {"status": "success", "data": {"name": user.name, "email": user.email}}


@app.route("/log")
def log():
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri="http://127.0.0.1:5000/oauth_redirect",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


@app.route("/oauth_redirect")
def oauth_redirect():
    print(request.args)
    code = request.args.get("code")
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code,
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    client.parse_request_body_response(json.dumps(token_response.json()))

    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    return {
        "status": "success",
        "email": users_email,
        "picture": picture,
        "name": users_name,
    }
