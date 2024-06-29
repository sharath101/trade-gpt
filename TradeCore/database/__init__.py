import logging
import os

from config import Config
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configure logger
logger = logging.getLogger("databases")
logging.basicConfig(level=logging.INFO)

DATABASE_URL = Config.Misc.DATABASE_URI

# Create engine and session
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Create a global session object
session = Session()

Base = declarative_base()

# Import the tables to ensure they are registered with the Base metadata
from .api_key import APIKey
from .dhan_order_book import DhanOrderBook
from .market_holidays import MarketHolidays
from .order_book import OrderBook
from .strategy_book import StrategyBook
from .symbol import Symbol
from .users import Users
from .virtual_order_book import VirtualOrderBook


# Create tables when the module is imported
def create_tables():
    try:
        Base.metadata.create_all(engine)
    except Exception as e:
        logger.error(f"Error while creating tables: {e}")


create_tables()
