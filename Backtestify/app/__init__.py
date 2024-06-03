from gevent import monkey

monkey.patch_all()
import sys
from logging import Logger

from flask import Flask

from .config import Config
from .extensions import client_manager, configure_logging, cors, socketio

redis_instance = None
redis_instance_backtest = None

logger: Logger = None


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    python_path = app.config["PYTHONPATH"]
    if python_path and python_path not in sys.path:
        sys.path.append(python_path)

    socketio.init_app(
        app,
        async_mode="gevent",
        cors_allowed_origins="*",
        client_manager=client_manager,
    )
    cors.init_app(app)
    logger = configure_logging(app)
    from utils import BacktestRedis, RedisManager

    redis_instance = RedisManager()
    redis_instance_backtest = BacktestRedis()

    # Register blueprints
    from .routes import api as api_blueprint

    app.register_blueprint(api_blueprint)

    from .socketio_events import register_client_events, register_strategy_events

    register_strategy_events(socketio)
    register_client_events(socketio)

    return app
