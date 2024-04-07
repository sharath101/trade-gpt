class MarketTickerData:
    def __init__(self):
        self.symbol = None
        self.price = None
        self.timestamp = None
        self.volume = None

    def __repr__(self):
        return f"TickerData(symbol={self.symbol}, price={self.price}, volume={self.volume}, timestamp={self.timestamp})"
    

class MarketQuoteData:
    def __init__(self):
        self.exchange_segment=None
        self.security_id=None
        self.LTP=None
        self.LTQ=None
        self.LTT=None
        self.avg_price=None
        self.volume=None
        self.total_sell_quantity=None
        self.total_buy_quantity=None
        self.open=None
        self.close=None
        self.high=None
        self.low=None

    def __repr__(self):
        return f"QouteData(symbol={self.security_id}, price={self.avg_price}, volume={self.volume}, timestamp={self.LTT})"
    

class MarketDepthData:
    def __init__(self):
        self.exchange_segment=None
        self.security_id=None
        self.LTP=None
        self.bid_quantity=[None]
        self.ask_quantity=[None]
        self.bid_price=[None]
        self.ask_price=[None]
        self.bid_orders=[None]
        self.ask_orders=[None]
     

    def __repr__(self):
        return f"DepthData(symbol={self.security_id}, price={self.LTP}, volume={self.volume}, numbers={len(self.bid_quantity)})"