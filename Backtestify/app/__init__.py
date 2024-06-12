from gevent import monkey

monkey.patch_all()
from logging import Logger

from database import *
from flask import Flask

from .config import Config

logger: Logger = None  # type: ignore

from .extensions import client_manager, configure_logging, cors, socketio

client_events = None
strategy_events = None


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    socketio.init_app(
        app,
        async_mode="gevent",
        cors_allowed_origins="*",
        client_manager=client_manager,
    )
    cors.init_app(app)
    global logger
    logger = configure_logging(app)

    # Register blueprints
    from .socketio_events import StrategyEvents

    global strategy_events
    strategy_events = StrategyEvents(socketio)
    strategy_events.register_events()

    from .routes import api as api_blueprint

    app.register_blueprint(api_blueprint)

    return app
