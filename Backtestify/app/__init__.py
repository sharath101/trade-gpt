# from gevent import monkey

# monkey.patch_all()
from logging import Logger

from config import Config
from database import *
from flask import Flask

logger: Logger = None  # type: ignore

from config import Config

from .extensions import client_manager, configure_logging, cors, socketio

client_events = None
strategy_event = None


def create_app():
    app = Flask(Config.Backtestify.NAME)
    app.config.from_object(Config.Backtestify)

    socketio.init_app(
        app,
        # async_mode="gevent_uwsgi",
        cors_allowed_origins="*",
        client_manager=client_manager,
    )
    cors.init_app(app)
    global logger
    logger = configure_logging(app)

    # Register blueprints
    from .strategy_events import StrategyEvents

    global strategy_event
    strategy_event = StrategyEvents(socketio)
    strategy_event.register_events()

    from .routes import api as api_blueprint

    app.register_blueprint(api_blueprint)

    return app
