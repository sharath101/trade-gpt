from ..order_manager import Order
from .broker import Broker


class VirtualBroker(Broker):
    def __init__(self):
        self.commision = 0.03
        self.commission_limit = 20
        pass

    def place_order(self, order: Order):
        pass

    def calculate_commission(self, value):
        return min(self.commision * value, self.commission_limit)
