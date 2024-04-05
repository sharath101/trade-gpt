from market_feed import DhanMarketFeed
from dotenv import load_dotenv
load_dotenv()

def analyser(data):
    print(data)


marketFeed = DhanMarketFeed(analyser)
marketFeed.connect()
