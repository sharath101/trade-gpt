from market_data import db
from dataclasses import dataclass
import datetime


@dataclass
class MarketTickerData:
    symbol: str
    price: float
    timestamp: datetime.datetime
    exchange: str

    def __repr__(self):
        timestamp = self.timestamp.strftime("%H:%M:%S")
        f_string = f"MarketTickerData(symbol={self.symbol}, price={self.price}, timestamp={timestamp}, exchange={self.exchange})"
        return f_string


@dataclass
class MarketQuoteData:
    exchange_segment: str
    symbol: str
    price: float
    quantity: int
    timestamp: datetime.datetime
    avg_price: float
    volume: int
    total_sell_quantity: int
    total_buy_quantity: int
    open: float
    close: float
    high: float
    low: float

    def __repr__(self):
        f_string = f"MarketQuoteData(symbol={self.symbol}, LTP={self.price}, LTQ={self.quantity}, LTT={self.timestamp}, exchange={self.exchange_segment})"
        return f_string


@dataclass
class MarketDepthData:
    exchange_segment: str
    security_id: str
    LTP: float
    bid_quantity: list
    ask_quantity: list
    bid_price: list
    ask_price: list
    bid_orders: list
    ask_orders: list


class APIKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(500), nullable=False)
    secret = db.Column(db.String(100), nullable=False)
    expiry = db.Column(db.DateTime, nullable=True)
    platform = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"APIKey(key={self.key}, secret={self.secret})"


class Symbol(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(100), nullable=False)
    exchange = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"Symbol(symbol={self.symbol}, exchange={self.exchange})"
