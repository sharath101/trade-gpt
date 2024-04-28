from typing import List

from utils import db


class OrderBook(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary key in database
    correlation_id = db.Column(db.String(100), nullable=False)  # Correlation ID
    client_id = db.Column(db.String(100), nullable=False)  # Client ID from the client
    order_id = db.Column(db.String(100), nullable=False)  # Order ID from the broker
    symbol = db.Column(db.String(100), nullable=False)  # Symbol of the stock
    exchange = db.Column(db.String(100), nullable=False)  # Exchange of the stock
    quantity = db.Column(db.Integer, nullable=False)  # Quantity of the stock placed
    price = db.Column(db.Float, nullable=False)  # Price of the order excuted
    transaction_type = db.Column(db.String(100), nullable=False)  # Buy or Sell
    order_type = db.Column(db.String(100), nullable=False)  # Market or Limit
    product_type = db.Column(db.String(100), nullable=False)  # Intraday or Delivery
    status = db.Column(db.String(100), nullable=False)  # Order status
    order_created = db.Column(db.DateTime, nullable=True)  # Order created timestamp
    order_updated = db.Column(db.DateTime, nullable=True)  # Order updated timestamp
    exchange_timestamp = db.Column(db.DateTime, nullable=True)  # Exchange timestamp
    bo_profit_val = db.Column(db.Float, nullable=True)  # Bracket order profit value
    bo_stoploss_val = db.Column(db.Float, nullable=True)  # Bracket order stoploss value
    order_opened = db.Column(db.Boolean, nullable=True)  # Order opened or not

    def __repr__(self):
        return f"Order(order_id={self.order_id}, symbol={self.symbol})"


class OrderBookService:
    def create_order(self, order: OrderBook):
        db.session.add(order)
        db.session.commit()
        return order

    def create_orders(self, orders: List[OrderBook]):
        created_orders = []
        for order in orders:
            db.session.add(order)
            created_orders.append(order)
        db.session.commit()
        return created_orders

    def get_order_by_id(self, order_id):
        return OrderBook.query.get(order_id)

    def update_order(self, order_id, **kwargs):
        order = OrderBook.query.get(order_id)
        if order:
            for key, value in kwargs.items():
                setattr(order, key, value)
            db.session.commit()
            return order
        return None

    def delete_order(self, order_id):
        order = OrderBook.query.get(order_id)
        if order:
            db.session.delete(order)
            db.session.commit()
            return order
        return None
