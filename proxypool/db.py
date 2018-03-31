# -*- coding: utf-8 -*-
import redis
from proxypool.config import HOST, PORT, PASSWORD


class RedisClient(object):
    def __init__(self, host=HOST, port=PORT):
        if PASSWORD:
            self._db = redis.Redis(host=host, port=port, password=PASSWORD)
        else:
            self._db = redis.Redis(host=host, port=port)

    def get(self, count=1):
        proxies = self._db.lrange('proxies', 0, count - 1)
        self._db.ltrim('proxies', count, -1)
        return proxies

    def put(self, proxy):
        self._db.rpush('proxies', proxy)

    def pop(self):
        try:
            return self._db.rpop('proxies').decode('utf-8')
        except Exception:
            return None

    def flush(self):
        self._db.flushall()
