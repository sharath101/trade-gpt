from typing import Any, Dict, List

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text, func

from . import Base, logger, session


class StrategyBook(Base):
    __tablename__ = "strategy_book"

    # Primary Key
    id: int = Column(Integer, primary_key=True)

    # Foreign Key to the User table
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Strategy name
    strategy_name: str = Column(Text, nullable=False)

    # Strategy class
    folder_loc: str = Column(Text, nullable=False)

    # indicator list
    indicators: str = Column(JSON, nullable=False)

    # description
    description = Column(String(200), nullable=False)

    # creation date
    created_at = Column(DateTime, nullable=False, default=func.current_timestamp())

    def __repr__(self) -> str:
        return f"StrategyBook(strategy_name={self.strategy_name}, indicators={self.indicators})"

    def __init__(self, **strategy):
        print("hi")
        self.user_id = strategy.get("user_id", None)
        self.strategy_name = strategy.get("strategy_name", None)
        self.folder_loc = strategy.get("folder_loc", None)
        self.indicators = strategy.get("indicators", None)
        self.description = strategy.get("description", "")

    def save(self) -> None:
        try:
            session.add(self)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error while saving StrategyBook: {e}")

    @staticmethod
    def save_all(api_keys: List["StrategyBook"]) -> None:
        try:
            session.bulk_save_objects(api_keys)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error while saving all StrategyBook: {e}")

    def delete(self) -> None:
        try:
            session.delete(self)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error while deleting StrategyBook: {e}")

    @staticmethod
    def delete_all(api_keys: List["StrategyBook"]) -> None:
        try:
            for api_key in api_keys:
                session.delete(api_key)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error while deleting all StrategyBook: {e}")

    @staticmethod
    def filter(**filters: Dict[str, Any]) -> List["StrategyBook"]:
        try:
            return session.query(StrategyBook).filter_by(**filters).all()
        except Exception as e:
            logger.error(f"Error while filtering APIKey: {e}")
            return []

    @staticmethod
    def get_all() -> List["StrategyBook"]:
        try:
            return session.query(StrategyBook).all()
        except Exception as e:
            logger.error(f"Error while getting all StrategyBook: {e}")
            return []

    @staticmethod
    def get_first(**filters: Dict[str, Any]) -> "StrategyBook":
        try:
            return session.query(StrategyBook).filter_by(**filters).first()
        except Exception as e:
            logger.error(f"Error while getting first StrategyBook: {e}")
            return None
