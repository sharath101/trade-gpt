from typing import List

from api import app
from database import db


class OrderBook(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary key in database
    correlation_id = db.Column(db.String(100), nullable=False)  # Correlation ID
    client_id = db.Column(db.String(100), nullable=False)  # Client ID from the client
    order_id = db.Column(db.String(100), nullable=False)  # Order ID from the broker
    symbol = db.Column(db.String(100), nullable=False)  # Symbol of the stock
    exchange = db.Column(db.String(100), nullable=False)  # Exchange of the stock
    quantity = db.Column(db.Integer, nullable=False)  # Quantity of the stock placed
    price = db.Column(db.Float, nullable=False)  # Price when order was placed
    trigger_price = db.Column(db.Float, nullable=False)  # Price of the order excuted
    transaction_type = db.Column(db.String(100), nullable=False)  # Buy or Sell
    order_type = db.Column(db.String(100), nullable=False)  # Market or Limit
    product_type = db.Column(db.String(100), nullable=False)  # Intraday or Delivery
    order_status = db.Column(
        db.String(100), nullable=False
    )  # Order status (TRANSIT PENDING REJECTED CANCELLED TRADED EXPIRED)
    position_status = db.Column(
        db.String(100), nullable=True
    )  # Position Status (OPEN CLOSED)
    order_created = db.Column(db.DateTime, nullable=True)  # Order created timestamp
    order_updated = db.Column(db.DateTime, nullable=True)  # Order updated timestamp
    exchange_timestamp = db.Column(db.DateTime, nullable=True)  # Exchange timestamp
    bo_takeprofit = db.Column(db.Float, nullable=True)  # Bracket order profit value
    bo_stoploss = db.Column(db.Float, nullable=True)  # Bracket order stoploss value

    def __repr__(self):
        return f"Order(order_id={self.order_id}, symbol={self.symbol})"

    def save(self):
        with app.app_context():
            db.session.add(self)
            db.session.commit()

    @staticmethod
    def save_all(orders: List["OrderBook"]):
        with app.app_context():
            for order in orders:
                db.session.add(order)
            db.session.commit()

    def delete(self):
        with app.app_context():
            if self.id:
                db.session.delete(self)
            db.session.commit()

    @staticmethod
    def delete_all(orders: List["OrderBook"]):
        with app.app_context():
            for order in orders:
                db.session.delete(order)
            db.session.commit()

    @staticmethod
    def filter(**filters):
        with app.app_context():
            return OrderBook.query.filter_by(**filters).all()
