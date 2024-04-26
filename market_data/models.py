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
