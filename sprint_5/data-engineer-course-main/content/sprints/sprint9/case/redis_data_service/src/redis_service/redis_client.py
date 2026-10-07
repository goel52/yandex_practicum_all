import json
from typing import Dict, Optional, Tuple

import redis


class RedisClient:
    def __init__(self, host: str, port: int, password: str) -> None:
        self._client = redis.StrictRedis(
            host=host,
            port=port,
            password=password,
            ssl=True,
            ssl_ca_certs="redis_service/crt/YandexInternalRootCA.crt")

    def set(self, k, v):
        self._client.set(k, json.dumps(v, ensure_ascii=False))

    def get(self, k):
        restaurant: str = self._client.get(k).decode("utf-8")  # type: ignore
        return json.loads(restaurant)


class RedisClientFactory:
    @staticmethod
    def from_json(json: Dict) -> Tuple[Optional[RedisClient], Optional[str]]:
        if 'redis' not in json:
            return (None, "No redis field found in request.")

        redis: Dict = json['redis']
        if 'host' not in redis:
            return (None, "No host field found in redis block.")

        if 'port' not in redis:
            return (None, "No port field found in redis block.")

        if 'password' not in redis:
            return (None, "No password field found in redis block.")

        redis_client = RedisClient(redis['host'], int(redis['port']), redis['password'])
        return (redis_client, None)
