from abc import ABC, abstractmethod
from typing import Callable, List


class MarketFeed(ABC):

    @abstractmethod
    def set_credentials(self, symbols: List[str], analyseanalyse: Callable):
        pass

    @abstractmethod
    async def connect_feed(self):
        pass

    @abstractmethod
    def parse(self, data):
        pass
