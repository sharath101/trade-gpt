from .candles import CandleManager
from .models import MarketQuoteData


async def analyser(data: MarketQuoteData):
    candle1m = CandleManager(1)
    candle1m.process_tick(data.timestamp, data.price, data.quantity, data.symbol)
