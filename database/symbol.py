from database import db
from api import app, logger
from typing import List


class Symbol(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(100), nullable=False)
    exchange = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"Symbol(symbol={self.symbol}, exchange={self.exchange})"

    def save(self):
        try:
            with app.app_context():
                db.session.add(self)
                db.session.commit()
        except Exception as e:
            logger.error(f"Error while saving APIKey: {e}")

    @staticmethod
    def save_all(api_keys: List["Symbol"]):
        try:
            with app.app_context():
                for api_key in api_keys:
                    db.session.add(api_key)
                db.session.commit()
        except Exception as e:
            logger.error(f"Error while saving all Symbols: {e}")

    def delete(self):
        try:
            with app.app_context():
                if self.id:
                    db.session.delete(self)
                    db.session.commit()
        except Exception as e:
            logger.error(f"Error while deleting Symbol: {e}")

    @staticmethod
    def delete_all(api_keys: List["Symbol"]):
        try:
            with app.app_context():
                for api_key in api_keys:
                    if api_key.id:
                        db.session.delete(api_key)
                db.session.commit()
        except Exception as e:
            logger.error(f"Error while deleting all Symbols {e}")

    @staticmethod
    def filter(**filters):
        try:
            with app.app_context():
                return Symbol.query.filter_by(**filters).all()
        except Exception as e:
            logger.error(f"Error while filtering Symbol: {e}")
