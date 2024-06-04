import logging
import sys

from database import StrategyBook
from flask import Flask
from utils.logging import get_logger

from .config import Config
from .models import Strategy

NAME = "StrategEase"
logger = get_logger(NAME, logging.DEBUG)


def create_app():
    app = Flask(NAME)
    python_path = Config.PYTHONPATH
    if python_path and python_path not in sys.path:
        sys.path.append(python_path)

    # Register blueprints
    from .routes import api as api_blueprint

    app.register_blueprint(api_blueprint)

    return app
