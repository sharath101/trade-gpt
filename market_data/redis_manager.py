import pickle
import redis


class RedisManager:
    def __init__(self, host="localhost", port=6379, db=0):
        self.r = redis.Redis(host=host, port=port, db=db)

    def set(self, key, value):
        byte_value = pickle.dumps(value)
        self.r.set(key, byte_value)

    def get(self, key):
        value_str = self.r.get(key)
        if value_str is not None:
            value = pickle.loads(value_str)
            return value
        else:
            return None


redis_instance = RedisManager()
