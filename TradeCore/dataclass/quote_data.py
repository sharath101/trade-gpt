import datetime
from dataclasses import dataclass
from typing import Optional


@dataclass
class MarketQuoteData:
    symbol: str
    price: float
    timestamp: datetime.datetime
    volume: int
    open: float
    close: float
    high: float
    low: float
    exchange_segment: Optional[str] = None
    quantity: Optional[int] = None
    avg_price: Optional[float] = None
    total_sell_quantity: Optional[int] = None
    total_buy_quantity: Optional[int] = None

    def __repr__(self):
        f_string = f"MarketQuoteData(symbol={self.symbol}, price={self.price}, quantity={self.quantity}, LTT={self.timestamp}, volume={self.volume})"
        return f_string
