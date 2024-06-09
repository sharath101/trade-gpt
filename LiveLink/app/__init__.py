import logging

from database import *
from flask import Flask
from utils import CandleManager, redis_instance, redis_instance_backtest
from utils.logging import get_logger

from .config import Config

logger = get_logger(Config.NAME, logging.DEBUG)


def create_app():
    app = Flask(Config.NAME)

    # Register blueprints
    from .routes import api as api_blueprint

    app.register_blueprint(api_blueprint)
    return app
