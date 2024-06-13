import logging

from database import *
from flask import Flask
from utils import CandleManager, redis_instance, redis_instance_backtest
from utils.logging import get_logger

from .config import Config
from .extensions import client_manager, cors, socketio

logger = get_logger(Config.NAME, logging.DEBUG)


def create_app():
    app = Flask(Config.NAME)
    app.config.from_object(Config)

    socketio.init_app(
        app,
        async_mode="threading",
        cors_allowed_origins="*",
        client_manager=client_manager,
    )
    cors.init_app(app)

    # Register blueprints
    from .socketio_events import ClientEvents, StrategyEvents

    global client_events
    client_events = ClientEvents(socketio)
    client_events.register_events()

    global strategy_events
    strategy_events = StrategyEvents(socketio)
    strategy_events.register_events()

    # Register blueprints
    from .routes import api as api_blueprint

    app.register_blueprint(api_blueprint)
    return app
