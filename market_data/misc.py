from .models import APIKey
from datetime import datetime, timedelta


async def analyser(data):
    print(data)


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
    print(len(api_keys))
    for api_key in api_keys:
        if api_key["platform"] == platform:
            if api_key["expiry"] is not None:
                current_time = datetime.now()
                time_later = current_time + timedelta(hours=23)
                if current_time < time_later:
                    return {"key": api_key["key"], "secret": api_key["secret"]}
    else:
        return False
