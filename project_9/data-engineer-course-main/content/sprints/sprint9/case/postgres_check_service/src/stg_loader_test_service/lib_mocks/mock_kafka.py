from typing import Dict, Optional
from collections import deque
from lib.kafka_connect import KafkaConsumer, KafkaProducer


class MockKafkaProducer(KafkaProducer):
    def __init__(self) -> None:
        self.q = deque()

    def produce(self, payload: Dict) -> None:
        self.q.append(payload)


class MockKafkaConsumer(KafkaConsumer):
    def __init__(self) -> None:
        self.q = deque()
        self.consume_called = 0

    def add(self, obj: Dict) -> None:
        self.q.append(obj)

    def consume(self, timeout: float = 3.0) -> Optional[Dict]:
        self.consume_called += 1
        return self.q.popleft() if self.q else None
