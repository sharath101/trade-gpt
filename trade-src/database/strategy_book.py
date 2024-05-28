import json
from typing import List

from api import app, logger
from database import db


class StrategyBook(db.Model):
    # Primary Key
    id: int = db.Column(db.Integer, primary_key=True)

    # Foreign Key to the User table
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

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
        self.user_id = strategy.get("user_id", None)
        self.strategy_name = strategy.get("strategy_name", None)
        self.folder_loc = strategy.get("folder_loc", None)
        self.indicators = strategy.get("indicators", None)
        self.description = strategy.get("description", "")

    def save(self) -> None:
        try:
            with app.app_context():
                db.session.add(self)
                db.session.commit()
        except Exception as e:
            logger.error(f"Error while saving Strategy: {e}")
            raise RuntimeError(f"Error while saving Strategy: {e}")

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
    def filter(**filters) -> List["StrategyBook"]:
        try:
            with app.app_context():
                return StrategyBook.query.filter_by(**filters).all()
        except Exception as e:
            logger.error(f"Error while filtering Strategy: {e}")

    def to_dict(self):
        return {
            "id": self.id,
            "strategy_name": self.strategy_name,
            "indicators": self.indicators,
            "description": self.description,
        }

    @staticmethod
    def get_all_dict(user_id) -> List["StrategyBook"]:
        try:
            all_strategies = StrategyBook.filter(user_id=user_id)
            strategies_dict = [strategy.to_dict() for strategy in all_strategies]
            return strategies_dict
        except Exception as e:
            raise RuntimeError(f"{e}")

    @staticmethod
    def get_all() -> List["StrategyBook"]:
        try:
            with app.app_context():
                return StrategyBook.query.all()
        except Exception as e:
            logger.error(f"Error while getting all Strategy: {e}")
            raise RuntimeError(f"Error while getting all strategies: {e}")

    @staticmethod
    def get_first(**filters) -> "StrategyBook":
        try:
            with app.app_context():
                return StrategyBook.query.filter_by(**filters).first()
        except Exception as e:
            logger.error(f"Error while getting first Strategy: {e}")
