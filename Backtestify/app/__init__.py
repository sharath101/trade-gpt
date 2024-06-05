from gevent import monkey

monkey.patch_all()
from logging import Logger

from database import *
from flask import Flask

from .config import Config

redis_instance = None
redis_instance_backtest = None
logger: Logger = None

from .extensions import client_manager, configure_logging, cors, socketio
from .socketio_events import ClientEvents, StrategyEvents

client_events: ClientEvents = None
strategy_events: StrategyEvents = None


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
    from utils import BacktestRedis, RedisManager

    global redis_instance
    redis_instance = RedisManager()
    global redis_instance_backtest
    redis_instance_backtest = BacktestRedis()

    # Register blueprints
    global client_events
    client_events = ClientEvents(socketio)
    client_events.register_events()

    global strategy_events
    strategy_events = StrategyEvents(socketio)
    strategy_events.register_events()

    from .routes import api as api_blueprint

    app.register_blueprint(api_blueprint)

    return app
