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


class OrderBookService:
    def create_order(self, order: OrderBook):
        with app.app_context():
            db.session.add(order)
            db.session.commit()
        return order

    def create_orders(self, orders: List[OrderBook]):
        with app.app_context():
            created_orders = []
            for order in orders:
                db.session.add(order)
                created_orders.append(order)
            db.session.commit()
        return created_orders

    def get_order_by_id(self, id: int):
        with app.app_context():
            return OrderBook.query.get(id)

    def get_order_by_filter(self, **filters):
        with app.app_context():
            orders = OrderBook.query.filter_by(**filters).all()
            return orders

    def update_order(self, id: int, **kwargs):
        with app.app_context():
            order = OrderBook.query.get(id)
            if order:
                for key, value in kwargs.items():
                    setattr(order, key, value)
                db.session.commit()
                return order
            return None

    def delete_order(self, id: int):
        with app.app_context():
            order = OrderBook.query.get(id)
            if order:
                db.session.delete(order)
                db.session.commit()
                return order
            return None


order_book_service = OrderBookService()
