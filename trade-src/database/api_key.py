from api import app, logger
from typing import List
from database import db


class APIKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(500), nullable=False)
    secret = db.Column(db.String(100), nullable=False)
    expiry = db.Column(db.DateTime, nullable=True)
    platform = db.Column(db.String(100), nullable=False)
    trading = db.Column(db.Boolean, nullable=False, default=True)

    def __repr__(self) -> str:
        return f"APIKey(key={self.key}, secret={self.secret})"

    def save(self) -> None:
        try:
            with app.app_context():
                db.session.add(self)
                db.session.commit()
        except Exception as e:
            logger.error(f"Error while saving APIKey: {e}")

    @staticmethod
    def save_all(api_keys: List["APIKey"]) -> None:
        try:
            with app.app_context():
                for api_key in api_keys:
                    db.session.add(api_key)
                db.session.commit()
        except Exception as e:
            logger.error(f"Error while saving all APIKeys: {e}")

    def delete(self) -> None:
        try:
            with app.app_context():
                if self.id:
                    db.session.delete(self)
                    db.session.commit()
        except Exception as e:
            logger.error(f"Error while deleting APIKey: {e}")

    @staticmethod
    def delete_all(api_keys: List["APIKey"]) -> None:
        try:
            with app.app_context():
                for api_key in api_keys:
                    if api_key.id:
                        db.session.delete(api_key)
                db.session.commit()
        except Exception as e:
            logger.error(f"Error while deleting all APIKeys {e}")

    @staticmethod
    def filter(**filters) -> List["APIKey"]:
        try:
            with app.app_context():
                return APIKey.query.filter_by(**filters).all()
        except Exception as e:
            logger.error(f"Error while filtering APIKey: {e}")

    @staticmethod
    def get_all() -> List["APIKey"]:
        try:
            with app.app_context():
                return APIKey.query.all()
        except Exception as e:
            logger.error(f"Error while getting all APIKeys: {e}")

    @staticmethod
    def get_first(**filters) -> "APIKey":
        try:
            with app.app_context():
                return APIKey.query.filter_by(**filters).first()
        except Exception as e:
            logger.error(f"Error while getting first APIKey: {e}")
