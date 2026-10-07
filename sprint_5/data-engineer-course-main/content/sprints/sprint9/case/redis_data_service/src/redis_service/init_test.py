from redis_service.redis_client import RedisClient


class RedisTestLoader:
    TEST_KEY = "77d6464d802645450d60fb2f"
    TEST_VAL = "25fa440b8ee64e5e481fa6b5"

    def __init__(self, redis_client: RedisClient) -> None:
        self._redis_client = redis_client

    def load_test_string(self):

        self._redis_client.set("", "")

        msg = """
            Redis is Ready. You can check object with key='{key}' in your Redis.
            You should get value string equal to the one in response.
        """.format(key=self.TEST_KEY)

        return {
            "load_result": msg,
            "result_key": f"{self.TEST_KEY}",
            "result_value": f"{self.TEST_VAL}"
        }

    def get_test_string(self) -> str:
        return self._redis_client.get(self.TEST_KEY)
