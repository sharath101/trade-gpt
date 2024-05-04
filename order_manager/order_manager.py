from datetime import time, datetime
from secrets import token_hex
from typing import Dict, List
import logging as logger

from brokers import VirtualBroker
from baseclasses import Broker
from database import OrderBook
from strategy import StrategyManager
from strategy import EngulfingStrategy, MACDStrategy, Strategy
from dataclass import Order
from baseclasses import OrderManager as OMBase


class OrderManager(OMBase):
    """The OrderManager class is responsible for managing the orders for different symbols,
    across different brokers. Simulated P&L will ba calculated in VirtualBroker"""

    def __init__(self, symbols, balance=20000, backtesting=False):
        """Initializes the OrderManager with the given symbols and candle interval.
        Different symbols can have different strategies. This will be initialized here.
        """

        self.symbols: Dict[str, StrategyManager] = {}
        strategies: List[Strategy] = [MACDStrategy()]
        symbol_balance = balance
        for symbol in symbols:
            self.symbols[symbol] = StrategyManager(
                symbol, strategies, symbol_balance, backtesting
            )
        self.backtesting = backtesting
        if backtesting:
            self._open_positions: List[OrderBook] = []

        self.brokers: List[Broker] = [VirtualBroker(self, balance)]

    def next(self, symbol: str, current_price: float, timestamp: datetime, volume: int):
        """This method is called for each new data point on each symbol.
        It runs the strategies for each symbol"""

        assert self.one_position_per_symbol()
        if symbol in self.symbols:
            order: Order = self.symbols[symbol].run_strategies(
                symbol, current_price, timestamp, volume
            )
            if order is not None:
                order.symbol = symbol
                order.exchange = "NSE_EQ"
                self.place_order(order)

        self.analyse(current_price, timestamp)

    @property
    def open_positions(self) -> List[OrderBook]:
        if self.backtesting:
            return self._open_positions
        else:
            return OrderBook.filter(position_status="OPEN")

    @open_positions.setter
    def open_positions(self, value: List[OrderBook] | OrderBook) -> None:
        if type(value) == OrderBook:
            if self.backtesting:
                if value.position_status == "OPEN":
                    self._open_positions.append(value)
            else:
                value.save()

        elif type(value) == List[OrderBook]:
            if self.backtesting:
                self._open_positions = []
                for order in value:
                    if order.position_status == "OPEN":
                        self._open_positions.append(order)
            else:
                OrderBook.save_all(value)

    def place_order(self, order: Order):
        tag = token_hex(9)
        order = OrderBook(
            correlation_id=tag,
            symbol=order.symbol,
            exchange=order.exchange or "NSE_EQ",
            quantity=order.quantity,
            price=order.price,
            trigger_price=order.trigger_price,
            transaction_type=order.transaction_type,
            order_type=order.order_type or "LIMIT",
            product_type=order.product_type or "INTRADAY",
            order_status="TRANSIT",
            position_status="OPEN",
            bo_takeprofit=order.bo_takeprofit,
            bo_stoploss=order.bo_stoploss,
            buy_price=order.price if order.transaction_type == "BUY" else None,
            sell_price=None if order.transaction_type == "BUY" else order.price,
        )

        symbol_orders = [
            position
            for position in self.open_positions
            if position.symbol == order.symbol
        ]
        assert len(symbol_orders) <= 1
        if len(symbol_orders) == 0:
            self.open_positions = order
            for broker in self.brokers:
                broker.place_order(order)
        elif order.transaction_type != symbol_orders[0].transaction_type:
            self.close_position(symbol_orders[0], order.price)

    def analyse(self, current_price: float, current_time: time):
        open_positions: List[OrderBook] = self.open_positions
        market_closing_threshold = time(15, 20, 0)
        if current_time > market_closing_threshold:
            self.close_all_positions(open_positions, current_price)
            self.open_positions = open_positions
            return

        if self.backtesting:
            for broker in self.brokers:
                if broker.__class__.__name__ == "VirtualBroker":
                    broker.analyse(current_price)

    def close_all_positions(self, open_positions: List[OrderBook], current_price):
        for position in open_positions:
            self.close_position(position, current_price)

    def close_position(self, position: OrderBook, closing_price: float):
        self.symbols[position.symbol].closed()
        position.position_status = "CLOSED"

        if position.order_status != "TRADED":
            position.order_status = "CANCELLED"
            position.position_status = "CLOSED"
            return

        if position.transaction_type == "BUY":
            position.sell_price = closing_price
        else:
            position.buy_price = closing_price

        new_order = OrderBook(
            correlation_id=position.correlation_id + "_close",
            symbol=position.symbol,
            exchange=position.exchange,
            quantity=position.quantity,
            price=closing_price,
            trigger_price=0,
            transaction_type=("SELL" if position.transaction_type == "BUY" else "BUY"),
            order_type="LIMIT",
            product_type="INTRADAY",
            position_status="CLOSED",
            buy_price=(
                position.buy_price
                if position.transaction_type == "BUY"
                else closing_price
            ),
            sell_price=(
                closing_price
                if position.transaction_type == "BUY"
                else position.sell_price
            ),
        )
        for broker in self.brokers:
            broker.place_order(new_order)

    def one_position_per_symbol(self):
        symbol_set = set()
        for position in self.open_positions:
            if position.symbol in symbol_set:
                return False
            symbol_set.add(position.symbol)
        return True
