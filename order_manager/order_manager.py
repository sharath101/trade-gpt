from datetime import datetime, time
from secrets import token_hex
from typing import List

from talipp.ohlcv import OHLCV

from api import logger
from brokers import VirtualBroker
from brokers.broker import Broker
from database.order_book import OrderBook

from .models import Order


class OrderManager:
    def __init__(self, balance, backtesting=False):
        self.backtesting = backtesting
        self.initial_balance = balance
        self.balance = balance
        if backtesting:
            self.open_positions: List[OrderBook] = []
        self.broker: Broker = VirtualBroker()
        self.trade_wins = 0
        self.trade_losses = 0
        self.daily_profit = 0
        self.days = 0
        self.total_profit = 0
        self.total_commission = 0
        self.long_orders = 0
        self.short_orders = 0

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

        updated_open_positions = []
        for position in open_positions:
            updated_open_positions.append(position)
            if position.order_status == "PENDING":
                if (
                    position.transaction_type == "BUY"
                    and current_high >= position.trigger_price
                ) or (
                    position.transaction_type == "SELL"
                    and current_low <= position.trigger_price
                ):
                    if not self.open_position(position):
                        updated_open_positions.pop()

            elif position.order_status == "TRADED":
                if position.transaction_type == "BUY":
                    # Issue where both If statements are executed
                    if current_high >= position.bo_takeprofit:
                        self.close_position(position, position.bo_takeprofit)
                        updated_open_positions.pop()
                    elif current_low <= position.bo_stoploss:
                        self.close_position(position, position.bo_stoploss)
                        updated_open_positions.pop()

                if position.transaction_type == "SELL":
                    if current_low <= position.bo_takeprofit:
                        self.close_position(position, position.bo_takeprofit)
                        updated_open_positions.pop()
                    elif current_high >= position.bo_stoploss:
                        self.close_position(position, position.bo_stoploss)
                        updated_open_positions.pop()

        if self.backtesting:
            self.open_positions = updated_open_positions
        else:
            OrderBook.save_all(open_positions)

    def close_all_positions(self, open_positions: List[OrderBook], current_price):
        for position in open_positions:
            # self.broker.close_order()
            self.close_position(position, current_price)

        self.days += 1
        self.total_profit += self.daily_profit
        logger.info(
            f"\nDay {self.days} : Day Profit={self.daily_profit}  ||  Total Profit={self.total_profit}   ||   Net Profit={self.total_profit-self.total_commission}   ||   Balance={self.balance}   ||   long={self.long_orders}   ||   short={self.short_orders}\n"
        )
        self.daily_profit = 0

    def close_position(self, position: OrderBook, closing_price):
        if position.order_status != "TRADED":
            position.order_status = "EXPIRED"
            position.position_status = "CLOSED"
            return

        position.position_status = "CLOSED"
        self.balance += position.trigger_price * position.quantity

        if position.transaction_type == "BUY":
            delta = (closing_price - position.trigger_price) * position.quantity
            self.daily_profit += delta
            self.balance += delta
        if position.transaction_type == "SELL":
            delta = (position.trigger_price - closing_price) * position.quantity
            self.daily_profit += delta
            self.balance += delta

        if delta > 0:
            self.trade_wins += 1
        else:
            self.trade_losses += 1

        logger.debug(
            f"Closing {position.transaction_type} Position (delta: {delta}) (Balance: {self.balance}) (profit: {self.total_profit})"
        )

    def open_position(self, position: OrderBook) -> bool:
        commission = self.broker.calculate_commission(position.trigger_price)
        total_cost = position.trigger_price * position.quantity + commission
        if total_cost > self.balance:
            logger.warning(f"Insufficient balance for order: {position}")
            position.order_status = "CANCELLED"
            return False

        self.balance -= total_cost
        self.total_commission += commission
        position.order_status = "TRADED"
        if position.transaction_type == "BUY":
            self.long_orders += 1
        else:
            self.short_orders += 1
        logger.debug(
            f"{position.transaction_type} Order Placed at cost {total_cost} (Balance: {self.balance})"
        )
        return True
