import json
from datetime import datetime
from typing import Dict

from redis_service.redis_client import RedisClient


class RestaurantLoader:
    _RESTAURANTS_FILE_PATH = 'redis_service/data/restaurants.json'

    def __init__(self, redis_client: RedisClient) -> None:
        self._redis_client = redis_client

    def load_restaurants(self):
        rest_dict = []

        with open(self._RESTAURANTS_FILE_PATH) as f:
            rest_dict = json.load(f)

        for restaurant in rest_dict:
            restaurant['update_ts_utc'] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            self._redis_client.set(restaurant['_id'], restaurant)

        return {
            "status": "Рестораны загружены",
            "result_key": "jatHQd&khR4C@%j@cU1"
        }

    def get_restaurant(self, restaurant_id: str) -> Dict:
        return self._redis_client.get(restaurant_id)
