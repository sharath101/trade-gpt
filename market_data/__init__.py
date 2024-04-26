from .dhan_market_feed import DhanMarketFeed
from utils.processor import Processor
from .misc import analyser


marketDataQuote = DhanMarketFeed(analyser=analyser)
marketDataQuote.subscription_code = 17
marketFeedQuote = Processor(marketDataQuote)
