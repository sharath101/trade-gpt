import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import jwt
from sqlalchemy import Column, Integer, String

from . import Base, logger, session


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(500), unique=True, nullable=False)
    password = Column(String(100), nullable=True)
    picture = Column(String(200), nullable=True)
    uid = Column(String(100), nullable=True)
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
    def get_first(**filters: Dict[str, Any]) -> Optional["Users"]:
        try:
            return session.query(Users).filter_by(**filters).first()
        except Exception as e:
            logger.error(f"Error while getting first Users: {e}")
            return None

    def encode_auth_token(self, user_id) -> Optional[str]:
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                "exp": datetime.utcnow() + timedelta(days=1, minutes=5),
                "iat": datetime.utcnow(),
                "sub": user_id,
            }
            return jwt.encode(
                payload, os.getenv("SECRET_KEY", "topsecret"), algorithm="HS256"
            )
        except Exception as e:
            return None

    @staticmethod
    def decode_auth_token(auth_token) -> Optional["Users"]:
        """
        Decodes the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(
                auth_token, os.getenv("SECRET_KEY", "topsecret"), algorithms=["HS256"]
            )

            return Users.get_first(id=payload["sub"])
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
