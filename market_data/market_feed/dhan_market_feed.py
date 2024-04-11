from dhanhq import marketfeed
from .template import Template
from market_data.models import MarketDepthData, MarketQuoteData, MarketTickerData


class DhanMarketFeed(Template):
    def __init__(self, analyser, instruments, subscription_code, key, client_id):
        super().__init__(analyser)
        self.access_token = key
        self.client_id = client_id
        self.instruments = instruments
        self.subscription_code = subscription_code
        self.task = False

    async def connect(self):
        self.disconnect_request = False
        feed = marketfeed.DhanFeed(
            self.client_id,
            self.access_token,
            self.instruments,
            self.subscription_code,
            on_message=self.parse,
        )
        await feed.connect()

    async def parse(self, instance, data):
        if data:
            if self.subscription_code == marketfeed.Ticker:
                if "security_id" in data and "LTP" in data and "LTT" in data:
                    marketData = MarketTickerData()
                    marketData.symbol = data["security_id"]
                    marketData.price = data["LTP"]
                    marketData.timestamp = data["LTT"]

                    await self.analyser(marketData)

            if self.subscription_code == marketfeed.Quote:
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

            if self.subscription_code == marketfeed.Depth:
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
