import asyncio
from datetime import datetime, time
from secrets import token_hex
from typing import Dict, List

from talipp.ohlcv import OHLCV

from api import logger
from brokers import VirtualBroker
from brokers.broker import Broker
from database.order_book import OrderBook
from strategy import EngulfingStrategy, MACDStrategy, Strategy, StrategyManager

from .models import Order, Stats


class OrderManager:
    def __init__(self, symbols, candle_interval, balance, backtesting=False):
        self.symbols: Dict[str, StrategyManager] = {}
        strategies: List[Strategy] = [MACDStrategy(), EngulfingStrategy()]
        for symbol in symbols:
            self.symbols[symbol] = StrategyManager(
                symbol, candle_interval, strategies, backtesting
            )
        self.backtesting = backtesting
        self.initial_balance = balance
        self.balance = balance
        if backtesting:
            self.open_positions: List[OrderBook] = []
        self.broker: Broker = VirtualBroker()
        self.stats = Stats()

    def next(self, data: OHLCV):
        assert self.one_position_per_symbol()
        for symbol in self.symbols:
            order: Order = self.symbols[symbol].run_strategies(data)
            if order is not None:
                self.place_order(order)

        self.analyse(data)

    def place_order(self, order: Order):
        tag = token_hex(5)
        order = OrderBook(
            correlation_id=tag,
            symbol=order.symbol,
            exchange=order.exchange or "NSE",
            quantity=order.quantity,
            price=order.price,
            trigger_price=order.trigger_price,
            transaction_type=order.transaction_type,
            order_type=order.order_type or "LIMIT",
            product_type=order.product_type,
            order_status="PENDING",
            position_status="OPEN",
            bo_takeprofit=order.bo_takeprofit,
            bo_stoploss=order.bo_stoploss,
        )
        self.broker.place_order(order)
        symbol_orders = [
            position
            for position in self.open_positions
            if position.symbol == order.symbol
        ]
        assert len(symbol_orders) <= 1
        if len(symbol_orders) == 0:
            self.open_positions.append(order)
        elif order.transaction_type != symbol_orders[0].transaction_type:
            self.close_position(symbol_orders[0], order.price)
            self.open_positions.append(order)

    def analyse(self, data: OHLCV):
        if self.backtesting:
            open_positions: List[OrderBook] = self.open_positions
        else:
            open_positions: List[OrderBook] = OrderBook.filter(position_status="OPEN")
        current_price = data.close
        current_high = data.high
        current_low = data.low
        market_closing_threshold = time(15, 20, 0)
        current_time = data.time.time()
        if current_time > market_closing_threshold:
            self.close_all_positions(open_positions, current_price)
            if self.backtesting:
                self.open_positions = []
            else:
                OrderBook.save_all(open_positions)
            return

        for position in open_positions:
            if position.order_status == "PENDING":
                if (
                    position.transaction_type == "BUY"
                    and current_high >= position.trigger_price
                ) or (
                    position.transaction_type == "SELL"
                    and current_low <= position.trigger_price
                ):
                    self.open_position(position)
            elif position.order_status == "TRADED":
                if position.transaction_type == "BUY":
                    # Issue where both If statements are executed
                    if current_high >= position.bo_takeprofit:
                        self.close_position(position, position.bo_takeprofit)
                    elif current_low <= position.bo_stoploss:
                        self.close_position(position, position.bo_stoploss)
                if position.transaction_type == "SELL":
                    if current_low <= position.bo_takeprofit:
                        self.close_position(position, position.bo_takeprofit)
                    elif current_high >= position.bo_stoploss:
                        self.close_position(position, position.bo_stoploss)
        if self.backtesting:
            self.open_positions = [
                position
                for position in self.open_positions
                if position.position_status == "OPEN"
            ]
        else:
            OrderBook.save_all(open_positions)

    def close_all_positions(self, open_positions: List[OrderBook], current_price):
        for position in open_positions:
            # self.broker.close_order()
            self.close_position(position, current_price)

        self.stats.days += 1
        self.stats.total_profit += self.stats.daily_profit
        logger.info(f"{self.stats} Balance={self.balance}")
        self.stats.daily_profit = 0

    def close_position(self, position: OrderBook, closing_price):
        self.symbols[position.symbol].closed()
        self.stats.total_closed += 1
        position.position_status = "CLOSED"

        if position.order_status != "TRADED":
            position.order_status = "EXPIRED"
            position.position_status = "CLOSED"
            logger.debug(
                f"Closing UNTRADED Position (delta: 0) (Balance: {self.balance}) (profit: {self.stats.total_profit})"
            )
            return

        position.buy_price = (
            position.trigger_price
            if position.transaction_type == "BUY"
            else closing_price
        )
        position.sell_price = (
            closing_price
            if position.transaction_type == "SELL"
            else position.trigger_price
        )

        commission = self.broker.calculate_brokerage(position)
        self.stats.total_commission += commission
        self.balance += position.trigger_price * position.quantity - commission
        position.order_status = "EXPIRED"

        if position.transaction_type == "BUY":
            delta = (closing_price - position.trigger_price) * position.quantity
            self.stats.daily_profit += delta
            self.balance += delta
        if position.transaction_type == "SELL":
            delta = (position.trigger_price - closing_price) * position.quantity
            self.stats.daily_profit += delta
            self.balance += delta

        if delta > 0:
            self.stats.trade_wins += 1
        else:
            self.stats.trade_losses += 1

        logger.debug(
            f"Closing {position.transaction_type} Position at price {closing_price} (delta: {delta}) (Balance: {self.balance}) (profit: {self.stats.total_profit})"
        )

    def open_position(self, position: OrderBook) -> bool:
        total_cost = position.trigger_price * position.quantity
        if total_cost > self.balance:
            logger.debug(f"Insufficient balance for order: {position}")
            self.symbols[position.symbol].cancelled()
            position.order_status = "CANCELLED"
            position.position_status = "CLOSED"
            return False

        self.stats.total_opened += 1
        self.balance -= total_cost
        position.order_status = "TRADED"
        self.symbols[position.symbol].traded()
        if position.transaction_type == "BUY":
            self.stats.long_orders += 1
        else:
            self.stats.short_orders += 1
        logger.debug(
            f"{position.transaction_type} Order Placed at price {position.trigger_price},  cost {total_cost} (Balance: {self.balance})"
        )
        return True

    def one_position_per_symbol(self):
        symbol_set = set()
        for position in self.open_positions:
            if position.symbol in symbol_set:
                return False
            symbol_set.add(position.symbol)
        return True
