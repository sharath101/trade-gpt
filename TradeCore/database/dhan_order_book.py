from datetime import datetime
from typing import Any, Dict, List, Literal

from sqlalchemy import Column, DateTime, Float, Integer, String

from . import Base, logger, session
from .order_book import OrderBook


class DhanOrderBook(Base):
    __tablename__ = "dhan_order_book"

    id: int = Column(Integer, primary_key=True)

    # Correlation ID
    correlation_id: str = Column(String(25), nullable=False)

    # Client ID from the client
    client_id: str = Column(String(100), nullable=False)

    # Order ID from the broker
    order_id: str = Column(String(100), nullable=False)

    # Symbol of the stock
    symbol: str = Column(String(20), nullable=False)

    # Exchange of the stock
    exchange: Literal["NSE_EQ"] = Column(String(20), nullable=False, default="NSE_EQ")

    # Quantity of the stock placed
    quantity: int = Column(Integer, nullable=False)

    # Price at which the order is requested to execute
    price: float = Column(Float, nullable=False, default=0.0)

    # Price at which the order is triggered
    trigger_price: float = Column(Float, nullable=True, default=0.0)

    # Transaction type (BUY or SELL)
    transaction_type: Literal["BUY", "SELL"] = Column(String(4), nullable=False)

    # Order type (MARKET, LIMIT, CO, BO)
    order_type: Literal["MARKET", "LIMIT", "STOP_LOSS", "STOP_LOSS_MARKET"] = Column(
        String(16), nullable=False, default="MARKET"
    )

    # Product type (CNC, INTRADAY, STOP_LOSS, STOP_LOSS_MARKET)
    product_type: Literal["CNC", "INTRADAY", "MARGIN", "CO", "BO", "MTF"] = Column(
        String(8), nullable=False, default="INTRADAY"
    )

    # Order status (TRANSIT PENDING REJECTED CANCELLED TRADED EXPIRED)
    order_status: Literal[
        "TRANSIT", "PENDING", "REJECTED", "CANCELLED", "TRADED", "EXPIRED"
    ] = Column(String(9), nullable=False, default="TRANSIT")

    # Order created timestamp
    order_created: datetime = Column(DateTime, nullable=True)

    # Order updated timestamp
    order_updated: datetime = Column(DateTime, nullable=True)

    # Order executed timestamp
    exchange_timestamp: datetime = Column(DateTime, nullable=True)

    # Bracket order profit value
    bo_takeprofit: float = Column(Float, nullable=True)

    # Bracket order stop loss value
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
    def save_all(api_keys: List["DhanOrderBook"]) -> None:
        try:
            session.bulk_save_objects(api_keys)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error while saving all DhanOrderBook: {e}")

    def delete(self) -> None:
        try:
            session.delete(self)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error while deleting DhanOrderBook: {e}")

    @staticmethod
    def delete_all(api_keys: List["DhanOrderBook"]) -> None:
        try:
            for api_key in api_keys:
                session.delete(api_key)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error while deleting all DhanOrderBook: {e}")

    @staticmethod
    def filter(**filters: Dict[str, Any]) -> List["DhanOrderBook"]:
        try:
            return session.query(DhanOrderBook).filter_by(**filters).all()
        except Exception as e:
            logger.error(f"Error while filtering APIKey: {e}")
            return []

    @staticmethod
    def get_all() -> List["DhanOrderBook"]:
        try:
            return session.query(DhanOrderBook).all()
        except Exception as e:
            logger.error(f"Error while getting all DhanOrderBook: {e}")
            return []

    @staticmethod
    def get_first(**filters: Dict[str, Any]) -> "DhanOrderBook":
        try:
            return session.query(DhanOrderBook).filter_by(**filters).first()
        except Exception as e:
            logger.error(f"Error while getting first DhanOrderBook: {e}")

    @staticmethod
    def create_object(order: OrderBook) -> "DhanOrderBook":
        """Creates a DhanOrderBook object from an Order object."""

        return DhanOrderBook(
            correlation_id=order.correlation_id,
            symbol=order.symbol,
            exchange=order.exchange if order.exchange in ["NSE_EQ"] else "NSE_EQ",
            quantity=order.quantity if order.quantity > 0 else 1,
            price=order.price,
            trigger_price=order.trigger_price,
            transaction_type=order.transaction_type,
            order_type=(
                "STOP_LOSS_MARKET" if order.product_type in ["BO", "CO"] else "LIMIT"
            ),
            product_type=order.product_type,
            bo_takeprofit=order.bo_takeprofit,
            bo_stoploss=order.bo_stoploss,
        )
