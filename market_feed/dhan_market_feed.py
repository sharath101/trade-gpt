import os
import asyncio
from dhanhq import marketfeed
from market_feed.template import Template
from models.market_data import MarketTickerData


class DhanMarketFeed(Template) :
    def __init__(self, analyser, instruments, subscription_code):
        super().__init__(analyser)
        self.access_token = os.getenv("ACCESS_TOKEN")
        self.client_id = os.getenv("CLIENT_ID")
        self.instruments = instruments
        self.subscription_code = subscription_code

    async def connect(self):
        feed = marketfeed.DhanFeed(self.client_id,
            self.access_token,
            self.instruments,
            self.subscription_code,
            #on_connect=on_connect,
            on_message=self.parse
        )
        await feed.connect()

    async def parse(self, instance, data):
        if data:
            if self.subscription_code == 15:
                if 'security_id' in data and 'LTP' in data and 'LTT' in data:
                    marketData = MarketTickerData()
                    marketData.symbol = data['security_id']
                    marketData.price = data['LTP']
                    marketData.timestamp = data['LTT']
                    self.analyser(marketData)
        
        if self.subscription_code == 17:
            self.analyser(data)

        if self.subscription_code == 19:
            self.analyser(data)
