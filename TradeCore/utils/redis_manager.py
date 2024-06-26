import pickle
from typing import Dict, List

import redis


class RedisManager:
    def __init__(self, host="localhost", port=6379, db=0):
        self.r = redis.Redis(host=host, port=port, db=db)

    def set(self, key, value):
        try:
            byte_value = pickle.dumps(value)
            self.r.set(key, byte_value)
        except Exception as e:
            raise RuntimeError(f"Error setting value in redis: {e}")

    def get(self, key):
        try:
            value_str = self.r.get(key)
            if value_str is not None:
                value = pickle.loads(value_str)
                return value
            else:
                return None
        except Exception as e:
            raise RuntimeError(f"Error getting value from redis: {e}")


class BacktestRedis:
    def __init__(self):
        self._redis_dict: Dict[str, List[dict]] = {}

    def get(self, key):
        try:
            return self._redis_dict[key]
        except KeyError:
            return None

    def set(self, key, value):
        self._redis_dict[key] = value
