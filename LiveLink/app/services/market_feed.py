import struct
import time
from abc import ABC, abstractmethod

import websockets
from app import logger
from dhanhq import DhanFeed, marketfeed
from dhanhq.marketfeed import DhanSDKHelper


class MarketFeed(ABC):

    @abstractmethod
    def set_credentials(self, symbols):
        pass

    @abstractmethod
    async def connect_feed(self):
        pass

    @abstractmethod
    def parse(self, data):
        pass
