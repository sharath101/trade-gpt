from typing import List, Literal
from datetime import datetime
from api import app, logger
from database import db


class OrderBook(db.Model):
    # Primary key in database
    id = db.Column(db.Integer, primary_key=True)  # Primary key in database

    # Correlation ID
    correlation_id: str = db.Column(db.String(25), nullable=False)

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

    # Price of the order executed at exchange
    trigger_price: float = db.Column(db.Float, nullable=False, default=0.0)

    # Buy price of the stock
    buy_price: float = db.Column(db.Float, nullable=True)

    # Sell price of the stock
    sell_price: float = db.Column(db.Float, nullable=True)

    # Buy or Sell
    transaction_type: Literal["BUY", "SELL"] = db.Column(db.String(100), nullable=False)

    # Order type (MARKET, LIMIT, CO, BO)
    order_type: Literal["MARKET", "LIMIT", "STOP_LOSS", "STOP_LOSS_MARKET"] = db.Column(
        db.String(100), nullable=False, default="MARKET"
    )  # Market or Limit

    # Product type (CNC, INTRADAY, STOP_LOSS, STOP_LOSS_MARKET)
    product_type: Literal["CNC", "INTRADAY", "MARGIN", "CO", "BO", "MTF"] = db.Column(
        db.String(100), nullable=False, default="INTRADAY"
    )

    # Order status (TRANSIT PENDING REJECTED CANCELLED TRADED EXPIRED)
    order_status: Literal[
        "TRANSIT", "PENDING", "REJECTED", "CANCELLED", "TRADED", "EXPIRED"
    ] = db.Column(db.String(100), nullable=False, default="PENDING")

    # Position Status (OPEN CLOSED)
    position_status: Literal["OPENNIG", "OPEN", "CLOSE", "CLOSING"] = db.Column(
        db.String(100), nullable=True, default="OPEN"
    )

    # Position Action (OPEN CLOSE)
    position_action: Literal["OPEN", "CLOSE"] = db.Column(db.String(100), nullable=True)

    # Order Creation time
    order_created: datetime = db.Column(
        db.DateTime, nullable=False, default=datetime.now()
    )

    # Bracket order profit value
    bo_takeprofit: float = db.Column(db.Float, nullable=True)

    # Bracket order stoploss value
    bo_stoploss: float = db.Column(db.Float, nullable=True)

    def __repr__(self) -> str:
        return f"Order(order_id={self.order_id}, symbol={self.symbol})"

    def save(self) -> None:
        try:
            with app.app_context():
                db.session.add(self)
                db.session.commit()
        except Exception as e:
            logger.error(f"Error while saving OrderBook: {e}")

    @staticmethod
    def save_all(api_keys: List["OrderBook"]) -> None:
        try:
            with app.app_context():
                for api_key in api_keys:
                    db.session.add(api_key)
                db.session.commit()
        except Exception as e:
            logger.error(f"Error while saving all OrderBooks: {e}")

    def delete(self) -> None:
        try:
            with app.app_context():
                if self.id:
                    db.session.delete(self)
                    db.session.commit()
        except Exception as e:
            logger.error(f"Error while deleting OrderBook: {e}")

    @staticmethod
    def delete_all(api_keys: List["OrderBook"]) -> None:
        try:
            with app.app_context():
                for api_key in api_keys:
                    if api_key.id:
                        db.session.delete(api_key)
                db.session.commit()
        except Exception as e:
            logger.error(f"Error while deleting all OrderBooks {e}")

    @staticmethod
    def filter(**filters) -> List["OrderBook"]:
        try:
            with app.app_context():
                return OrderBook.query.filter_by(**filters).all()
        except Exception as e:
            logger.error(f"Error while filtering OrderBook: {e}")

    @staticmethod
    def get_all() -> List["OrderBook"]:
        try:
            with app.app_context():
                return OrderBook.query.all()
        except Exception as e:
            logger.error(f"Error while getting all OrderBooks: {e}")

    @staticmethod
    def get_first(**filters) -> "OrderBook":
        try:
            with app.app_context():
                return OrderBook.query.filter_by(**filters).first()
        except Exception as e:
            logger.error(f"Error while getting first OrderBook: {e}")
