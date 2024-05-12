from typing import List, Literal
from datetime import datetime
from api import app, logger
from database import db
from database import OrderBook


class VirtualOrderBook(db.Model):
    # Primary Key
    id: int = db.Column(db.Integer, primary_key=True)

    # Correlation ID
    correlation_id: str = db.Column(db.String(25), nullable=False)

    # Client ID from the client
    client_id: str = db.Column(db.String(100), nullable=True)

    # Order ID from the broker
    order_id: str = db.Column(db.String(100), nullable=True)

    # Symbol of the stock
    symbol: str = db.Column(db.String(20), nullable=False)

    # Exchange of the stock
    exchange: Literal["NSE_EQ"] = db.Column(
        db.String(20), nullable=False, default="NSE_EQ"
    )

    # Quantity of the stock placed
    quantity: int = db.Column(db.Integer, nullable=False)

    # Price at which the order is requested to execute
    price: float = db.Column(db.Float, nullable=False, default=0.0)

    # Price at which the order is triggered
    trigger_price: float = db.Column(db.Float, nullable=True, default=0.0)

    # Transaction type (BUY or SELL)
    transaction_type: Literal["BUY", "SELL"] = db.Column(db.String(4), nullable=False)

    # Order type (MARKET, LIMIT, CO, BO)
    order_type: Literal["MARKET", "LIMIT", "STOP_LOSS", "STOP_LOSS_MARKET"] = db.Column(
        db.String(16), nullable=False, default="MARKET"
    )

    # Product type (CNC, INTRADAY, STOP_LOSS, STOP_LOSS_MARKET)
    product_type: Literal["CNC", "INTRADAY", "MARGIN", "CO", "BO", "MTF"] = db.Column(
        db.String(8), nullable=False, default="INTRADAY"
    )

    # Order status (TRANSIT PENDING REJECTED CANCELLED TRADED EXPIRED)
    order_status: Literal[
        "TRANSIT",
        "PENDING",
        "REJECTED",
        "CANCELLED",
        "TRADED",
        "EXPIRED",
        "WIN",
        "LOSS",
        "CLOSED",
    ] = db.Column(db.String(9), nullable=False, default="TRANSIT")

    # Order created timestamp
    order_created: datetime = db.Column(db.DateTime, nullable=True)

    # Order updated timestamp
    order_updated: datetime = db.Column(db.DateTime, nullable=True)

    # Order executed timestamp
    exchange_timestamp: datetime = db.Column(db.DateTime, nullable=True)

    # Bracket order profit value
    bo_takeprofit: float = db.Column(db.Float, nullable=True)

    # Bracket order stop loss value
    bo_stoploss: float = db.Column(db.Float, nullable=True)

    def __repr__(self) -> str:
        return f"Order(order_id={self.order_id}, symbol={self.symbol})"

    def save(self) -> None:
        try:
            with app.app_context():
                db.session.add(self)
                db.session.commit()
        except Exception as e:
            logger.error(f"Error while saving VirtualOrderBook: {e}")

    @staticmethod
    def save_all(api_keys: List["VirtualOrderBook"]) -> None:
        try:
            with app.app_context():
                for api_key in api_keys:
                    db.session.add(api_key)
                db.session.commit()
        except Exception as e:
            logger.error(f"Error while saving all VirtualOrderBook: {e}")

    def delete(self) -> None:
        try:
            with app.app_context():
                if self.id:
                    db.session.delete(self)
                    db.session.commit()
        except Exception as e:
            logger.error(f"Error while deleting VirtualOrderBook: {e}")

    @staticmethod
    def delete_all(api_keys: List["VirtualOrderBook"]) -> None:
        try:
            with app.app_context():
                for api_key in api_keys:
                    if api_key.id:
                        db.session.delete(api_key)
                db.session.commit()
        except Exception as e:
            logger.error(f"Error while deleting all VirtualOrderBook {e}")

    @staticmethod
    def filter(**filters) -> List["VirtualOrderBook"]:
        try:
            with app.app_context():
                return VirtualOrderBook.query.filter_by(**filters).all()
        except Exception as e:
            logger.error(f"Error while filtering VirtualOrderBook: {e}")

    @staticmethod
    def get_all() -> List["VirtualOrderBook"]:
        try:
            with app.app_context():
                return VirtualOrderBook.query.all()
        except Exception as e:
            logger.error(f"Error while getting all VirtualOrderBook: {e}")

    @staticmethod
    def get_first(**filters) -> "VirtualOrderBook":
        try:
            with app.app_context():
                return VirtualOrderBook.query.filter_by(**filters).first()
        except Exception as e:
            logger.error(f"Error while getting first VirtualOrderBook: {e}")

    @staticmethod
    def create_object(order: OrderBook) -> "VirtualOrderBook":
        """Creates a DhanOrderBook object from an Order object."""

        return VirtualOrderBook(
            correlation_id=order.correlation_id,
            symbol=order.symbol,
            exchange=order.exchange if order.exchange in ["NSE_EQ"] else "NSE_EQ",
            quantity=order.quantity if order.quantity > 0 else 1,
            price=order.price,
            trigger_price=order.trigger_price,
            transaction_type=order.transaction_type,
            order_type=order.order_type,
            product_type=order.product_type,
            bo_takeprofit=order.bo_takeprofit,
            bo_stoploss=order.bo_stoploss,
            order_created=order.order_created,
        )
