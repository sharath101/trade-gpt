from dhanhq import marketfeed
from .template import Template
from market_data.models import MarketDepthData, MarketQuoteData, MarketTickerData
from market_data.constants import DHAN_INSTRUMENTS


class DhanMarketFeed(Template):
    def __init__(self, analyser):
        super().__init__(analyser)
        self._access_token = None
        self._client_id = None
        self._feed = None
        self._instruments = []
        self._subscription_code = 15  # Subscription code for Ticker

    def set_api_key(self, key, client_id):
        self._access_token = key
        self._client_id = client_id

    async def connect(self):
        self.disconnect_request = False
        self._feed = marketfeed.DhanFeed(
            self._client_id,
            self._access_token,
            self._instruments,
            self._subscription_code,
            on_message=self.parse,
        )
        await self._feed.connect()

    @property
    def instruments(self):
        return self._instruments

    @instruments.setter
    def instruments(self, instruments):
        """Pass the list of all symbols to be subscribed to the market feed"""
        self._instruments = []
        for instrument in instruments:
            if instrument not in DHAN_INSTRUMENTS["symbol"]:
                return
            else:
                index = DHAN_INSTRUMENTS["symbol"].index(instrument)
                security_id = DHAN_INSTRUMENTS["security_id"][index]
                if DHAN_INSTRUMENTS["exchange_segment"][index] == "NSE":
                    exc = marketfeed.NSE
                else:
                    exc = marketfeed.BSE
                self._instruments.append((exc, security_id))
        return

    async def parse(self, instance, data):
        if data:
            if self._subscription_code == marketfeed.Ticker:
                if "security_id" in data and "LTP" in data and "LTT" in data:
                    symbol = DHAN_INSTRUMENTS["symbol"][
                        DHAN_INSTRUMENTS["security_id"].index(str(data["security_id"]))
                    ]
                    exc = DHAN_INSTRUMENTS["exchange_segment"][
                        DHAN_INSTRUMENTS["security_id"].index(str(data["security_id"]))
                    ]
                    marketData = MarketTickerData(symbol, data["LTP"], data["LTT"], exc)
                    await self.analyser(marketData)

            if self._subscription_code == marketfeed.Quote:
                if "security_id" in data:
                    quoteData = MarketQuoteData()
                    quoteData.exchange_segment = data["exchange_segment"]
                    quoteData.security_id = data["security_id"]
                    quoteData.LTP = data["LTP"]
                    quoteData.LTQ = data["LTQ"]
                    quoteData.LTT = data["LTT"]
                    quoteData.avg_price = data["avg_price"]
                    quoteData.volume = data["volume"]
                    quoteData.total_sell_quantity = data["total_sell_quantity"]
                    quoteData.total_buy_quantity = data["total_buy_quantity"]
                    quoteData.open = data["open"]
                    quoteData.close = data["close"]
                    quoteData.high = data["high"]
                    quoteData.low = data["low"]

                    await self.analyser(quoteData)

            if self._subscription_code == marketfeed.Depth:
                if "security_id" in data:
                    depthData = MarketDepthData()
                    depthData.exchange_segment = data["exchange_segment"]
                    depthData.security_id = data["security_id"]
                    depthData.LTP = data["LTP"]
                    depthData.bid_quantity = []
                    depthData.ask_quantity = []
                    depthData.bid_price = []
                    depthData.ask_price = []
                    depthData.bid_orders = []
                    depthData.ask_orders = []

                    for orderbook in data["depth"]:
                        depthData.bid_quantity.append(orderbook["bid_quantity"])
                        depthData.ask_quantity.append(orderbook["ask_quantity"])
                        depthData.bid_price.append(orderbook["bid_price"])
                        depthData.ask_price.append(orderbook["ask_price"])
                        depthData.bid_orders.append(orderbook["bid_orders"])
                        depthData.ask_orders.append(orderbook["ask_orders"])

                    await self.analyser(depthData)
