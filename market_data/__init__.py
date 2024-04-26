from .dhan_market_feed import DhanMarketFeed
from .feed import Feed

marketDataTicker = DhanMarketFeed(analyser=None)
marketDataTicker.subscription_code = 15
marketFeedTicker = Feed(marketDataTicker)
marketDataQuote = DhanMarketFeed(analyser=None)
marketDataQuote.subscription_code = 17
marketFeedQuote = Feed(marketDataQuote)
