from dataclasses import dataclass
import datetime


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
