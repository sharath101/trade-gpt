class MarketData:
    def __init__(self):
        self.symbol = None
        self.price = None
        self.timestamp = None
        self.volume = None

    def __repr__(self):
        return f"TickerData(symbol={self.symbol}, price={self.price}, volume={self.volume}, timestamp={self.timestamp})"