from api import app, logger
from typing import List
import jwt
from datetime import datetime, timedelta

from database import db


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(500), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"Users(email={self.email}, name={self.name})"

    def save(self) -> None:
        try:
            with app.app_context():
                db.session.add(self)
                db.session.commit()
        except Exception as e:
            logger.error(f"Error while saving Users: {e}")

    @staticmethod
    def save_all(api_keys: List["Users"]) -> None:
        try:
            with app.app_context():
                for api_key in api_keys:
                    db.session.add(api_key)
                db.session.commit()
        except Exception as e:
            logger.error(f"Error while saving all Users: {e}")

    def delete(self) -> None:
        try:
            with app.app_context():
                if self.id:
                    db.session.delete(self)
                    db.session.commit()
        except Exception as e:
            logger.error(f"Error while deleting Users: {e}")

    @staticmethod
    def delete_all(api_keys: List["Users"]) -> None:
        try:
            with app.app_context():
                for api_key in api_keys:
                    if api_key.id:
                        db.session.delete(api_key)
                db.session.commit()
        except Exception as e:
            logger.error(f"Error while deleting all Users {e}")

    @staticmethod
    def filter(**filters) -> List["Users"]:
        try:
            with app.app_context():
                return Users.query.filter_by(**filters).all()
        except Exception as e:
            logger.error(f"Error while filtering Users: {e}")

    @staticmethod
    def get_all() -> List["Users"]:
        try:
            with app.app_context():
                return Users.query.all()
        except Exception as e:
            logger.error(f"Error while getting all Users: {e}")

    @staticmethod
    def get_first(**filters) -> "Users":
        try:
            with app.app_context():
                return Users.query.filter_by(**filters).first()
        except Exception as e:
            logger.error(f"Error while getting first Users: {e}")

    def encode_auth_token(self, user_id):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                'exp': datetime.now() + timedelta(days=0, seconds=5),
                'iat': datetime.now(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        """
        Decodes the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'))
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False
