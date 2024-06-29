import logging
import sys

from config import Config
from database import StrategyBook
from flask import Flask
from flask_cors import CORS
from utils.logging import get_logger

from .models import *

logger = get_logger(Config.StrategEase.NAME, logging.DEBUG)
cors = CORS()


def create_app():
    app = Flask(Config.StrategEase.NAME)
    python_path = Config.Misc.PYTHONPATH
    if python_path and python_path not in sys.path:
        sys.path.append(python_path)

    cors.init_app(app)

    # Register blueprints
    from .routes import api as api_blueprint

    app.register_blueprint(api_blueprint)

    return app
