from functools import wraps
from flask import jsonify, make_response, request

from api import app, bcrypt, logger
from database import Users


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        data = request.headers['Authorization']
        token = str.replace(str(data), 'Bearer ', '')
        if not token:
            return jsonify({"status": "failure", 'message': 'Token is missing'}), 200
        user = Users.decode_auth_token(token)
        if not user:
            return jsonify({"status": "failure", 'message': 'User not found'}), 200
        response = f(*args, **kwargs)
        auth_token = user.encode_auth_token(user.id)

        server_response = make_response(jsonify(response), 200)

        server_response.headers["Authorization"] = auth_token
        server_response.headers["Access-Control-Expose-Headers"] = "Authorization"

        return server_response
    
    return decorated


@app.route("/login", methods=["POST"])
def login():
    try:
        if (
            not request.headers.get("Content-Type")
            or request.headers.get("Content-Type") != "application/json"
        ):
            response_data = {"status": "failure", "message": "Content-Type not allowed"}
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
        response_data = {"status": "failure", "message": "Content-Type not allowed"}
        response = make_response(jsonify(response_data), 200)

        return response


@app.route("/check_login")
@token_required
def check_login():
    return {"status": "success"}
