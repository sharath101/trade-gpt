from typing import Any, Dict, List

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from . import Base, logger, session


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(500), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    name = Column(String, nullable=True)

    def __repr__(self) -> str:
        return f"Users(email={self.email}, name={self.name})"

    def save(self) -> None:
        try:
            session.add(self)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error while saving Users: {e}")

    @staticmethod
    def save_all(api_keys: List["Users"]) -> None:
        try:
            session.bulk_save_objects(api_keys)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error while saving all Users: {e}")

    def delete(self) -> None:
        try:
            session.delete(self)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error while deleting Users: {e}")

    @staticmethod
    def delete_all(api_keys: List["Users"]) -> None:
        try:
            for api_key in api_keys:
                session.delete(api_key)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error while deleting all Users: {e}")

    @staticmethod
    def filter(**filters: Dict[str, Any]) -> List["Users"]:
        try:
            return session.query(Users).filter_by(**filters).all()
        except Exception as e:
            logger.error(f"Error while filtering Users: {e}")
            return []

    @staticmethod
    def get_all() -> List["Users"]:
        try:
            return session.query(Users).all()
        except Exception as e:
            logger.error(f"Error while getting all Users: {e}")
            return []

    @staticmethod
    def get_first(**filters: Dict[str, Any]) -> "Users":
        try:
            return session.query(Users).filter_by(**filters).first()
        except Exception as e:
            logger.error(f"Error while getting first Users: {e}")
            return None
