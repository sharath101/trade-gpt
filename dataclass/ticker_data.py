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
