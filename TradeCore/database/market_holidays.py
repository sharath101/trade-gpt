from typing import Any, Dict, List

from sqlalchemy import Column, Date, Integer, String

from . import Base, logger, session


class MarketHolidays(Base):
    __tablename__ = "market_holidays"

    id: int = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    exchange: int = Column(String(100), nullable=False)

    def __repr__(self) -> str:
        return f"MarketHolidays(date={self.date}, exchange={self.exchange})"

    def save(self) -> None:
        try:
            session.add(self)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error while saving MarketHolidays: {e}")

    @staticmethod
    def save_all(api_keys: List["MarketHolidays"]) -> None:
        try:
            session.bulk_save_objects(api_keys)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error while saving all MarketHolidays: {e}")

    def delete(self) -> None:
        try:
            session.delete(self)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error while deleting MarketHolidays: {e}")

    @staticmethod
    def delete_all(api_keys: List["MarketHolidays"]) -> None:
        try:
            for api_key in api_keys:
                session.delete(api_key)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error while deleting all MarketHolidays: {e}")

    @staticmethod
    def filter(**filters: Dict[str, Any]) -> List["MarketHolidays"]:
        try:
            return session.query(MarketHolidays).filter_by(**filters).all()
        except Exception as e:
            logger.error(f"Error while filtering MarketHolidays: {e}")
            return []

    @staticmethod
    def get_all() -> List["MarketHolidays"]:
        try:
            return session.query(MarketHolidays).all()
        except Exception as e:
            logger.error(f"Error while getting all MarketHolidays: {e}")
            return []

    @staticmethod
    def get_first(**filters: Dict[str, Any]) -> "MarketHolidays":
        try:
            return session.query(MarketHolidays).filter_by(**filters).first()
        except Exception as e:
            logger.error(f"Error while getting first MarketHolidays: {e}")
            return None
