import json
from typing import Dict

from lib.redis import RedisClient


class MockRedisClient(RedisClient):
    def __init__(self) -> None:
        self._d = {}

    def set(self, k, v):
        self._d[k] = json.dumps(v)

    def get(self, k) -> Dict:
        return json.loads(self._d[k])
