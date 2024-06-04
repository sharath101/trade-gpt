import sys

from database import StrategyBook
from flask import Flask

from .config import Config
from .routes import *
from .routes import api as api_blueprint


def create_app():
    app = Flask("StrategEase")
    python_path = Config.PYTHONPATH
    if python_path and python_path not in sys.path:
        sys.path.append(python_path)

    # Register blueprints
    app.register_blueprint(api_blueprint)

    return app
