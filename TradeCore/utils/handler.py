import logging
from functools import wraps

from flask import jsonify
from pydantic import ValidationError

logger = logging.getLogger(__name__)


def handle_request(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            response = func(*args, **kwargs)
            return response
        except ValidationError as e:
            logger.error(f"Validation error {str(e)}")
            return jsonify(e.errors()), 422
        except Exception as exc:
            logger.error(f"Error {str(e)}")
            return jsonify({"error": "Internal Server Error", "details": str(exc)}), 500

    return wrapper


def handle_response(response_data=None, status=200):
    logger.info(response_data)
    response = {
        "status": "success" if status == 200 else "error",
        "data": response_data,
    }
    return jsonify(response), status
