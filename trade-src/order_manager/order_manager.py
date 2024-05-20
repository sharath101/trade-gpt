from datetime import datetime, time
from secrets import token_hex
from typing import Dict, List

from api import logger
from baseclasses import Broker
from baseclasses import OrderManager as OMBase
from brokers import VirtualBroker
from database import OrderBook
from dataclass import Order
from strategy import EngulfingStrategy, MACDStrategy, Strategy, StrategyManager


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
                symbol, symbol_balance, strategies, backtesting
            )
        self.backtesting = backtesting
        if backtesting:
            self._open_positions: List[OrderBook] = []

        self.brokers: List[Broker] = [VirtualBroker(self, balance)]

    def next(self, symbol: str, current_price: float, timestamp: datetime, volume: int):
        """This method is called for each new data point on each symbol.
        It runs the strategies for each symbol"""

        market_closing_threshold = time(15, 15, 0)
        if timestamp.time() < market_closing_threshold:
            """Market is open, so we will run the strategies for each symbol"""

            assert self.one_position_per_symbol()
            if symbol in self.symbols:
                order: Order = self.symbols[symbol].run_strategies(
                    symbol, current_price, timestamp, volume
                )
                if order is not None:
                    order.symbol = symbol
                    order.exchange = "NSE_EQ"
                    self.place_order(order)

        self.analyse(current_price, timestamp, symbol)

    @property
    def open_positions(self) -> List[OrderBook]:
        open_positions = []
        if self.backtesting:
            all_positions = self._open_positions
        else:
            all_positions = OrderBook.get_all()
        for position in all_positions:
            if (
                position.position_status != "CLOSE"
                and position.position_action == "OPEN"
            ):

                """Condition to filter active orders intended to open a position"""

                open_positions.append(position)
        return open_positions

    @open_positions.setter
    def open_positions(self, value: List[OrderBook] | OrderBook) -> None:
        if isinstance(value, OrderBook):
            if self.backtesting:
                for order in self._open_positions:
                    if order.correlation_id == value.correlation_id:
                        self._open_positions.remove(order)
                        self._open_positions.append(value)
                        break
                else:
                    self._open_positions.append(value)
            else:
                value.save()

        elif isinstance(value, list):
            if self.backtesting:
                self._open_positions = []
                for order in value:
                    self._open_positions.append(order)
            else:
                OrderBook.save_all(value)

    @property
    def closing_positions(self):
        closing_positions = []
        if self.backtesting:
            all_positions = self._open_positions
        else:
            all_positions = OrderBook.get_all()
        for position in all_positions:
            if (
                position.position_status == "CLOSING"
                and position.position_action == "CLOSE"
            ):

                """Condition to filter active orders intended to close a position"""

                closing_positions.append(position)
        return closing_positions

    @property
    def all_positions(self) -> List[OrderBook]:
        open_positions = []
        if self.backtesting:
            all_positions = self._open_positions
        else:
            all_positions = OrderBook.get_all()
        for position in all_positions:
            if position.position_status != "CLOSE":

                """Condition to filter active orders"""

                open_positions.append(position)
        return open_positions

    def place_order(self, order: Order):
        tag = token_hex(9)
        order: OrderBook = OrderBook(
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
            position_status="OPENING",
            position_action="OPEN",
            order_created=order.timestamp,
            bo_takeprofit=order.bo_takeprofit,
            bo_stoploss=order.bo_stoploss,
            buy_price=order.price if order.transaction_type == "BUY" else None,
            sell_price=None if order.transaction_type == "BUY" else order.price,
        )

        # List of open positions for the symbol (OPENING, OPEN, CLOSING)
        symbol_orders = [
            position
            for position in self.open_positions
            if position.symbol == order.symbol
        ]

        assert len(symbol_orders) <= 1
        if len(symbol_orders) == 0:
            for broker in self.brokers:
                broker.place_order(order)
            self.open_positions = order
        elif order.transaction_type != symbol_orders[0].transaction_type:
            self.close_position(symbol_orders[0], order.price, order.order_created)

    def analyse(self, current_price: float, current_time: datetime, symbol: str):
        open_positions: List[OrderBook] = self.all_positions
        market_closing_threshold = time(15, 20, 0)
        if current_time.time() > market_closing_threshold:
            self.close_all_positions(open_positions, current_price, current_time)
            return

        if self.backtesting:
            for broker in self.brokers:
                broker.analyse(current_price, current_time, symbol)

    def close_all_positions(self, open_positions: List[OrderBook], current_price, current_time):
        for position in open_positions:
            self.close_position(position, current_price, current_time, immediate=True)
            self.open_positions = position

    def close_position(
        self, position: OrderBook, closing_price: float, current_time: datetime,immediate: bool = True
    ):

        if position.position_status == "CLOSING":
            """This implies that the position is already in closing state, so no need to close again.
            An order is already placed with correlation_id suffix of _close to close this position,
            so it will be closed automatically when the order is executed. The analyse method will
            update the position status to CLOSED when that order is executed."""
            return

       

        if position.order_status == "TRANSIT" or position.order_status == "PENDING":
            """This imples that the order is not yet traded, so we will cancel the order.
            The position status at this point must be OPENING, we will update it to CLOSED"""

            try:
                assert position.position_status == "OPENING"
            except AssertionError:
                logger.warning(
                    f"Position status is not OPENING for position {position.correlation_id}"
                )

            for broker in self.brokers:
                broker.cancel_order(position)

            """Note: Currently, not checking if the order
            was successfully cancelled by broker"""

            position.order_status = "CANCELLED"
            position.position_status = "CLOSE"
            self.symbols[position.symbol].closed()
            return

        elif position.order_status != "TRADED":
            """If position is not traded, then it is either EXPIRED, REJECTED,
            CANCELLED, because previously we checked for TRANSIT and PENDING status,
            in all the above cases, the position status must be CLOSE. This should be
            implemented in analyse method, but just to be sure, we are updating again."""

            position.position_status = "CLOSE"
            self.symbols[position.symbol].closed()
            return
        
        self.symbols[position.symbol].closing()
        position.position_status = "CLOSING"
        
        """ If the position is traded, we will close the order by placing a new order
        of opposite transaction type. If the immediate flag is set, then the order
        will be placed as MARKET order, otherwise it will be placed as LIMIT order
        at requested price."""

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
            order_type="LIMIT" if not immediate else "MARKET",
            order_status="TRANSIT",
            product_type="INTRADAY",
            position_status="CLOSING",
            position_action="CLOSE",
            order_created=current_time,
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

        self.open_positions = new_order

    def one_position_per_symbol(self):
        symbol_set = set()
        for position in self.open_positions:
            if position.symbol in symbol_set:
                return False
            symbol_set.add(position.symbol)
        return True



