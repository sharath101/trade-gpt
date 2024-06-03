from datetime import datetime
from typing import Any, Dict, List, Literal

from sqlalchemy import Column, DateTime, Float, Integer, String

from . import Base, logger, session


class OrderBook(Base):
    __tablename__ = "order_book"

    # Primary key in database
    id = Column(Integer, primary_key=True)  # Primary key in database

    # Correlation ID
    correlation_id: str = Column(String(25), nullable=False)

    # Symbol of the stock
    symbol: str = Column(String(20), nullable=False)

    # Exchange of the stock
    exchange: Literal["NSE_EQ"] = Column(String(20), nullable=False, default="NSE_EQ")

    # Quantity of the stock placed
    quantity: int = Column(Integer, nullable=False)

    # Price at which the order is requested to execute
    price: float = Column(Float, nullable=False, default=0.0)

    # Price of the order executed at exchange
    trigger_price: float = Column(Float, nullable=False, default=0.0)

    # Buy price of the stock
    buy_price: float = Column(Float, nullable=True)

    # Sell price of the stock
    sell_price: float = Column(Float, nullable=True)

    # Buy or Sell
    transaction_type: Literal["BUY", "SELL"] = Column(String(100), nullable=False)

    # Order type (MARKET, LIMIT, CO, BO)
    order_type: Literal["MARKET", "LIMIT", "STOP_LOSS", "STOP_LOSS_MARKET"] = Column(
        String(100), nullable=False, default="MARKET"
    )  # Market or Limit

    # Product type (CNC, INTRADAY, STOP_LOSS, STOP_LOSS_MARKET)
    product_type: Literal["CNC", "INTRADAY", "MARGIN", "CO", "BO", "MTF"] = Column(
        String(100), nullable=False, default="INTRADAY"
    )

    # Order status (TRANSIT PENDING REJECTED CANCELLED TRADED EXPIRED)
    order_status: Literal[
        "TRANSIT", "PENDING", "REJECTED", "CANCELLED", "TRADED", "EXPIRED"
    ] = Column(String(100), nullable=False, default="PENDING")

    # Position Status (OPEN CLOSED)
    position_status: Literal["OPENING", "OPEN", "CLOSE", "CLOSING"] = Column(
        String(100), nullable=True, default="OPEN"
    )

    # Position Action (OPEN CLOSE)
    position_action: Literal["OPEN", "CLOSE"] = Column(String(100), nullable=True)

    # Order Creation time
    order_created: datetime = Column(DateTime, nullable=False, default=datetime.now())

    # Bracket order profit value
    bo_takeprofit: float = Column(Float, nullable=True)

    # Bracket order stoploss value
    bo_stoploss: float = Column(Float, nullable=True)

    def __repr__(self) -> str:
        return f"APIKey(key={self.key}, secret={self.secret})"

    def save(self) -> None:
        try:
            session.add(self)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error while saving APIKey: {e}")

    @staticmethod
    def save_all(api_keys: List["OrderBook"]) -> None:
        try:
            session.bulk_save_objects(api_keys)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error while saving all OrderBook: {e}")

    def delete(self) -> None:
        try:
            session.delete(self)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error while deleting OrderBook: {e}")

    @staticmethod
    def delete_all(api_keys: List["OrderBook"]) -> None:
        try:
            for api_key in api_keys:
                session.delete(api_key)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error while deleting all OrderBook: {e}")

    @staticmethod
    def filter(**filters: Dict[str, Any]) -> List["OrderBook"]:
        try:
            return session.query(OrderBook).filter_by(**filters).all()
        except Exception as e:
            logger.error(f"Error while filtering OrderBook: {e}")
            return []

    @staticmethod
    def get_all() -> List["OrderBook"]:
        try:
            return session.query(OrderBook).all()
        except Exception as e:
            logger.error(f"Error while getting all OrderBook: {e}")
            return []

    @staticmethod
    def get_first(**filters: Dict[str, Any]) -> "OrderBook":
        try:
            return session.query(OrderBook).filter_by(**filters).first()
        except Exception as e:
            logger.error(f"Error while getting first OrderBook: {e}")
            return None
