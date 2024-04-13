from .models import APIKey
from .candles import CandleManager
from datetime import datetime, timedelta
from .models import MarketQuoteData


async def analyser(data: MarketQuoteData):
    candle1m = CandleManager(1)
    candle1m.process_tick(data.timestamp, data.price, data.quantity, data.symbol)


def get_access_token(platform):
    api_keys = APIKey.query.all()
    api_keys = [
        {
            "key": key.key,
            "secret": key.secret,
            "expiry": key.expiry,
            "platform": key.platform,
        }
        for key in api_keys
    ]
    for api_key in api_keys:
        if api_key["platform"] == platform:
            if api_key["expiry"] is not None:
                current_time = datetime.now()
                time_later = current_time + timedelta(hours=23)
                if current_time < time_later:
                    return {"key": api_key["key"], "secret": api_key["secret"]}
    else:
        return False
