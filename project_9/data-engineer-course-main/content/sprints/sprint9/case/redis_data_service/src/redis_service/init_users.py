import json
from datetime import datetime
from typing import Dict

from redis_service.redis_client import RedisClient


class UserLoader:
    _USERS_FILE_PATH = 'redis_service/data/users.json'

    def __init__(self, redis_client: RedisClient) -> None:
        self._redis_client = redis_client

    def load_users(self):
        users_dict = []

        with open(self._USERS_FILE_PATH) as f:
            users_dict = json.load(f)

        for user in users_dict:
            user['update_ts_utc'] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            self._redis_client.set(user['_id'], user)

        return {
            "load_result": "Гости загружены.",
            "result_key": "GbV@t5UDqcQ@HdR8Nj"
        }

    def get_user(self, user_id: str) -> Dict:
        return self._redis_client.get(user_id)
