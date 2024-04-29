from abc import ABC, abstractmethod
from secrets import token_hex
from typing import List

from talipp.ohlcv import OHLCV

from brokers import DhanBroker
from brokers.broker import Broker
from database import OrderBook, order_book_service

from .models import Order


class OrderManager:
    def __init__(self, balance, backtesting=False):
        self.initial_balance = balance
        self.balance = balance
        if backtesting:
            self.open_positions = List[OrderBook]
        self.broker: Broker = DhanBroker()
        self.trade_wins = 0
        self.trade_losses = 0

    def place_order(self, order: Order):
        tag = token_hex(5)
        order = OrderBook(
            correlation_id=tag,
            symbol=order.symbol,
            exchange=order.exchange,
            quantity=order.quantity,
            price=order.price,
            trigger_price=order.trigger_price,
            transaction_type=order.transaction_type,
            order_type=order.order_type,
            product_type=order.product_type,
            order_status="TRADED" if order.trigger_price == order.price else "PENDING",
            position_status="OPEN",
            bo_takeprofit=order.bo_profit_val,
            bo_stoploss=order.bo_stoploss_val,
        )
        self.simulate(order)
        self.broker.place_order(order)

    def simulate(self, order: Order):
        cost = order.price * order.quantity
        total_cost = cost + self.broker.calculate_commission(cost)
        if total_cost > self.balance:
            print(f"Insufficient balance for order: {order}")
            return
        print(f"Order Placed: {order}")
        self.balance -= total_cost
        self.open_positions.append(order)

    # def analyse(self, data: OHLCV):
    #     if self.backtesting:
    #         open_positions: List[OrderBook] = self.open_positions
    #     else:
    #         open_positions: List[OrderBook] = order_book_service.get_order_by_filter(
    #             position_status="OPEN"
    #         )

    #     current_price = data.close
    #     current_high = data.high
    #     current_low = data.low
    #     for position in open_positions:
    #         if position.order_status == "PENDING":
    #             if (
    #                 position.transaction_type == 'BUY'
    #                 and current_high >= position.trigger_price
    #             ) or (
    #                 position.transaction_type == 'SELL'
    #                 and current_low <= position.trigger_price
    #             ):
    #                 position.order_status = "TRADED"

    #         if position.order_status == 'TRADED':
    #             if position.transaction_type == 'BUY':
    #                 if current_high >= position.bo_takeprofit:
    #                     self.trade_wins += 1
    #                     self.balance += (position.bo_takeprofit - position.trigger_price) * position.quantity
    #             if position.transaction_type == 'SELL':
