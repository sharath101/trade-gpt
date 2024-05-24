import json
from typing import List

from api import app, logger
from database import db


class StrategyBook(db.Model):
    # Primary Key
    id: int = db.Column(db.Integer, primary_key=True)

    # Strategy name
    strategy_name: str = db.Column(db.Text, nullable=False)

    # Strategy class
    folder_loc: str = db.Column(db.Text, nullable=False)

    # indicator list
    indicators: str = db.Column(db.Text, nullable=False)

    # description
    description = db.Column(db.String(200), nullable=False)

    # creation date
    created_at = db.Column(
        db.DateTime, nullable=False, default=db.func.current_timestamp()
    )

    def __repr__(self) -> str:
        return f"StrategyBook(strategy_name={self.strategy_name}, indicators={self.indicators})"

    def __init__(self, **strategy):
        self.strategy_name = strategy.get("strategy_name", None)
        self.folder_loc = strategy.get("folder_loc", None)
        self.indicators = json.dumps(strategy.get("indicators", {}))
        self.description = strategy.get("description", "")

    def save(self) -> None:
        try:
            with app.app_context():
                db.session.add(self)
                db.session.commit()
        except Exception as e:
            logger.error(f"Error while saving Strategy: {e}")
            raise f"Error while saving Strategy: {e}"

    @staticmethod
    def save_all(api_keys: List["StrategyBook"]) -> None:
        try:
            with app.app_context():
                for api_key in api_keys:
                    db.session.add(api_key)
                db.session.commit()
        except Exception as e:
            logger.error(f"Error while saving all Strategy: {e}")

    def delete(self) -> None:
        try:
            with app.app_context():
                if self.id:
                    db.session.delete(self)
                    db.session.commit()
        except Exception as e:
            logger.error(f"Error while deleting Strategy: {e}")

    @staticmethod
    def delete_all(api_keys: List["StrategyBook"]) -> None:
        try:
            with app.app_context():
                for api_key in api_keys:
                    if api_key.id:
                        db.session.delete(api_key)
                db.session.commit()
        except Exception as e:
            logger.error(f"Error while deleting all VirtualOrderBook {e}")

    @staticmethod
    def filter(**filters) -> List["StrategyBook"]:
        try:
            with app.app_context():
                return StrategyBook.query.filter_by(**filters).all()
        except Exception as e:
            logger.error(f"Error while filtering Strategy: {e}")

    @staticmethod
    def get_all() -> List["StrategyBook"]:
        try:
            with app.app_context():
                return StrategyBook.query.all()
        except Exception as e:
            logger.error(f"Error while getting all Strategy: {e}")

    @staticmethod
    def get_first(**filters) -> "StrategyBook":
        try:
            with app.app_context():
                return StrategyBook.query.filter_by(**filters).first()
        except Exception as e:
            logger.error(f"Error while getting first Strategy: {e}")
