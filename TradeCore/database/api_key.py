from typing import Any, Dict, List

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from . import Base, logger, session


class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True)
    key = Column(String(500), nullable=False)
    secret = Column(String(100), nullable=False)
    expiry = Column(DateTime, nullable=True)
    platform = Column(String(100), nullable=False)
    trading = Column(Boolean, nullable=False, default=True)

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
    def save_all(api_keys: List["APIKey"]) -> None:
        try:
            session.bulk_save_objects(api_keys)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error while saving all APIKeys: {e}")

    def delete(self) -> None:
        try:
            session.delete(self)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error while deleting APIKey: {e}")

    @staticmethod
    def delete_all(api_keys: List["APIKey"]) -> None:
        try:
            for api_key in api_keys:
                session.delete(api_key)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error while deleting all APIKeys: {e}")

    @staticmethod
    def filter(**filters: Dict[str, Any]) -> List["APIKey"]:
        try:
            return session.query(APIKey).filter_by(**filters).all()
        except Exception as e:
            logger.error(f"Error while filtering APIKey: {e}")
            return []

    @staticmethod
    def get_all() -> List["APIKey"]:
        try:
            return session.query(APIKey).all()
        except Exception as e:
            logger.error(f"Error while getting all APIKeys: {e}")
            return []

    @staticmethod
    def get_first(**filters: Dict[str, Any]) -> "APIKey":
        try:
            return session.query(APIKey).filter_by(**filters).first()
        except Exception as e:
            logger.error(f"Error while getting first APIKey: {e}")
            return None
