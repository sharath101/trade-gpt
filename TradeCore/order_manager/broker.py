from abc import ABC, abstractmethod

from dataclass import Order


class Broker(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def place_order(self, order: Order):
        pass

    @abstractmethod
    def calculate_brokerage(self):
        pass

    @abstractmethod
    def cancel_order(self, position):
        pass

    @abstractmethod
    def analyse(self, current_price, current_time, symbol):
        pass
