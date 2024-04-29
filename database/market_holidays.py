from database import db
from api import app, logger
from typing import List


class MarketHolidays(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String, nullable=False)
    exchange = db.Column(db.String(100), nullable=False)

    def __repr__(self) -> str:
        return f"MarketHolidays(date={self.date}, exchange={self.exchange})"

    def save(self) -> None:
        try:
            with app.app_context():
                db.session.add(self)
                db.session.commit()
        except Exception as e:
            logger.error(f"Error while saving APIKey: {e}")

    @staticmethod
    def save_all(api_keys: List["MarketHolidays"]) -> None:
        try:
            with app.app_context():
                for api_key in api_keys:
                    db.session.add(api_key)
                db.session.commit()
        except Exception as e:
            logger.error(f"Error while saving all MarketHolidays: {e}")

    def delete(self) -> None:
        try:
            with app.app_context():
                if self.id:
                    db.session.delete(self)
                    db.session.commit()
        except Exception as e:
            logger.error(f"Error while deleting MarketHolidays: {e}")

    @staticmethod
    def delete_all(api_keys: List["MarketHolidays"]) -> None:
        try:
            with app.app_context():
                for api_key in api_keys:
                    if api_key.id:
                        db.session.delete(api_key)
                db.session.commit()
        except Exception as e:
            logger.error(f"Error while deleting all MarketHolidays {e}")

    @staticmethod
    def filter(**filters) -> List["MarketHolidays"]:
        try:
            with app.app_context():
                return MarketHolidays.query.filter_by(**filters).all()
        except Exception as e:
            logger.error(f"Error while filtering MarketHolidays: {e}")

    @staticmethod
    def get_all() -> List["MarketHolidays"]:
        try:
            with app.app_context():
                return MarketHolidays.query.all()
        except Exception as e:
            logger.error(f"Error while getting all MarketHolidays: {e}")

    @staticmethod
    def get_first(**filters) -> "MarketHolidays":
        try:
            with app.app_context():
                return MarketHolidays.query.filter_by(**filters).first()
        except Exception as e:
            logger.error(f"Error while getting first MarketHolidays: {e}")
