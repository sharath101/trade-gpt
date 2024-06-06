import logging

from dataclass import Order
from utils.logging import get_logger
from utils.type_dict import MarketData, MarketDataList

from .socket_client import SocketClient
from .strategy_manager import StrategyManager
from .strategy_obj import Strategy

NAME = "StratRun"
logger = get_logger(NAME, logging.DEBUG)
