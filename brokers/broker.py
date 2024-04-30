from abc import ABC, abstractmethod


class Broker(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def place_order(self):
        pass

    @abstractmethod
    def calculate_brokerage(self):
        pass
