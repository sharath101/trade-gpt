from typing import Any, Dict, List

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from . import Base, logger, session


class Symbol(Base):
    __tablename__ = "symbol"

    id = Column(Integer, primary_key=True)
    symbol = Column(String(100), nullable=False)
    exchange = Column(String(100), nullable=False)

    def __repr__(self) -> str:
        return f"Symbol(symbol={self.symbol}, exchange={self.exchange})"

    def save(self) -> None:
        try:
            session.add(self)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error while saving Symbol: {e}")

    @staticmethod
    def save_all(api_keys: List["Symbol"]) -> None:
        try:
            session.bulk_save_objects(api_keys)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error while saving all Symbol: {e}")

    def delete(self) -> None:
        try:
            session.delete(self)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error while deleting Symbol: {e}")

    @staticmethod
    def delete_all(api_keys: List["Symbol"]) -> None:
        try:
            for api_key in api_keys:
                session.delete(api_key)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error while deleting all Symbol: {e}")

    @staticmethod
    def filter(**filters: Dict[str, Any]) -> List["Symbol"]:
        try:
            return session.query(Symbol).filter_by(**filters).all()
        except Exception as e:
            logger.error(f"Error while filtering Symbol: {e}")
            return []

    @staticmethod
    def get_all() -> List["Symbol"]:
        try:
            return session.query(Symbol).all()
        except Exception as e:
            logger.error(f"Error while getting all Symbol: {e}")
            return []

    @staticmethod
    def get_first(**filters: Dict[str, Any]) -> "Symbol":
        try:
            return session.query(Symbol).filter_by(**filters).first()
        except Exception as e:
            logger.error(f"Error while getting first Symbol: {e}")
            return None
