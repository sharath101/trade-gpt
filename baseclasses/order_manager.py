from datetime import time, datetime
from typing import List

from database.order_book import OrderBook
from dataclass import Order


class OrderManager:

    def __init__(self):
        pass

    def next(self, symbol: str, current_price: float, timestamp: datetime, volume: int):
        pass

    @property
    def open_positions(self):
        pass

    @open_positions.setter
    def open_positions(self, value: List[OrderBook] | OrderBook):
        pass

    def place_order(self, order: Order):
        pass

    def analyse(self, current_price: float, current_time: time):
        pass

    def close_all_positions(self, open_positions: List[OrderBook], current_price):
        pass

    def close_position(self, position: OrderBook, closing_price: float):
        pass

    def one_position_per_symbol(self):
        pass
