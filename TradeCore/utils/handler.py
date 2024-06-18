import logging
from functools import wraps

from flask import jsonify, request, make_response
from pydantic import ValidationError
from database import Users

logger = logging.getLogger(__name__)


def handle_request(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            data = request.headers.get("Authorization")
            token = str.replace(str(data), "Bearer ", "")
            if not token:
                return handle_response({"message": "Token is missing"}, 400)
            user = Users.decode_auth_token(token)
            if not user:
                return handle_response({"message": "User not found"}, 400)

            response, status = func(*args, **kwargs)

            return handle_response(response, status)
        except ValidationError as e:
            logger.error(f"Validation errors")
            return handle_response({"message": f"Invalid request: {e}"}, 422)
        except Exception as exc:
            logger.error(f"Error")
            return handle_response({"message": f"Internal Server Error: {exc}"}, 500)

    return wrapper


def handle_response(response_data=None, status=200, user=None):
    logger.info(response_data)
    response = {
        "status": "success" if status >= 200 and status < 300 else "error",
        "data": response_data,
    }

    if not user:
        return response, status

    if not isinstance(response, tuple):
        response = jsonify(response), status

    auth_token = user.encode_auth_token(user.id)
    if auth_token:
        server_response = make_response(*response)
        server_response.headers["Authorization"] = auth_token
    server_response.headers["Access-Control-Expose-Headers"] = "Authorization"

    return server_response
