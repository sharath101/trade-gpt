from database import APIKey
from datetime import datetime, timedelta
from api import logger


def get_access_token(platform):
    try:
        api_keys = APIKey.get_all()
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
                    time_later = current_time + timedelta(hours=8)
                    if api_key["expiry"] > time_later:
                        logger.info(f"API Key used is valid until: {api_key['expiry']}")
                        return {"key": api_key["key"], "secret": api_key["secret"]}
        else:
            return False
    except Exception as e:
        logger.error(f"Error while getting access token: {e}")
        return False
